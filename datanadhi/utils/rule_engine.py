"""Rule engine for evaluating log entries against configured rules.

This module implements the core logic for matching log entries against rules
and determining which pipelines to trigger and whether to output to stdout.
"""

import re
from typing import Any

from .datatypes import ConditionType, Rule, RuleCondition


def get_nested_value(data: dict, key_path: str) -> Any:
    """Safely retrieve a nested value from a dictionary using dot notation.

    Args:
        data: Dictionary to search in
        key_path: Dot-separated path to the value (e.g., "context.user.id")

    Returns:
        The value at the specified path, or None if any part of the path doesn't exist
    """
    keys = key_path.split(".")
    val = data
    for k in keys:
        val = val.get(k) if isinstance(val, dict) else None
        if val is None:
            break
    return val


def match_condition(value: Any, condition: RuleCondition) -> bool:
    """Check if a value matches a condition according to its type.

    Args:
        value: The value to check (from the log entry)
        condition: The condition to match against

    Returns:
        True if the value matches the condition, False otherwise
    """
    if value is None:
        return False

    cond_type = condition.type
    cond_val = condition.value

    if cond_type == ConditionType.EXACT:
        return value == cond_val
    if cond_type == ConditionType.PARTIAL:
        return cond_val in str(value)
    if cond_type == ConditionType.REGEX:
        return bool(re.match(cond_val, str(value)))
    return False


def evaluate_rules(
    log_dict: dict, rules: list[Rule] | None = None
) -> tuple[list[str], bool]:
    """Evaluate log entry against a set of rules to determine actions.

    This function implements the core rule evaluation logic:
    - For each rule, evaluate its conditions based on the any_condition_match flag
    - If any_condition_match is True, trigger on first matching condition
    - If any_condition_match is False, all conditions must match
    - Collect all pipeline IDs that should be triggered
    - Set stdout flag if any matching rule has stdout=True

    Args:
        log_dict: The log entry to evaluate against rules
        rules: List of rules to check. If None, returns empty result

    Returns:
        A tuple of (pipeline_ids, stdout_flag) where:
        - pipeline_ids is a list of pipeline IDs that should be triggered
        - stdout_flag indicates whether the log should be output to stdout
    """
    try:
        pipelines_to_trigger = set()
        stdout_flag = False
        if not rules:
            return [], stdout_flag

        for rule in rules:
            conditions = rule.conditions
            any_condition_match = rule.any_condition_match
            all_conditions_match = True

            for condition in conditions:
                # Get the value from the log entry using the condition's key path
                value = get_nested_value(log_dict, condition.key)
                condition_match = match_condition(value, condition)

                if condition_match:
                    # For any_condition_match=True, trigger immediately on first match
                    if any_condition_match:
                        pipelines_to_trigger.update(rule.pipelines)
                        if rule.stdout:
                            stdout_flag = True
                        break
                else:
                    # For any_condition_match=False, fail fast on first non-match
                    if any_condition_match:
                        continue
                    all_conditions_match = False
                    break

            # For any_condition_match=False, trigger only if all conditions matched
            if all_conditions_match and not any_condition_match:
                pipelines_to_trigger.update(rule.pipelines)
                if rule.stdout:
                    stdout_flag = True

        return list(pipelines_to_trigger), stdout_flag
    except Exception as e:
        print(f"Error evaluating rules: {e}")
        return [], False
