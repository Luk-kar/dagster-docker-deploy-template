"""
This script generates the `workspace.yaml` configuration file during build time
because the pipeline port environment variables cannot be provided dynamically.
In this YAML configuration, the port values must be hardcoded, and failing to do so
would result in missing configuration errors.

Instead of manually updating the ports, this approach ensures that the values are set
at build time, eliminating the need to remember and change them whenever they update.
It's the safest workaround without too much tinkering with the webserver and daemon configurations.
"""

# Python
import os

# Third-party
from jinja2 import Environment, FileSystemLoader

# Local
from env_utils import (
    validate_dagster_environment_variables,
    discover_dagster_code_services,
)

# Fail fast
validate_dagster_environment_variables()

# Paths
output_folder = os.path.dirname(os.path.abspath(__file__))

env = Environment(loader=FileSystemLoader(output_folder))

workspace_yaml_path = os.path.join(output_folder, "workspace.yaml")

template = env.get_template("workspace.yaml.jinja")

service_configs = discover_dagster_code_services()

workspace_yaml_content = template.render(services=service_configs)

# Write to workspace.yaml
with open(workspace_yaml_path, "w") as f:
    f.write(workspace_yaml_content)

print(f"workspace.yaml generated successfully at:\n{workspace_yaml_path}!")
