"""
This script generates the `dagster.yaml` configuration file during build time
to avoid issues with missing environment variables at runtime.
Providing these variables dynamically can lead to errors (the cause unknown),
causing failures due to a missing configuration.

Instead of hardcoding the values, this approach ensures that the values are set
at build time, eliminating the need to manually update them whenever they change.
It's the safest workaround without too much tinkering with the webserver and daemon configurations.
"""

# Python
import os

# Third-party
from jinja2 import Environment, FileSystemLoader

# Local
from env_utils import generate_dagster_config_from_env

# Paths
output_folder = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(output_folder))

dagster_yaml_path = os.path.join(output_folder, "dagster.yaml")
template = env.get_template("dagster.yaml.jinja")


def get_int_env(var_name: str) -> int:
    value = os.getenv(var_name)

    if not value:
        raise ValueError(f"Missing or empty environment variable: {var_name}")

    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Environment variable {var_name} must be an integer, got '{value}'"
        )


def get_env(var_name: str) -> str:
    value = os.getenv(var_name)

    if not value:
        raise ValueError(f"Missing or empty environment variable: {var_name}")
    return value


# Define configuration variables with their types and environment variable names
config_variables = [
    {
        "name": "DAGSTER_POSTGRES_PORT",
        "env_var": "DAGSTER_POSTGRES_PORT",
        "type": "int",
    },
    {
        "name": "PIPELINE_NETWORK_NAME",
        "env_var": "PIPELINE_NETWORK_NAME",
        "type": "str",
    },
    # Add more configuration variables here as needed
    # {
    #     "name": "DAGSTER_LOG_LEVEL",
    #     "env_var": "DAGSTER_LOG_LEVEL",
    #     "type": "str"
    # },
]


# Generate configuration by reading from environment variables
config = generate_dagster_config_from_env(config_variables)

# Render template with validated environment variables
dagster_yaml = template.render(config)

# Write to dagster.yaml
with open(dagster_yaml_path, "w") as f:
    f.write(dagster_yaml)

print(f"dagster.yaml generated successfully at:\n{dagster_yaml_path}!")
