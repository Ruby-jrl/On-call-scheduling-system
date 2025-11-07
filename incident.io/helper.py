from datetime import datetime, timezone
import json

# Define ISO8601 format
ISO_FMT = "%Y-%m-%dT%H:%M:%SZ"

def parse_time(s: str) -> datetime:
    """Parse an ISO8601 string into a datetime in UTC."""
    return datetime.strptime(s, ISO_FMT).replace(tzinfo=timezone.utc)

def fmt_time(dt: datetime) -> str:
    """Format a datetime as an ISO8601 string in UTC."""
    return dt.strftime(ISO_FMT)

def load_json(path: str) -> dict:
    """Load a JSON file from the given path string."""
    with open(path) as f:
        return json.load(f)