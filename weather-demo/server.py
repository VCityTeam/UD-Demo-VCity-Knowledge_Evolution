#!/usr/bin/env python3
"""
Weather Demo Flask Server.

This server provides an HTTP endpoint to trigger the weather forecast pipeline:
1. Fetch weather forecasts from multiple sources
2. Transform JSON data to RDF knowledge graphs
3. Upload the TriG files to a quads-loader service

Usage:
    python server.py

Endpoints:
    GET /health - Health check
    POST /run-pipeline - Execute the full weather pipeline
    GET /run-pipeline - Execute the full weather pipeline (for convenience)
"""

import os
import sys
import traceback
from datetime import datetime

from flask import Flask, jsonify

# Import pipeline functions from existing modules
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


def run_fetch_forecast():
    """Execute the fetch-forecast pipeline step."""
    # Import here to avoid circular imports and ensure fresh execution
    import importlib
    
    # Import and reload to get fresh state
    import fetch_forecast
    importlib.reload(fetch_forecast)
    
    city = fetch_forecast.CITY
    owm_api_key = fetch_forecast.OWM_API_KEY
    
    results = {
        "open_meteo": None,
        "openweathermap": None,
        "meteofrance": None
    }
    
    try:
        fetch_forecast.get_forecast_open_meteo(city)
        results["open_meteo"] = "success"
    except Exception as e:
        results["open_meteo"] = f"error: {str(e)}"
    
    try:
        fetch_forecast.get_forecast_openweathermap(city, owm_api_key)
        results["openweathermap"] = "success"
    except Exception as e:
        results["openweathermap"] = f"error: {str(e)}"
    
    try:
        fetch_forecast.get_observation_meteofrance(city)
        results["meteofrance"] = "success"
    except Exception as e:
        results["meteofrance"] = f"error: {str(e)}"
    
    return results


def run_json_to_rdf():
    """Execute the json-to-rdf pipeline step."""
    import importlib
    
    import json_to_rdf
    importlib.reload(json_to_rdf)
    
    try:
        json_to_rdf.main()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def run_upload_trig():
    """Execute the upload-trig pipeline step."""
    import importlib
    
    import upload_trig
    importlib.reload(upload_trig)
    
    try:
        upload_trig.upload_trig_file()
        return {"status": "success"}
    except SystemExit as e:
        # upload_trig uses sys.exit on errors
        return {"status": "error", "message": f"Upload failed with exit code {e.code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "weather-demo"
    })


@app.route('/get-forecasts', methods=['GET', 'POST'])
def get_forecasts():
    """
    Execute the full weather pipeline.
    
    This is equivalent to running:
        python fetch-forecast.py && python json-to-rdf.py && python upload-trig.py
    """
    start_time = datetime.now()
    results = {
        "pipeline_start": start_time.isoformat(),
        "steps": {}
    }
    
    # Step 1: Fetch forecasts
    print("=" * 60)
    print("Step 1: Fetching weather forecasts...")
    print("=" * 60)
    try:
        fetch_result = run_fetch_forecast()
        results["steps"]["fetch_forecast"] = {
            "status": "completed",
            "details": fetch_result
        }
    except Exception as e:
        results["steps"]["fetch_forecast"] = {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        results["pipeline_end"] = datetime.now().isoformat()
        results["success"] = False
        return jsonify(results), 500
    
    # Step 2: Transform JSON to RDF
    print()
    print("=" * 60)
    print("Step 2: Transforming JSON to RDF...")
    print("=" * 60)
    try:
        rdf_result = run_json_to_rdf()
        results["steps"]["json_to_rdf"] = rdf_result
        if rdf_result.get("status") == "error":
            results["pipeline_end"] = datetime.now().isoformat()
            results["success"] = False
            return jsonify(results), 500
    except Exception as e:
        results["steps"]["json_to_rdf"] = {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        results["pipeline_end"] = datetime.now().isoformat()
        results["success"] = False
        return jsonify(results), 500
    
    # Step 3: Upload TriG files
    print()
    print("=" * 60)
    print("Step 3: Uploading TriG files...")
    print("=" * 60)
    try:
        upload_result = run_upload_trig()
        results["steps"]["upload_trig"] = upload_result
        if upload_result.get("status") == "error":
            results["pipeline_end"] = datetime.now().isoformat()
            results["success"] = False
            return jsonify(results), 500
    except Exception as e:
        results["steps"]["upload_trig"] = {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        results["pipeline_end"] = datetime.now().isoformat()
        results["success"] = False
        return jsonify(results), 500
    
    # Success
    end_time = datetime.now()
    results["pipeline_end"] = end_time.isoformat()
    results["duration_seconds"] = (end_time - start_time).total_seconds()
    results["success"] = True
    
    print()
    print("=" * 60)
    print(f"Pipeline completed successfully in {results['duration_seconds']:.2f}s")
    print("=" * 60)
    
    return jsonify(results)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"Starting Weather Demo Server on port {port}...")
    print(f"Endpoints:")
    print(f"  - GET  /health        - Health check")
    print(f"  - GET  /run-pipeline  - Execute weather pipeline")
    print(f"  - POST /run-pipeline  - Execute weather pipeline")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
