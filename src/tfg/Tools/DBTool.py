from influxdb_client import InfluxDBClient
import re
from pydantic import BaseModel
from langchain.tools.base import StructuredTool
from typing import Optional

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

# Define expected input schema for the tool using Pydantic
class InfluxDBQueryInput(BaseModel):
    """
    Defines the input parameters required for querying InfluxDB.

    Attributes:
        metric (str): Sensor metric to query (e.g., temperature, humidity).
        time_range (Optional[str]): Relative time range (e.g., '24h', '7d'). Ignored if start_time is provided.
        aggregation (str): Aggregation function to apply (e.g., 'mean', 'max').
        start_time (Optional[str]): Absolute start time in ISO 8601 format.
        end_time (Optional[str]): Absolute end time in ISO 8601 format.
    """
    metric: str
    aggregation: str
    time_range: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


# Function to construct Flux query dynamically
def construct_flux_query(params: dict) -> str:
    """
    Constructs a Flux query based on extracted parameters.

    Args:
        params (dict): Dictionary with keys 'metric', 'aggregation', and either 'time_range' or both 'start_time' and 'end_time'.

    Returns:
        str: A formatted Flux query string.

    Raises:
        ValueError: If metric or aggregation is invalid, or required time parameters are missing.
    """
    field = params.get("metric", "humidity")
    aggregation = params.get("aggregation", "mean")
    start_time = params.get("start_time")
    end_time = params.get("end_time")
    time_range = params.get("time_range", "24h")

    # Validate metric and aggregation
    if field not in VALID_METRICS:
        raise ValueError(f"❌ Invalid metric '{field}'. Available metrics: {', '.join(VALID_METRICS)}")
    if aggregation not in VALID_AGGREGATIONS:
        raise ValueError(f"❌ Invalid aggregation '{aggregation}'. Available functions: {', '.join(VALID_AGGREGATIONS)}")

    # Build time range
    if start_time and end_time:
        time_clause = f'range(start: time(v: "{start_time}"), stop: time(v: "{end_time}"))'
    elif time_range:
        time_clause = f'range(start: -{time_range})'
    else:
        raise ValueError("❌ You must provide either a relative time_range or both start_time and end_time.")

    # Construct query
    flux_query = f"""
    from(bucket: "{INFLUXDB_BUCKET}")
      |> {time_clause}
      |> filter(fn: (r) => r["_measurement"] == "sensor_data")
      |> filter(fn: (r) => r["_field"] == "{field}")
      |> aggregateWindow(every: 1h, fn: {aggregation}, createEmpty: false)
      |> yield(name: "result")
    """
    return flux_query

# Function that receives individual arguments (required by StructuredTool)
def query_influxdb(
    metric: str,
    aggregation: str,
    time_range: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> str:
    """
    Queries InfluxDB using structured parameters. Accepts both relative and absolute time formats.

    Args:
        metric (str): Metric name to query (e.g., "temperature").
        aggregation (str): Aggregation function (e.g., "mean", "max").
        time_range (str, optional): Relative time range (e.g., "24h", "7d"). Ignored if start_time and end_time are provided.
        start_time (str, optional): Absolute start time (e.g., "2024-11-01T00:00:00Z").
        end_time (str, optional): Absolute end time (e.g., "2024-11-10T23:59:59Z").

    Returns:
        str: Resulting observation string or error message.
    """
    params = {
        "metric": metric,
        "time_range": time_range,
        "aggregation": aggregation,
        "start_time": start_time,
        "end_time": end_time,
    }
    return _query_influxdb_internal(params)


# Internal function to perform the actual query logic
def _query_influxdb_internal(params: dict) -> str:
    """
    Constructs and executes a Flux query on InfluxDB from parameter dictionary.

    Args:
        params (dict): Dictionary containing 'metric', 'time_range', and 'aggregation'.

    Returns:
        str: Query results or an error message.
    """
    try:
        # Build the Flux query dynamically from parameters
        flux_query = construct_flux_query(params)

        print(f"📊 Extracted Parameters: {params}")
        print(f"🔥 Executing Flux Query:\n{flux_query}") 

        # Execute the query using InfluxDB client
        result = query_api.query(org=INFLUXDB_ORG, query=flux_query)
        results = []

        # Format the results
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
influx_tool = StructuredTool.from_function(
    name="InfluxDB Query Tool",
    description=(
        "Fetches sensor data from InfluxDB.\n"
        "- Required parameters: `metric` (e.g., 'temperature'), `aggregation` (e.g., 'mean').\n"
        "- Time range can be specified either as a relative `time_range` (e.g., '24h') or as absolute times with `start_time` and `end_time` "
        "(e.g., '2024-11-01T00:00:00Z')."
    ),
    func=query_influxdb,
    args_schema=InfluxDBQueryInput
)
