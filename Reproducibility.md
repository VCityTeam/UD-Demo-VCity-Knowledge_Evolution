# Reproducibility Guide for ConVer-G

This document provides step-by-step instructions to reproduce a weather forecasting experiment.

## Overview

This experiment demonstrates the data acquisition, transformation, and ingestion pipeline.
It uses the `Quads-loaDer` for versioned storage, `Quads-Query` for retrieval, and `Quads-Visualizer` for visualization.

The demo use case is the following:

- The system downloads the weather forecasting of the 3 next days for two forecasting sources.
- Each day, it downloads the real weather forecast of the current day.
- The system creates a knowledge graph containing the previous forecasting and the real weather and uploads it to ConVer-G.
- The system permits navigating between all versioned graphs and comparing which source is the most accurate using SPARQL queries.

## Prerequisites

To reproduce this experiment locally, you need **Docker & Docker Compose** to run the ConVer-G services (PostgreSQL, Quads-loaDer, Quads-Query, Quads-Visualizer, Quads-Creator).

## 1. Infrastructure Setup

File: [docker-compose.yml](https://github.com/VCityTeam/UD-Demo-VCity-Knowledge_Evolution/tree/JOSS-ConVer-G-2/docker/docker-compose.yml).
Download the file and place it in a working directory.
First, initialize the backend services defined in the `docker-compose.yml` file. This corresponds to the persistent storage layer of the ConVer-G architecture.

```bash
docker-compose up -d
```

## 2. Experiment Execution

At this point, the backend services are running and ready to accept requests.
To create our dataset, we will use the `Quads-Creator` container.
Every day, fetch the weather forecast for the next 3 days (just once per day will be necessary).

```bash
#!/bin/bash
curl http://localhost:5000/get-forecasts
```

This will create a dataset containing the weather forecasts for the next 3 days.

## 3. Visualize the Results

Once your weather data is ingested (via the `curl http://localhost:5000/get-forecasts` command), you can explore it through the web-based visualization at **`http://localhost:80`**.

### Step 1: Access the Metagraph View
This allows you to see the complete snapshots of your weather dataset over time.

### Step 2: Navigate Versions via Clustering
Use the clustering feature to organize nodes by:
- **`prov:specializationOf`**: Groups all snapshots of the same named graph (e.g., all MeteoFrance forecasts together)
- **`prov:atLocation`**: Groups all named graphs captured within the same snapshot (e.g., all forecasts from the same day)

This lets you navigate either by **structure** (how a single forecast source evolves) or by **time** (the complete dataset state on a specific day).

### Step 3: Select a Versioned Graph
Select the "Change versioned graph" option and click on any node in the metagraph to load its content in the right panel—the **Versioned Graph**. This displays the actual RDF quads (weather data triples) present in that snapshot.

### Step 4: Analyze Differences with Delta Visualization
Use the **Change versioned graph** feature to compare two versions:
1. Select a base version
2. Hover a target version to compare against
3. The tool computes and displays the **delta** (additions in green, deletions in red, unchanged in gray).

This is particularly useful for seeing how weather forecasts evolved or comparing prediction accuracy between sources.

### Step 5: Use Focus Mode
If the visualization is cluttered with metadata, toggle **Focus mode** to hide all non-PROV-O triples, letting you concentrate on the actual weather data and its provenance.

### Step 6: Merged Graphs Option
Enable **Merged graphs** to view all versioned graphs combined into a single unified view. Use the search bar to filter nodes by label when navigating large datasets with many forecast versions.

## 4. Querying the Results

To query the versioned weather dataset, open the [**Quads-Query**](http://localhost:8081) web interface in your browser.
The interface provides a [Yasgui-based SPARQL editor](https://docs.triply.cc/yasgui/) provided by [Apache Fuseki](https://jena.apache.org/documentation/fuseki2/) where you can write and execute queries against the versioned knowledge graph.

To run a query:

1. Open the Quads-Query UI at `http://localhost:8081` or use the embedded SPARQL endpoint in your application by selecting **SPARQL Query** in the Quads-Visualizer interface.
2. Copy the content of one of the example query files into the SPARQL editor.
3. Click the **Execute** button to run the query and view the results.

The following example queries are available in the [Queries example](https://github.com/VCityTeam/UD-Demo-VCity-Knowledge_Evolution/tree/JOSS-ConVer-G-2/weather-demo/queries-example) folder:

- [max-by-target-horizon.rq](https://github.com/VCityTeam/UD-Demo-VCity-Knowledge_Evolution/blob/JOSS-ConVer-G-2/weather-demo/queries-example/max-by-target-horizon.rq) computes the maximum temperature for each day and horizon.
- [max-meteofrance.rq](https://github.com/VCityTeam/UD-Demo-VCity-Knowledge_Evolution/blob/JOSS-ConVer-G-2/weather-demo/queries-example/max-meteofrance.rq) computes the maximum temperature for the MeteoFrance source.
- [most-accurate-source.rq](https://github.com/VCityTeam/UD-Demo-VCity-Knowledge_Evolution/blob/JOSS-ConVer-G-2/weather-demo/queries-example/most-accurate-source.rq) computes the most accurate source for each horizon.
