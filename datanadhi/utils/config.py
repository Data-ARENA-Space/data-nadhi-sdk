"""Configuration management for Data Nadhi SDK.

This module handles loading rule configurations from YAML files and managing
API key authentication. It provides functions to:
1. Load and parse rule configurations
2. Convert YAML configurations to Rule objects
3. Retrieve API keys from environment variables or explicit parameters
"""

import os
from pathlib import Path

import yaml

from .datatypes import Rule, RuleCondition


class ConfigCache:
    def __init__(self):
        self.value = None

    @property
    def cache(self):
        return self.value

    def set_cache(self, value):
        self.value = value


def get_config_paths(config_dir: Path) -> dict[str, Path]:
    """Get paths for configuration files in the specified directory.

    This function constructs paths for the main config.yaml and a sample
    config_sample.yaml file within the given directory.

    Args:
        config_dir: Directory where config files are located

    Returns:
        Dictionary with keys 'config' and 'sample' pointing to respective file paths
    """
    if not config_dir.is_dir():
        raise NotADirectoryError(f"{config_dir} is not a valid directory")
    return [p for p in config_dir.glob("*.yaml")] + [
        p for p in config_dir.glob("*.yml")
    ]


def load_config(
    config_cache: ConfigCache, input_config_dir: str | None = None
) -> list[Rule]:
    """Load and parse rules from a YAML configuration file.

    This function reads a YAML configuration file and converts it into a list
    of Rule objects. If no path is provided, it looks for a config.yaml file
    in the .datanadhi directory of the current working directory.

    The YAML file should have this structure:
    ```yaml
    rules:
      - name: rule_name
        conditions:
          - key: path.to.value
            type: exact|partial|regex
            value: value_to_match
        stdout: true|false
        pipelines:
          - pipeline_id_1
          - pipeline_id_2
    ```

    Args:
        input_config_path: Optional path to the configuration file

    Returns:
        List of Rule objects parsed from the configuration

    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        yaml.YAMLError: If the configuration file is invalid YAML
    """
    if input_config_dir:
        config_dir = Path(input_config_dir)
    else:
        config_dir = Path(os.getcwd()) / ".datanadhi"

    config_paths = get_config_paths(config_dir)

    if len(config_paths) == 0:
        raise FileNotFoundError(f"No config found in {config_dir}")

    rules = []
    for config_path in config_paths:
        with open(config_path) as f:
            config = yaml.safe_load(f)
            rules = []
            for rule in config.get("rules", []):
                # Convert conditions to RuleCondition objects
                rule["conditions"] = [
                    RuleCondition(**cond) for cond in rule.get("conditions", [])
                ]
                # Create Rule object with all attributes
                rule_obj = Rule(**rule)
                rules.append(rule_obj)
    config_cache.set_cache(rules)
    return rules


def get_api_key(explicit_api_key: str | None = None) -> str:
    """Get the Data Nadhi API key from parameter or environment.

    This function tries to get the API key in this order:
    1. From the explicit_api_key parameter if provided
    2. From the DATA_NADHI_API_KEY environment variable
    3. Raises an error if no key is found

    Args:
        explicit_api_key: Optional API key provided directly

    Returns:
        The API key as a string

    Raises:
        ValueError: If no API key is found in parameters or environment
    """
    if explicit_api_key:
        return explicit_api_key

    env_key = os.environ.get("DATA_NADHI_API_KEY")
    if not env_key:
        raise ValueError("API key not provided via parameter or DATA_NADHI_API_KEY env")
    return env_key
