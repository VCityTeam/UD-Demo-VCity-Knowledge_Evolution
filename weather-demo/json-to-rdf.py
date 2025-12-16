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
from rdflib import Graph, Namespace, Literal, URIRef, ConjunctiveGraph
from rdflib.namespace import RDF, XSD, GEO
from datetime import datetime


# Define namespaces
WEATHER = Namespace("http://example.org/weather/")
SCHEMA = Namespace("http://schema.org/")
WEATHER_GRAPH = Namespace("http://example.org/weather/graphs/")

# Configuration
DATA_DIR = "weather-demo/weather-data"
OUTPUT_EXTENSION = ".trig"


def json_to_rdf(json_file_path):
    """
    Transform a single JSON forecast file into RDF triples.
    
    Args:
        json_file_path: Path to the JSON file
        
    Returns:
        ConjunctiveGraph: RDF graph with named graphs (quads)
    """
    try:
        # Read JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create a ConjunctiveGraph (supports named graphs)
        cg = ConjunctiveGraph()
        
        # Bind namespaces for prettier output
        cg.bind("weather", WEATHER)
        cg.bind("geo", GEO)
        cg.bind("xsd", XSD)
        cg.bind("schema", SCHEMA)
        
        # Determine named graph URI
        source = data.get("source", "unknown")
        forecast_horizon = data.get("forecast_horizon_days", 0)
        graph_name = URIRef(WEATHER_GRAPH[f"{source}-D{forecast_horizon}"])
        
        # Get the named graph
        g = cg.get_context(graph_name)
        
        # Create subject URI based on fetch_datetime
        fetch_datetime_str = data.get("fetch_datetime", datetime.now().isoformat())
        subject = URIRef(WEATHER[f"forecast/{fetch_datetime_str}"])
        
        # Add type
        g.add((subject, RDF.type, WEATHER.WeatherForecast))
        
        # Add all properties from JSON
        
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
            g.add((subject, GEO.lat, 
                   Literal(data["latitude"], datatype=XSD.decimal)))
        
        # longitude (using standard geo vocabulary)
        if "longitude" in data:
            g.add((subject, GEO.long, 
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
        
        return cg
        
    except Exception as e:
        print(f"Error processing {json_file_path}: {e}")
        return None


def save_rdf_file(graph, json_file_path):
    """
    Save the RDF graph to a TriG file in the same directory as the JSON file.
    
    Args:
        graph: ConjunctiveGraph to save
        json_file_path: Original JSON file path (used to determine output location)
    """
    try:
        # Determine output file path
        json_path = Path(json_file_path)
        output_path = json_path.parent / (json_path.stem + OUTPUT_EXTENSION)
        
        # Serialize to TriG format
        graph.serialize(destination=str(output_path), format='trig', encoding='utf-8')
        
        print(f"  ✓ Created: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"Error saving RDF file: {e}")
        return None


def process_all_json_files(data_dir=DATA_DIR):
    """
    Recursively process all JSON files in the data directory.
    
    Args:
        data_dir: Root directory containing weather data
    """
    json_files = []
    
    # Find all JSON files
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return
    
    print(f"Found {len(json_files)} JSON file(s) to process\n")
    
    processed = 0
    failed = 0
    
    for json_file in json_files:
        print(f"Processing: {json_file}")
        
        # Transform JSON to RDF
        rdf_graph = json_to_rdf(json_file)
        
        if rdf_graph is not None:
            # Save RDF file
            output_file = save_rdf_file(rdf_graph, json_file)
            if output_file:
                processed += 1
            else:
                failed += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Transformation complete!")
    print(f"  Processed: {processed} file(s)")
    if failed > 0:
        print(f"  Failed: {failed} file(s)")
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
