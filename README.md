# Data Nadhi SDK

A powerful Python logging SDK that provides structured logging with rule-based filtering and pipeline triggering capabilities. The name "Nadhi" comes from the Tamil word நதி (river), representing the flow of log data through your system.

## Features

- **Structured JSON Logging**: All logs are formatted as JSON for easy parsing and analysis
- **Rule-Based Filtering**: Define complex rules to filter and route your logs
- **Pipeline Triggering**: Trigger custom actions based on log content and rules
- **Trace ID Support**: Built-in support for distributed tracing
- **Contextual Logging**: Add rich context to your log entries
- **UTC Timestamps**: Consistent timestamp formatting in ISO 8601 format

## Installation

You can install the Data Nadhi SDK using pip:

### From PyPI (when available)
```bash
pip install data-nadhi-sdk
```

### Directly from GitHub
```bash
# Latest version from main branch
pip install git+https://github.com/Data-ARENA-Space/data-nadhi-sdk.git

# With development dependencies
pip install "git+https://github.com/Data-ARENA-Space/data-nadhi-sdk.git#egg=data-nadhi-sdk[dev]"

# Specific version/tag
pip install git+https://github.com/Data-ARENA-Space/data-nadhi-sdk.git@v1.0.0
```

## Quick Start

1. Create a configuration file `.datanadhi/config.yaml`:

```yaml
rules:
  - name: "error_alert"
    conditions:
      level: "ERROR"
    actions:
      - type: "notify"
        params:
          method: "email"
          recipients: ["alerts@example.com"]
```

2. Use the logger in your code:

```python
from datanadhi import DataNadhiLogger

# Initialize the logger
logger = DataNadhiLogger()

# Simple logging
logger.info("User logged in", context={"user_id": 123})

# Logging with trace ID
logger.error(
    "Database connection failed",
    trace_id="550e8400-e29b-41d4-a716-446655440000",
    context={
        "host": "db.example.com",
        "port": 5432
    }
)
```

## Log Output Format

Each log entry is formatted as a JSON object with the following fields:

```json
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
```

## Rule Configuration

Rules are defined in YAML format and consist of conditions and actions. When a log entry matches the conditions, the specified actions are triggered.

Example rule configuration:

```yaml
rules:
  - name: "high_latency_alert"
    conditions:
      level: "WARNING"
      context.latency:
        operator: "gt"
        value: 1000
    actions:
      - type: "notify"
        params:
          method: "slack"
          channel: "#performance-alerts"
```

## Advanced Usage

### Custom Formatters

You can create custom formatters by extending the `JsonFormatter` class:

```python
from datanadhi.formatters import JsonFormatter

class CustomFormatter(JsonFormatter):
    def format(self, record):
        entry = super().format(record)
        # Add custom formatting logic here
        return entry
```

### Pipeline Integration

The SDK supports pipeline triggering based on rule matches. When a log entry matches a rule's conditions, the specified pipelines are triggered asynchronously. Pipeline IDs are configured in the rules configuration file:

```yaml
rules:
  - name: "error_alert"
    conditions:
      level: "ERROR"
    pipelines:
      - "pipeline_error_001"  # Pipeline ID to trigger
      - "pipeline_error_002"  # Multiple pipelines can be triggered
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.