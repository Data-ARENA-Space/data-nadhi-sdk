"""Data types and classes for the Data Nadhi rule engine and logging system.

This module defines the core data structures used throughout the Data Nadhi SDK,
including rule definitions, condition types, and evaluation results.
"""

from dataclasses import dataclass, field
from enum import Enum


class ConditionType(str, Enum):
    """Types of conditions that can be used in rules.

    This enum inherits from str to allow direct YAML deserialization.

    Attributes:
        EXACT: Direct equality comparison (value == condition)
        PARTIAL: Substring matching (condition in value)
        REGEX: Regular expression pattern matching
    """

    EXACT = "exact"
    PARTIAL = "partial"
    REGEX = "regex"


@dataclass
class RuleCondition:
    """A condition that must be satisfied for a rule to trigger.

    Args:
        key: Dot-notation path to the value in the log data (e.g., "context.user.id")
        type: The type of condition (EXACT, PARTIAL, or REGEX)
        value: The value to match against. Interpretation varies by condition type
    """

    key: str
    type: ConditionType
    value: str


@dataclass
class Rule:
    """A rule that defines when and how to process log data.

    Args:
        name: Unique identifier for the rule
        conditions: List of conditions that must be satisfied
        any_condition_match: If True, any match triggers. If False, all must match
        stdout: Whether to output the log to stdout when rule matches
        pipelines: List of pipeline IDs to trigger when rule matches
    """

    name: str
    conditions: list[RuleCondition]
    any_condition_match: bool = False
    stdout: bool = False
    pipelines: list[str] = field(default_factory=list)


@dataclass
class RuleEvaluationResult:
    """Result of evaluating rules against a log entry.

    Args:
        pipelines: List of pipeline IDs that should be triggered
        stdout: Whether the log should be output to stdout
        payload: The complete log data that triggered the rule
    """

    pipelines: list[str]
    stdout: bool
    payload: dict
