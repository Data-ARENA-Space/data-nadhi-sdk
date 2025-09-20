"""JSON formatter for structured logging output.

This module provides a formatter that converts log records into JSON format,
making logs easily parseable by log aggregation and analysis tools. The formatter
includes additional fields like trace IDs and context data beyond standard log fields.

Example output:
    {
        "timestamp": "2025-09-20T08:15:30.123456Z",
        "module_name": "my_module",
        "function_name": "my_function",
        "line_number": 42,
        "level": "INFO",
        "message": "User logged in",
        "trace_id": "550e8400-e29b-41d4-a716-446655440000",
        "context": {
            "user_id": 123,
            "ip_address": "192.168.1.1"
        }
    }
"""

import datetime
import json
import logging


class JsonFormatter(logging.Formatter):
    """Format log records as JSON strings with standardized fields.

    This formatter extends the standard logging.Formatter to output records as
    JSON objects with consistent field names and formats. It includes support
    for additional fields like trace IDs and context data.

    The JSON output includes:
    - timestamp: ISO 8601 format with UTC timezone
    - module_name: Module where the log was created
    - function_name: Function that created the log
    - line_number: Line number in the source file
    - level: Log level (DEBUG, INFO, etc.)
    - message: The log message
    - trace_id: Unique ID for tracing request flow (optional)
    - context: Additional structured data about the log event (optional)
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string.

        Converts the log record into a structured dictionary and then
        serializes it to JSON. Handles missing optional fields (trace_id
        and context) gracefully.

        Args:
            record: The log record to format

        Returns:
            A JSON string containing all log record fields
        """
        timestamp = datetime.datetime.fromtimestamp(record.created).isoformat()
        entry = {
            "timestamp": f"{timestamp}Z",  # Add Z to indicate UTC
            "module_name": record.module,
            "function_name": record.funcName,
            "line_number": record.lineno,
            "level": record.levelname,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None),
            "context": getattr(record, "context", {}),
        }
        return json.dumps(entry)
