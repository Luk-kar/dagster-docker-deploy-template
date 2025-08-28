"""
Environment variable utilities for Dagster configuration generators.

These utilities are designed to safely read and validate environment variables
at build time, preventing runtime failures due to missing or invalid configuration.

The generators use these functions to create static YAML configuration files like in
(dagster.yaml and workspace.yaml).
"""

# Python
from os import getenv, environ
import re


def get_int_env(var_name: str) -> int:
    """
    Get an environment variable as an integer with validation.

    Args:
        var_name: Name of the environment variable to retrieve

    Returns:
        The environment variable value as an integer

    Raises:
        ValueError: If the variable is missing, empty, or cannot be converted to int
    """

    value = getenv(var_name)

    # Check if the value is None or an empty string
    if not value:
        raise ValueError(f"Missing or empty environment variable: {var_name}")

    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Environment variable {var_name} must be an integer, got '{value}'"
        )


def get_env(var_name: str) -> str:
    """
    Get an environment variable as a string with validation.

    Args:
        var_name: Name of the environment variable to retrieve

    Returns:
        The environment variable value as a string

    Raises:
        ValueError: If the variable is missing or empty
    """

    value = getenv(var_name)
    if not value:
        raise ValueError(f"Missing or empty environment variable: {var_name}")
    return value


def generate_dagster_config_from_env(config_variables: list) -> dict:
    """
    Generate Dagster YAML configuration from environment variables.
    """

    config = {}
    for var_config in config_variables:
        var_name = var_config["name"]
        env_var = var_config["env_var"]
        var_type = var_config["type"]

        if var_type == "int":
            config[var_name] = get_int_env(env_var)
        elif var_type == "str":
            config[var_name] = get_env(env_var)
        else:
            raise ValueError(f"Unsupported variable type: {var_type}")
    return config


def discover_dagster_code_services() -> list:
    """
    Automatically discover DAGSTER_CODE_* environment variables and pair them.

    Looks for patterns like:
    - DAGSTER_CODE_001_NAME and DAGSTER_CODE_001_PORT
    - DAGSTER_CODE_002_NAME and DAGSTER_CODE_002_PORT
    - DAGSTER_CODE_ANALYTICS_NAME and DAGSTER_CODE_ANALYTICS_PORT

    Returns:
        List of service configuration dictionaries
    """
    services = []
    env_vars = dict(environ)

    name_pattern = re.compile(r"^DAGSTER_CODE_(.+)_NAME$")

    for env_var_name, env_var_value in env_vars.items():
        name_match = name_pattern.match(env_var_name)

        if name_match:
            identifier = name_match.group(1)
            port_env_var = f"DAGSTER_CODE_{identifier}_PORT"

            if port_env_var in env_vars:
                service_name = env_var_value
                service_port = env_vars[port_env_var]
                services.append({"name": service_name, "port": service_port})
            else:
                raise ValueError(
                    f"Found {env_var_name} but missing corresponding {port_env_var}"
                )

    if not services:
        raise ValueError(
            "No DAGSTER_CODE_*_NAME and DAGSTER_CODE_*_PORT pairs found in environment variables.\n"
            "Expected pattern: DAGSTER_CODE_<IDENTIFIER>_NAME and DAGSTER_CODE_<IDENTIFIER>_PORT\n"
            f"Variables names: {list(env_vars.keys())}"
        )

    return services


def validate_dagster_environment_variables():
    """
    Validate that all DAGSTER_* environment variables are recognized.

    Raises:
        ValueError: If any unrecognized DAGSTER_* variables are found
    """
    allowed_dagster_vars = {
        "DAGSTER_POSTGRES_PORT",
        "DAGSTER_WEBSERVER_PORT",
        "DAGSTER_CURRENT_IMAGE",
        "DAGSTER_HOME",  # Standard Dagster environment variable set by Docker
    }

    env_vars = dict(environ)
    dagster_vars = [var for var in env_vars.keys() if var.startswith("DAGSTER_")]

    # Check for DAGSTER_CODE_* pattern variables (these are allowed)
    code_name_pattern = re.compile(r"^DAGSTER_CODE_.+_NAME$")
    code_port_pattern = re.compile(r"^DAGSTER_CODE_.+_PORT$")

    unrecognized_vars = []

    for var in dagster_vars:
        if (
            var not in allowed_dagster_vars
            and not code_name_pattern.match(var)
            and not code_port_pattern.match(var)
        ):
            unrecognized_vars.append(var)

    if unrecognized_vars:
        raise ValueError(
            f"Unrecognized DAGSTER_* environment variables found: {unrecognized_vars}. "
            f"Allowed variables: {sorted(allowed_dagster_vars)} or DAGSTER_CODE_*_NAME/DAGSTER_CODE_*_PORT pairs"
        )
