import requests
from bs4 import BeautifulSoup
from prometheus_client import start_http_server, Summary
import time
import os

class blazegraph_exporter:
    """
    Blazegraph exporter for Prometheus
    """

    def __init__(self, url, port):
        """
        Initialize the exporter
        :param url: The base URL of the Blazegraph server
        :param port: The port to expose the metrics
        """
        self.base_url = url
        self.metrics_url = f"{self.base_url}/blazegraph/counters"
        self.server, self.t = start_http_server(port)
        print(f"Server started on port {port}")
        self.metrics = {}

        self.init_metrics()

    def fetch_and_get_rows(self):
        """
        Fetch the metrics page and return the rows of the table
        :return: The rows of the table
        """
        headers = {"Accept": "text/html"}  # Explicitly request HTML format if necessary

        # Fetching the HTML content
        response = requests.get(self.metrics_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            return {}
        
        # Parsing HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')

        # Iterating over rows in the table
        return table.find_all('tr')[2:]  # Skip the first two header rows

    def get_metric_key(self, name):
        """
        Convert the metric name to a valid Prometheus metric key
        :param name: The metric name
        :return: The metric key
        """
        return name.replace("/", " ") \
            .strip() \
            .replace(".", "_") \
            .replace("/", "_") \
            .replace(" ", "_") \
            .replace("%", "percentage_") \
            .replace("#", "number_") \
            .lower()

    def init_metrics(self):
        """
        Initialize the metrics
        """
        for row in self.fetch_and_get_rows():
            cols = row.find_all(['th', 'td'])
            
            # Extracting metric name and values
            if cols[0].a:
                initial_key = cols[0].get_text(strip=True)
                name = self.get_metric_key(cols[0].get_text(strip=True))

                # check if value is a number in all formats
                try:
                    float(cols[1].get_text(strip=True).replace(",", ""))
                    self.metrics[name] = Summary(name, f"Summary for {initial_key}")
                except ValueError:
                    pass

    def fetch_and_parse_metrics(self):
        """
        Fetch and parse the metrics
        """
        for row in self.fetch_and_get_rows():
            cols = row.find_all(['th', 'td'])
            
            # Extracting metric name and values
            if cols[0].a:
                name = self.get_metric_key(cols[0].get_text(strip=True))

                # check if value is a number in all formats
                try:
                    value = float(cols[1].get_text(strip=True).replace(",", ""))
                    self.metrics[name].observe(value)
                except ValueError:
                    pass

if __name__ == "__main__":
    # use $BASE_URL environment variable to define the base url
    base_url = os.getenv("BASE_URL", "http://localhost:9999")
    port_exporter = os.getenv("PORT_EXPORTER", 9400)
    bg_exporter = blazegraph_exporter(base_url, port_exporter)

    while True:
        time.sleep(5.0)
        bg_exporter.fetch_and_parse_metrics()
