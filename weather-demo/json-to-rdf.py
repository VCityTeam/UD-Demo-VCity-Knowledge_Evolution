#!/usr/bin/env python3
"""
Transform weather forecast JSON files into RDF knowledge graphs.

This script recursively scans the weather-data directory for JSON files
and transforms them into RDF using the TriG format (supporting named graphs/quads).
Each forecast is stored in a named graph based on the source and forecast horizon.
"""

import os
import json
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef, Dataset
from rdflib.namespace import RDF, XSD, WGS, PROV
from datetime import datetime


# Define namespaces
WEATHER = Namespace("http://example.org/weather/")
SCHEMA = Namespace("http://schema.org/")
WEATHER_GRAPH = Namespace("http://example.org/weather/graphs/")

# Configuration
DATA_DIR = "weather-data"
OUTPUT_EXTENSION = ".trig"


def json_to_rdf(json_file_path):
    """
    Transform a single JSON forecast file into RDF triples.
    
    Args:
        json_file_path: Path to the JSON file
        
    Returns:
        tuple: (weather_dataset, metadata_graph) - Weather dataset and metadata graph
    """
    try:
        # Read JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create a Dataset for weather data and a Graph for metadata
        weather_ds = Dataset()
        metadata_graph = Graph()
        
        # Bind namespaces for prettier output
        for ds in [weather_ds, metadata_graph]:
            ds.bind("weather", WEATHER)
            ds.bind("xsd", XSD)
            ds.bind("schema", SCHEMA)
            ds.bind("wgs", WGS)
            ds.bind("prov", PROV)
        
        # Determine named graph URI
        source = data.get("source", "unknown")
        forecast_horizon = data.get("forecast_horizon_days", 0)
        graph_name = URIRef(WEATHER_GRAPH[f"{source}-D{forecast_horizon}"])
        
        # Get the named graph for weather data
        g = weather_ds.graph(graph_name)
        
        # Create city URI as an object
        city_name = data.get("city", "unknown")
        # Sanitize city name for URI (replace spaces and commas)
        city_uri_part = city_name.replace(" ", "_").replace(",", "")
        city_uri = URIRef(WEATHER[f"city/{city_uri_part}"])
        
        # Add city type and properties
        g.add((city_uri, RDF.type, WEATHER.City))
        
        # city name as literal (for display purposes)
        if "city" in data:
            g.add((city_uri, SCHEMA.name, Literal(data["city"], datatype=XSD.string)))
        
        # latitude (using standard geo vocabulary)
        if "latitude" in data:
            g.add((city_uri, WGS.lat, 
                   Literal(data["latitude"], datatype=XSD.decimal)))
        
        # longitude (using standard geo vocabulary)
        if "longitude" in data:
            g.add((city_uri, WGS.long, 
                   Literal(data["longitude"], datatype=XSD.decimal)))
        
        # Create forecast URI as the main subject
        # Use target_datetime or current timestamp to create unique forecast identifier
        target_dt = data.get("target_datetime", "unknown")
        forecast_horizon = data.get("forecast_horizon_days", 0)
        forecast_id = f"{city_uri_part}_{target_dt}_D{forecast_horizon}"
        forecast_uri = URIRef(WEATHER[f"forecast/{forecast_id}"])
        
        # Add forecast type
        g.add((forecast_uri, RDF.type, WEATHER.Forecast))
        
        # Link forecast to city
        g.add((forecast_uri, WEATHER.hasCity, city_uri))
        
        # fetch_datetime (metadata)
        if "fetch_datetime" in data:
            metadata_graph.add((forecast_uri, PROV.generatedAtTime, 
                   Literal(data["fetch_datetime"], datatype=XSD.dateTime)))
        
        # target_datetime
        if "target_datetime" in data:
            g.add((forecast_uri, WEATHER.targetDateTime, 
                   Literal(data["target_datetime"], datatype=XSD.dateTime)))
        
        # forecast_horizon_days
        if "forecast_horizon_days" in data:
            g.add((forecast_uri, WEATHER.forecastHorizonDays, 
                   Literal(data["forecast_horizon_days"], datatype=XSD.integer)))
        
        # source - create URI for the data source (store in METADATA graph)
        if "source" in data:
            source_uri = URIRef(WEATHER[f"source/{data['source']}"])
            metadata_graph.add((source_uri, RDF.type, WEATHER.DataSource))
            g.add((forecast_uri, WEATHER.hasSource, source_uri))
        
        # temperature_celsius
        if "temperature_celsius" in data:
            g.add((forecast_uri, WEATHER.temperatureCelsius, 
                   Literal(data["temperature_celsius"], datatype=XSD.decimal)))
        
        # description (optional field)
        if "description" in data:
            g.add((forecast_uri, WEATHER.description, Literal(data["description"], datatype=XSD.string)))
        
        # fetch_date (metadata)
        if "fetch_date" in data:
            metadata_graph.add((forecast_uri, WEATHER.fetchDate, 
                   Literal(data["fetch_date"], datatype=XSD.date)))
        
        # target_date (optional)
        if "target_date" in data:
            g.add((forecast_uri, WEATHER.targetDate, 
                   Literal(data["target_date"], datatype=XSD.date)))
        
        return weather_ds, metadata_graph
        
    except Exception as e:
        print(f"Error processing {json_file_path}: {e}")
        return None, None


