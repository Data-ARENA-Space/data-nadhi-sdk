"""Advanced logging system with rule-based filtering and pipeline triggers.

This module implements the core DataNadhiLogger class, which provides:
- Rule-based log filtering using exact, partial, and regex matches
- Automated pipeline triggering based on log content
- JSON formatting with context and trace ID support
- Thread-safe trace ID propagation using contextvars
- Configurable stdout output based on rules

Example:
    ```python
    from datanadhi import DataNadhiLogger

    # Initialize with module name and optional API key
    logger = DataNadhiLogger(module_name="my_app")

    # Log with context data that can trigger rules
    logger.info("User login", context={
        "user": {"id": 123, "action": "login"}
    })
    ```

Environment Variables:
    DATA_NADHI_API_KEY: API key for authentication
    DATA_NADHI_STACKLEVEL: Stack level for logging (default: 2)
    DATA_NADHI_SKIP_STACK: Stack frames to skip for caller info (default: 4)
"""

import contextvars
import datetime
import logging
import os
import sys
import threading
import uuid

from .formatters.json_default_formatter import JsonFormatter
from .utils.config import get_api_key, load_config
from .utils.datatypes import RuleEvaluationResult
from .utils.rule_engine import evaluate_rules

# Thread-safe trace ID storage
trace_id_var = contextvars.ContextVar("trace_id", default=None)


