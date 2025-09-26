# Data Nadhi SDK

A powerful Python logging SDK that provides structured logging with rule-based filtering and pipeline triggering capabilities. The name "Nadhi" comes from the Tamil word நதி (river), representing the flow of log data through your system.

---

## Features

- **Structured JSON Logging**: All logs are formatted as JSON for easy parsing and analysis.
- **Rule-Based Filtering**: Define complex rules in YAML to filter and route your logs.
- **Pipeline Triggering**: Trigger external pipelines (e.g., via HTTP) based on rule matches.
- **Trace ID Support**: Built-in support for distributed tracing.
- **Contextual Logging**: Add rich context to your log entries.
- **UTC Timestamps**: Consistent timestamp formatting in ISO 8601 format.
- **Configurable via YAML**: Supports loading and merging multiple config files.
- **Environment Variable Support**: API keys and server host are configurable via environment variables.
- **Error Handling**: SDK logs its own errors if enabled.

---

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
pip install git+https://github.com/Data-ARENA-Space/data-nadhi-sdk.git@v0.1.0
```

---

## Quick Start

1. **Create a configuration file** (e.g., `.datanadhi/config.yaml`):

```yaml
rules:
  - name: "error_alert"
    any_condition_match: false
    conditions:
      - key: "level"
        type: "exact"
        value: "ERROR"
    pipelines:
      - "pipeline_error_001"
    stdout: true
```

2. **Set environment variables** (recommended in `.env`):

```env
NADHI_API_KEY=your_api_key_here
NADHI_SERVER_HOST=nadhi-server  # or the Docker container name of your server
```

3. **Use the logger in your code:**

```python
from dotenv import load_dotenv
from datanadhi import DataNadhiLogger

load_dotenv()  # Loads environment variables from .env

logger = DataNadhiLogger(module_name="my_app")

logger.info("User logged in", context={"user_id": 123})

logger.error(
    "Database connection failed",
    trace_id="550e8400-e29b-41d4-a716-446655440000",
    context={"host": "db.example.com", "port": 5432}
)
```

---

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

---

## Rule Configuration

Rules are defined in YAML format and consist of:
- `name`: Rule name.
- `any_condition_match`: If true, any condition match triggers the rule; if false, all must match.
- `conditions`: List of conditions (each with `key`, `type` (`exact`, `partial`, `regex`), and `value`).
- `pipelines`: List of pipeline IDs to trigger if the rule matches.
- `stdout`: If true, log is printed to stdout.

**Example:**
```yaml
rules:
  - name: "signup_rule"
    any_condition_match: false
    conditions:
      - key: "context.user.action"
        type: "exact"
        value: "signup"
      - key: "context.user.email"
        type: "regex"
        value: ".*@example.com"
    pipelines:
      - "pipeline_signup_001"
      - "pipeline_signup_002"
    stdout: true
```

---

## Pipeline Triggering

When a rule matches and specifies pipelines, the SDK will:
- Trigger each pipeline asynchronously (in a background thread).
- Send a POST request to the nadhi-server (or configured host) at `/api/pipeline/trigger` with:
    - `pipeline_id`
    - `log_data` (the log payload)

**Example request:**
```http
POST http://nadhi-server:5000/api/pipeline/trigger
Headers:
    x-api-key: <your-api-key>
    Content-Type: application/json
Body:
{
    "pipeline_id": "pipeline_signup_001",
    "log_data": { ... }
}
```

**Server host and API key are read from environment variables:**
- `DATA_NADHI_API_KEY` (required)
- `DATA_NADHI_SERVER_HOST` (defaults to `nadhi-server` for Docker network)

---

## Environment Variables

- `DATA_NADHI_API_KEY`: **Required**. API key for authenticating with the nadhi-server.
- `DATA_NADHI_SERVER_HOST`: Hostname of the nadhi-server (default: `nadhi-server`).
- `DATA_NADHI_CONFIG_DIR`: (Optional) Directory containing YAML config files. All `.yml` and `.yaml` files will be loaded and merged.

---

## Advanced Usage

### Multiple Config Files

You can place multiple `.yml` or `.yaml` files in your config directory (default: `.datanadhi/`).  
The SDK will load and merge all rules from these files.

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

---

## Error Handling

- If pipeline triggering fails, the SDK logs the error using the configured logger, including exception info.
- If the API key is missing, a clear error is raised.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## Support

For support, please open an issue on the GitHub repository or contact the maintainers.