def save_daily_rdf_file(graph, day_path, date_str):
    """
    Save the consolidated weather RDF graph for a day to a TriG file.
    
    Args:
        graph: Dataset containing all weather forecasts for the day
        day_path: Path to the day directory
        date_str: Date string (YYYY-MM-DD) for naming the file
    """
    try:
        # Determine output file path - save in the day directory
        output_path = Path(day_path) / f"{date_str}{OUTPUT_EXTENSION}"
        
        # Serialize to TriG format
        graph.serialize(destination=str(output_path), format='trig', encoding='utf-8')
        
        print(f"  ✓ Created weather KG: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"Error saving weather RDF file: {e}")
        return None


def save_metadata_file(metadata_graph, day_path):
    """
    Save the metadata graph to a metadata.ttl file.
    
    Args:
        metadata_graph: Graph containing all metadata
        day_path: Path to the day directory
    """
    try:
        # Determine output file path - save in the day directory
        output_path = Path(day_path) / "metadata.ttl"
        
        # Serialize to Turtle format
        metadata_graph.serialize(destination=str(output_path), format='turtle', encoding='utf-8')
        
        print(f"  ✓ Created metadata: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"Error saving metadata file: {e}")
        return None


def process_all_json_files(data_dir=DATA_DIR):
    """
    Process JSON files for the current day only.
    Creates one .trig file containing all forecasts for today.
    
    Args:
        data_dir: Root directory containing weather data
    """
    # Get current date
    today = datetime.now()
    current_year = str(today.year)
    current_month = str(today.month).zfill(2)
    current_day = str(today.day).zfill(2)
    date_str = f"{current_year}-{current_month}-{current_day}"
    
    # Construct path to today's directory
    day_path = os.path.join(data_dir, current_year, current_month, current_day)
    
    # Check if today's directory exists
    if not os.path.exists(day_path):
        print(f"No data directory found for today ({date_str})")
        return
    
    # Find all JSON files in today's directory
    json_files = []
    for root, dirs, files in os.walk(day_path):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    
    if not json_files:
        print(f"No JSON files found for today ({date_str})")
        return
    
    print(f"Found {len(json_files)} JSON file(s) for {date_str}\n")
    print(f"Processing day: {date_str} ({len(json_files)} forecast(s))")
    
    # Create a Dataset for weather data and a Graph for metadata
    combined_weather_graph = Dataset()
    combined_metadata_graph = Graph()
    
    # Bind namespaces for prettier output
    for ds in [combined_weather_graph, combined_metadata_graph]:
        ds.bind("weather", WEATHER)
        ds.bind("xsd", XSD)
        ds.bind("schema", SCHEMA)
        ds.bind("wgs", WGS)
        ds.bind("prov", PROV)
    
    total_processed = 0
    total_failed = 0
    
    # Process each JSON file for today
    for json_file in json_files:
        print(f"  - {json_file}")
        
        # Transform JSON to RDF (returns both weather and metadata datasets)
        weather_graph, metadata_graph = json_to_rdf(json_file)
        
        if weather_graph is not None and metadata_graph is not None:
            # Merge weather data into the combined weather graph
            for s, p, o, g in weather_graph.quads():
                combined_weather_graph.add((s, p, o, g))
            
            # Merge metadata into the combined metadata graph (triples only)
            for s, p, o in metadata_graph:
                combined_metadata_graph.add((s, p, o))
            
            total_processed += 1
        else:
            total_failed += 1
    
    # Save both graphs for today
    if total_processed > 0:
        weather_output = save_daily_rdf_file(combined_weather_graph, day_path, date_str)
        metadata_output = save_metadata_file(combined_metadata_graph, day_path)
        success = weather_output is not None and metadata_output is not None
    else:
        success = False
    
    print()
    print(f"{'='*60}")
    print(f"Transformation complete!")
    print(f"  Date: {date_str}")
    print(f"  Forecasts processed: {total_processed}")
    if total_failed > 0:
        print(f"  Failed forecasts: {total_failed}")
    if not success:
        print(f"  ERROR: Failed to save output file")
    print(f"{'='*60}")


def main():
    """Main entry point."""
    print("="*60)
    print("Weather Forecast JSON to RDF Transformer")
    print("="*60)
    print()
    
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"Error: Data directory '{DATA_DIR}' not found!")
        return
    
    # Process all JSON files
    process_all_json_files(DATA_DIR)


if __name__ == "__main__":
    main()