class DataNadhiLogger:
    """Advanced logger with rule-based filtering and pipeline triggers.

    This class extends Python's logging functionality with:
    - Rule-based filtering of log messages
    - Automatic pipeline triggering based on log content
    - Structured logging with JSON formatting
    - Context and trace ID support for distributed tracing
    - Configurable stack trace handling

    Args:
        module_name: Name to identify this logger instance
        api_key: Data Nadhi API key for authentication
        log_formatter: Custom formatter, defaults to JsonFormatter
        config_path: Path to rule configuration file
        log_level: Minimum log level to process
        stacklevel: Override default stack level for logging
        skip_stack: Override default stack frames to skip for caller info
    """

    def __init__(
        self,
        module_name: str | None = None,
        *,
        api_key: str | None = None,
        log_formatter: logging.Formatter | None = None,
        config_path: str | None = None,
        log_level: int = logging.DEBUG,
        stacklevel: int | None = None,
        skip_stack: int | None = None,
    ) -> None:
        # Initialize core attributes
        self.module_name = module_name or "datanadhi_module"
        self.api_key = get_api_key(api_key)
        self.rules = load_config(config_path)

        # Configure stack trace handling
        if stacklevel is not None:
            self.stacklevel = stacklevel
        else:
            self.stacklevel = int(os.environ.get("DATA_NADHI_STACKLEVEL", 2))

        if skip_stack is not None:
            self.skip_stack = skip_stack
        else:
            self.skip_stack = int(os.environ.get("DATA_NADHI_SKIP_STACK", 4))

        self.logger = logging.getLogger(self.module_name)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(log_formatter or JsonFormatter())
            self.logger.addHandler(handler)
            self.logger.setLevel(log_level)
            self.logger.propagate = False

    def _get_caller_info(self) -> tuple[str, int, str, str]:
        """Get information about the calling code's location.

        Uses the configured skip_stack value to determine how many frames
        to skip in the call stack. This allows accurate reporting of where
        the log call originated.

        Returns:
            tuple containing:
            - filename (str): Absolute path to the source file
            - line_number (int): Line number in the source file
            - function_name (str): Name of the calling function
            - module_name (str): Name of the module containing the call
        """
        frame = sys._getframe(self.skip_stack)
        filename = os.path.abspath(frame.f_code.co_filename)
        lineno = frame.f_lineno
        function_name = frame.f_code.co_name
        module_name = frame.f_globals.get("__name__")
        return filename, lineno, function_name, module_name

    def _build_internal_payload(
        self, level: str, message: str, context: dict = {}
    ) -> dict:
        """Build a structured log payload with metadata.

        Creates a standardized log payload including:
        - Basic log information (message, level)
        - Temporal information (timestamp)
        - Source code location (filename, line number, etc.)
        - Trace ID for request tracking
        - Custom context data

        Args:
            level: Log level (DEBUG, INFO, etc.)
            message: The log message
            context: Additional structured data about the log event

        Returns:
            Dictionary containing the complete log payload
        """
        filename, lineno, function_name, module_name = self._get_caller_info()

        return {
            "message": message,
            "trace_id": trace_id_var.get(),
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "log_record": {
                "filename": filename,
                "function_name": function_name,
                "level": level,
                "line_number": lineno,
                "module_name": module_name,
            },
            "context": context,
        }

    def rule_result(
        self,
        level: str,
        message: str,
        context: dict = {},
        trace_id: str | None = None,
    ) -> RuleEvaluationResult:
        """Evaluate log entry against rules and prepare the result.

        This method:
        1. Ensures a valid trace ID exists
        2. Builds the log payload
        3. Evaluates rules against the payload
        4. Returns the evaluation result

        Args:
            level: Log level (DEBUG, INFO, etc.)
            message: The log message
            context: Additional structured data
            trace_id: Optional trace ID for request tracking

        Returns:
            RuleEvaluationResult containing:
            - List of pipelines to trigger
            - Whether to output to stdout
            - The complete log payload
        """
        if trace_id is not None:
            trace_id_var.set(trace_id)
        if trace_id_var.get() is None:
            trace_id_var.set(str(uuid.uuid4()))
        payload = self._build_internal_payload(level, message, context)
        pipelines, stdout_flag = evaluate_rules(payload, rules=self.rules)
        return RuleEvaluationResult(
            pipelines=pipelines, stdout=stdout_flag, payload=payload
        )

    def trigger_pipelines(self, payload: dict, pipelines: list[str]) -> None:
        """Trigger data pipelines asynchronously.

        Each pipeline is triggered in a separate daemon thread to avoid
        blocking the logging operation.

        Args:
            payload: The log data to send to the pipeline
            pipelines: List of pipeline IDs to trigger
        """

        def trigger_pipeline_sync(pid: str, payload: dict) -> None:
            # TODO: Replace with actual pipeline triggering logic
            print(f"Trigger pipeline placeholder: {pid} with payload {payload}")

        # Trigger each pipeline in a separate daemon thread
        for pid in pipelines:
            threading.Thread(
                target=trigger_pipeline_sync, args=(pid, payload), daemon=True
            ).start()

    # Convenience methods for different log levels
    def debug(
        self, message: str, context: dict = {}, trace_id: str | None = None
    ) -> None:
        """Log a DEBUG level message with optional context and trace ID.

        Args:
            message: The log message
            context: Additional structured data
            trace_id: Optional trace ID for request tracking
        """
        rule_result = self.rule_result("DEBUG", message, context, trace_id)
        if rule_result.stdout:
            extra = {
                "context": rule_result.payload["context"],
                "trace_id": rule_result.payload["trace_id"],
            }
            self.logger.debug(message, extra=extra, stacklevel=self.stacklevel)
        self.trigger_pipelines(rule_result.payload, rule_result.pipelines)

    def info(
        self, message: str, context: dict = {}, trace_id: str | None = None
    ) -> None:
        """Log an INFO level message with optional context and trace ID.

        Args:
            message: The log message
            context: Additional structured data
            trace_id: Optional trace ID for request tracking
        """
        rule_result = self.rule_result("INFO", message, context, trace_id)
        if rule_result.stdout:
            extra = {
                "context": rule_result.payload["context"],
                "trace_id": rule_result.payload["trace_id"],
            }
            self.logger.info(message, extra=extra, stacklevel=self.stacklevel)
        self.trigger_pipelines(rule_result.payload, rule_result.pipelines)

    def warning(
        self, message: str, context: dict = {}, trace_id: str | None = None
    ) -> None:
        """Log a WARNING level message with optional context and trace ID.

        Args:
            message: The log message
            context: Additional structured data
            trace_id: Optional trace ID for request tracking
        """
        rule_result = self.rule_result("WARNING", message, context, trace_id)
        if rule_result.stdout:
            extra = {
                "context": rule_result.payload["context"],
                "trace_id": rule_result.payload["trace_id"],
            }
            self.logger.warning(message, extra=extra, stacklevel=self.stacklevel)
        self.trigger_pipelines(rule_result.payload, rule_result.pipelines)

    def error(
        self, message: str, context: dict = {}, trace_id: str | None = None
    ) -> None:
        """Log an ERROR level message with optional context and trace ID.

        Args:
            message: The log message
            context: Additional structured data
            trace_id: Optional trace ID for request tracking
        """
        rule_result = self.rule_result("ERROR", message, context, trace_id)
        if rule_result.stdout:
            extra = {
                "context": rule_result.payload["context"],
                "trace_id": rule_result.payload["trace_id"],
            }
            self.logger.error(message, extra=extra, stacklevel=self.stacklevel)
        self.trigger_pipelines(rule_result.payload, rule_result.pipelines)

    def critical(
        self, message: str, context: dict = {}, trace_id: str | None = None
    ) -> None:
        """Log a CRITICAL level message with optional context and trace ID.

        Args:
            message: The log message
            context: Additional structured data
            trace_id: Optional trace ID for request tracking
        """
        rule_result = self.rule_result("CRITICAL", message, context, trace_id)
        if rule_result.stdout:
            extra = {
                "context": rule_result.payload["context"],
                "trace_id": rule_result.payload["trace_id"],
            }
            self.logger.critical(message, extra=extra, stacklevel=self.stacklevel)
        self.trigger_pipelines(rule_result.payload, rule_result.pipelines)

    @staticmethod
    def get_record_defaults(record: logging.LogRecord) -> dict:
        """Extract default fields from a log record.

        This is a utility method for custom formatters to access standard
        log record fields in a consistent way.

        Args:
            record: The log record to process

        Returns:
            Dictionary of default log record fields
        """
        return {
            "timestamp": record.created,
            "module_name": record.name,
            "line_number": record.lineno,
            "function_name": record.funcName,
            "level": record.levelname,
            "filename": record.pathname,
        }
