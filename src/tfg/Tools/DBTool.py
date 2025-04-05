from influxdb_client import InfluxDBClient
from langchain.tools import Tool
import re

# Client configuration
INFLUXDB_URL = "https://apiivm78.etsii.upm.es:8086"
INFLUXDB_TOKEN = "bYNCMsvuiCEoJfPFL5gPgWgDISh79wO4dH9dF_y6cvOKp6uWTRZHtPIwEbRVb2gfFqo3AdygZCQIdbAGBfd31Q=="
INFLUXDB_ORG = "UPM"
INFLUXDB_BUCKET = "LoraWAN"

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()

# Supported parameters
VALID_METRICS = {"temperature", "humidity", "light", "motion", "vdd"}
VALID_AGGREGATIONS = {"mean", "max", "min", "sum"}

# Function to construct Flux query dynamically
def construct_flux_query(params: dict) -> str:
    """
    Constructs a Flux query based on extracted parameters.
    
    Args:
        params (dict): A dictionary containing 'metric', 'time_range', and 'aggregation'.
    
    Returns:
        str: A formatted Flux query.
    """
    measurement = "sensor_data"  # Default measurement
    field = params.get("metric", "humidity")  # Default metric
    time_range = params.get("time_range", "24h")  # Default to 24h if missing
    aggregation = params.get("aggregation", "mean")  # Default to mean

    # Validate metric
    if field not in VALID_METRICS:
        raise ValueError(f"❌ Invalid metric '{field}'. Available metrics: {', '.join(VALID_METRICS)}")

    # Validate aggregation function
    if aggregation not in VALID_AGGREGATIONS:
        raise ValueError(f"❌ Invalid aggregation '{aggregation}'. Available functions: {', '.join(VALID_AGGREGATIONS)}")

    # Construct Flux query
    flux_query = f"""
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -{time_range})
      |> filter(fn: (r) => r["_measurement"] == "{measurement}")
      |> filter(fn: (r) => r["_field"] == "{field}")
      |> aggregateWindow(every: 1h, fn: {aggregation}, createEmpty: false)
      |> yield(name: "result")
    """
    return flux_query

# Function to execute a Flux query
def query_influxdb(params: dict) -> str:
    """
    Constructs and executes a Flux query on InfluxDB.
    
    Args:
        params (dict): Dictionary containing query parameters (metric, time_range, aggregation).
    
    Returns:
        str: Query results or an error message.
    """
    try:
        flux_query = construct_flux_query(params)

        print(f"📊 Extracted Parameters: {params}")
        print(f"🔥 Executing Flux Query:\n{flux_query}") 

        result = query_api.query(org=INFLUXDB_ORG, query=flux_query)
        results = []

        for table in result:
            for record in table.records:
                results.append(f"Time: {record.get_time()}, Value: {record.get_value()}")

        return "\n".join(results) if results else "⚠️ No data found in the database. Verify if data exists for this time range."
    
    except ValueError as ve:
        return str(ve)  # Return validation error messages

    except Exception as e:
        return f"❌ Error querying InfluxDB: {str(e)}"

# Function to extract the time range from a query
def extract_time_range(user_query: str) -> str:
    """
    Extracts the time range from a user query.

    Args:
        user_query (str): The input query from the user.

    Returns:
        str: A formatted time range for InfluxDB (e.g., "24h", "7d", "30d").
    """
    time_patterns = {
        r"(\d+)\s*(minute|minutes|min)": "m",
        r"(\d+)\s*(hour|hours|h)": "h",
        r"(\d+)\s*(day|days|d)": "d",
        r"(\d+)\s*(week|weeks|w)": "w",
        r"(\d+)\s*(month|months|mo)": "d",  # Approximate: 1 month = 30 days
        r"(\d+)\s*(year|years|y)": "d"  # Approximate: 1 year = 365 days
    }

    detected_range = "24h"  # Default if no time range is found

    for pattern, unit in time_patterns.items():
        match = re.search(pattern, user_query, re.IGNORECASE)
        if match:
            value = int(match.group(1))  # Extract numeric value
            if "month" in pattern:
                value *= 30  # Convert months to days
            elif "year" in pattern:
                value *= 365  # Convert years to days
            detected_range = f"{value}{unit}"
            break

    return detected_range

# LangChain compatible tool
influx_tool = Tool(
    name="InfluxDB Query Tool",
    func=query_influxdb,
    description="Fetches sensor data from InfluxDB. Requires parameters like metric (e.g., humidity, temperature), time_range (e.g., 24h), and aggregation (e.g., mean)."
)