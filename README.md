# Dagster Docker Deploy (Dynamic Template)

A refactored, dynamic template derived from the official Dagster [“deploy with Docker Compose” example](https://github.com/dagster-io/dagster/tree/master/examples/deploy_docker), designed for flexible configuration and simple deployment. More about Dagster services [here](https://docs.dagster.io/deployment/oss/deployment-options/docker).

## Overview

This template follows the recommended Dagster Docker Compose architecture: a **webserver**, a **daemon**, and one or more **code locations**. Each pipeline run typically launches in a dedicated container for isolation and scalability.

## Dynamic Configuration with Environment Variables

Configuration options can be overridden via environment variables:

- **Postgres connection:**  
 Set `DAGSTER_POSTGRES_USER`, `DAGSTER_POSTGRES_PASSWORD`, `DAGSTER_POSTGRES_PORT` and `DAGSTER_POSTGRES_DB` on the webserver, daemon, and code location services for storage of runs, logs, and schedules.
- **Ports:**  
 Use `DAGSTER_WEBSERVER_PORT` to expose the webserver (e.g., 3000) and `DAGSTER_CODE_EXAMPLE_PORT` for each code location’s gRPC server; assign unique ports in your `docker-compose.yaml` and `.env` files.
- **Code location identification:**  
 Name variables for each code location following a pattern like `DAGSTER_CODE_<IDENTIFIER>_NAME` and `DAGSTER_CODE_<IDENTIFIER>_PORT`, where `<IDENTIFIER>` matches the folder under `services/orchestration/dagster/pipelines/<identifier>`.

## Adding a New code location

Follow this pattern to add another code location (code location):

1. **Clone example pipeline:**  
 Copy the `services/orchestration/dagster/pipelines/example` folder to a new directory, such as `analytics` (`services/orchestration/dagster/pipelines/analytics`).
2. **Configure environment variables:**  
 Add environment variables in your `.env` or Compose config:  
   - `DAGSTER_CODE_ANALYTICS_NAME`  
   - `DAGSTER_CODE_ANALYTICS_PORT`
3. **Update Compose service:**  
 Duplicate the `dagster_code_example` service in the `docker-compose.yaml`, rename it (e.g., `dagster_code_analytics`), and update its settings (image name, build context, environment, port matching your new directory and variables).
4. **Update args:**
 Update args `DAGSTER_CODE_ANALYTICS_NAME` and `DAGSTER_CODE_ANALYTICS_PORT` in the copied `Dockerfile.code_space`

## Example Compose Service Configuration
```yaml
  dagster_code_analytics:
    build:
      context: ./services/orchestration/dagster/pipelines
      dockerfile: ./analytics/Dockerfile.code_space
      args:
        - DAGSTER_CODE_ANALYTICS_NAME=${DAGSTER_CODE_ANALYTICS_NAME}
        - DAGSTER_CODE_ANALYTICS_PORT=${DAGSTER_CODE_ANALYTICS_PORT}
    container_name: ${DAGSTER_CODE_ANALYTICS_NAME}
    image: "${DAGSTER_CODE_ANALYTICS_NAME}_image"
    restart: always
    environment:
      WAREHOUSE_POSTGRES_USER: ${DAGSTER_POSTGRES_USER}
      WAREHOUSE_POSTGRES_PASSWORD: ${DAGSTER_POSTGRES_PASSWORD}
      WAREHOUSE_POSTGRES_DB: ${DAGSTER_POSTGRES_DB}
      WAREHOUSE_POSTGRES_PORT: ${DAGSTER_POSTGRES_PORT}

      DAGSTER_CURRENT_IMAGE: "${DAGSTER_CODE_ANALYTICS_NAME}_image"
      DAGSTER_CODE_ANALYTICS_PORT: ${DAGSTER_CODE_ANALYTICS_PORT}
      DAGSTER_CODE_ANALYTICS_NAME: ${DAGSTER_CODE_ANALYTICS_NAME}
    ports:
     - ${DAGSTER_CODE_ANALYTICS_PORT}:${DAGSTER_CODE_ANALYTICS_PORT}
    networks:
     - ${PIPELINE_NETWORK_NAME}

```

## Added Variables for `.env` (example for `analytics` code location)

```
# New code location
DAGSTER_CODE_ANALYTICS_NAME=analytics
DAGSTER_CODE_ANALYTICS_PORT=4002

# Global/shared variables
DAGSTER_POSTGRES_USER=postgres_user
DAGSTER_POSTGRES_PASSWORD=postgres_password
DAGSTER_POSTGRES_DB=postgres_db
```
## Requirements

- Docker and Docker Compose are installed locally or on the target host.

## Quick start

1) Clone the repository.
 ```
 git clone git@github.com:Luk-kar/dagster-docker-deploy.git
 cd dagster-docker-deploy
 ```
2) Rename the `.env.example` to `.env`:
 ```
 cp ".env.example" ".env"
 ```
3) Review and adjust values in `.env` and update code location entries in `docker-compose.yaml` as needed.
4) Build images:
 ``` 
 docker compose build
 ```
 This builds the Dagster webserver/daemon image and any user‑code images defined in the Compose file.

5) Launch the stack:
 ```
 docker compose up  
 ```
 This starts the webserver, daemon, backing services (e.g., Postgres), and code locations.

## How it differs from the official example

- Dynamic templating: Incorporates templating (e.g., Jinja) and scripts to generate configuration (`dagster.yaml` and `workspace.yaml`) and compose files more flexibly than a static example.  
- Template orientation: Structured as a reusable starting point rather than a single fixed configuration in the Dagster monorepo example directory.
- Same deployment model: Retains Dagster’s recommended Docker Compose topology (webserver, daemon, code locations, per‑run containers).

## Tips

- Use secrets instead of the `.env` file when you set up in production.
- Validate container startup by checking logs for the webserver and daemon services after docker compose up.
- Ensure DAGSTER_HOME is set within images that run Dagster processes and that dagster.yaml/workspace.yaml are available there.
