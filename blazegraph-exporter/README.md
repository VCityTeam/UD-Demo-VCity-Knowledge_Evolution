# Blazegraph Exporter

This is a Prometheus exporter for the Blazegraph triple store.

## Overview

The Blazegraph exporter is designed to expose metrics from a Blazegraph instance to Prometheus.
This allows for monitoring and alerting based on the performance and health of the Blazegraph database.

## Configuration

The exporter can be customized using the following environment variables:

- `BASE_URL`: The base URL of the Blazegraph instance to be monitored.
- `PORT_EXPORTER`: The port on which the exporter will run.

## Usage

To run the Blazegraph exporter, set the required environment variables and start the exporter:

```sh
export BASE_URL=http://your-blazegraph-instance-url
export PORT_EXPORTER=your-desired-port
docker run -d -p $PORT_EXPORTER:$PORT_EXPORTER -e "BASE_URL=$BASE_URL" -e "PORT_EXPORTER=$PORT_EXPORTER" blazegraph-exporter
```

Replace `http://your-blazegraph-instance-url` with the actual URL of your Blazegraph instance and `your-desired-port` with the port number you want the exporter to listen on.

## Metrics

The exporter will expose various metrics related to the Blazegraph instance, which can be scraped by Prometheus for monitoring and alerting purposes.

## License

See the [LICENSE](../LICENSE) file for license rights and limitations.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.
