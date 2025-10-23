# Data Nadhi SDK

Python logging SDK with rule-based filtering and automatic pipeline triggering.

## Description

This SDK provides structured JSON logging with trace ID support, rule-based log filtering, and automatic triggering of data pipelines based on log content. Logs can be filtered using exact match, partial match, or regex patterns.

## Dev Container

This repository includes a dev container configuration with all required dependencies pre-configured.

**To use:**
1. Open the repository in VS Code
2. Click "Reopen in Container" when prompted
3. Python 3.11+ and all dependencies will be available

## Usage

```python
from datanadhi import DataNadhiLogger

logger = DataNadhiLogger(module_name="my_app")
logger.info("User login", context={"user": {"id": 123}})
```

## Environment Variables

```env
DATA_NADHI_API_KEY=your-api-key
DATA_NADHI_STACKLEVEL=2
DATA_NADHI_SKIP_STACK=4
```

## License

This project is licensed under the ISC License - see the [LICENSE](LICENSE) file for details.
