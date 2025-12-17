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
from rdflib.namespace import RDF, XSD, WGS
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
        Dataset: RDF graph with named graphs (quads)
    """
    try:
        # Read JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create a Dataset (supports named graphs)
        ds = Dataset()
        
        # Bind namespaces for prettier output
        ds.bind("weather", WEATHER)
        ds.bind("xsd", XSD)
        ds.bind("schema", SCHEMA)
        ds.bind("wgs", WGS)
        
        # Determine named graph URI
        source = data.get("source", "unknown")
        forecast_horizon = data.get("forecast_horizon_days", 0)
        graph_name = URIRef(WEATHER_GRAPH[f"{source}-D{forecast_horizon}"])
        
        # Get the named graph
        g = ds.graph(graph_name) # Use .graph() for Dataset
        
        # Create subject URI based on city name
        city_name = data.get("city", "unknown")
        # Sanitize city name for URI (replace spaces and commas)
        city_uri_part = city_name.replace(" ", "_").replace(",", "")
        subject = URIRef(WEATHER[f"city/{city_uri_part}"])
        
        # Add type
        g.add((subject, RDF.type, WEATHER.City))
        
        # Add all properties from JSON as objects
        
        # fetch_datetime
        if "fetch_datetime" in data:
            g.add((subject, WEATHER.fetchDateTime, 
                   Literal(data["fetch_datetime"], datatype=XSD.dateTime)))
        
        # target_datetime
        if "target_datetime" in data:
            g.add((subject, WEATHER.targetDateTime, 
                   Literal(data["target_datetime"], datatype=XSD.dateTime)))
        
        # forecast_horizon_days
        if "forecast_horizon_days" in data:
            g.add((subject, WEATHER.forecastHorizonDays, 
                   Literal(data["forecast_horizon_days"], datatype=XSD.integer)))
        
        # source
        if "source" in data:
            g.add((subject, WEATHER.source, Literal(data["source"])))
        
        # city
        if "city" in data:
            g.add((subject, WEATHER.city, Literal(data["city"])))
        
        # latitude (using standard geo vocabulary)
        if "latitude" in data:
            g.add((subject, WGS.lat, 
                   Literal(data["latitude"], datatype=XSD.decimal)))
        
        # longitude (using standard geo vocabulary)
        if "longitude" in data:
            g.add((subject, WGS.long, 
                   Literal(data["longitude"], datatype=XSD.decimal)))
        
        # temperature_celsius
        if "temperature_celsius" in data:
            g.add((subject, WEATHER.temperatureCelsius, 
                   Literal(data["temperature_celsius"], datatype=XSD.decimal)))
        
        # description (optional field)
        if "description" in data:
            g.add((subject, WEATHER.description, Literal(data["description"])))
        
        # fetch_date (optional)
        if "fetch_date" in data:
            g.add((subject, WEATHER.fetchDate, 
                   Literal(data["fetch_date"], datatype=XSD.date)))
        
        # target_date (optional)
        if "target_date" in data:
            g.add((subject, WEATHER.targetDate, 
                   Literal(data["target_date"], datatype=XSD.date)))
        
        return ds
        
    except Exception as e:
        print(f"Error processing {json_file_path}: {e}")
        return None


def save_daily_rdf_file(graph, day_path, date_str):
    """
    Save the consolidated RDF graph for a day to a TriG file.
    
    Args:
        graph: Dataset containing all forecasts for the day
        day_path: Path to the day directory
        date_str: Date string (YYYY-MM-DD) for naming the file
    """
    try:
        # Determine output file path - save in the day directory
        output_path = Path(day_path) / f"{date_str}{OUTPUT_EXTENSION}"
        
        # Serialize to TriG format
        graph.serialize(destination=str(output_path), format='trig', encoding='utf-8')
        
        print(f"  ✓ Created: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"Error saving RDF file: {e}")
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
    
    # Create a combined Dataset for all forecasts of this day
    combined_graph = Dataset()
    
    # Bind namespaces for prettier output
    combined_graph.bind("weather", WEATHER)
    combined_graph.bind("xsd", XSD)
    combined_graph.bind("schema", SCHEMA)
    
    total_processed = 0
    total_failed = 0
    
    # Process each JSON file for today
    for json_file in json_files:
        print(f"  - {json_file}")
        
        # Transform JSON to RDF
        rdf_graph = json_to_rdf(json_file)
        
        if rdf_graph is not None:
            # Merge this graph into the combined graph
            # Iterate over quads (s, p, o, g) and add to the combined Dataset
            for s, p, o, g in rdf_graph.quads():
                combined_graph.add((s, p, o, g))
            total_processed += 1
        else:
            total_failed += 1
    
    # Save the combined graph for today
    if total_processed > 0:
        output_file = save_daily_rdf_file(combined_graph, day_path, date_str)
        success = output_file is not None
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
