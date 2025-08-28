`./code/dagster.yaml`:
```
scheduler:
  module: dagster.core.scheduler
  class: DagsterDaemonScheduler


run_coordinator:
  module: dagster.core.run_coordinator
  class: QueuedRunCoordinator
  config:
    max_concurrent_runs: 5
    tag_concurrency_limits:
      - key: "operation"
        value: "example"
        limit: 5

run_launcher:
  module: dagster_docker
  class: DockerRunLauncher
  config:
    env_vars:
      - DAGSTER_POSTGRES_USER
      - DAGSTER_POSTGRES_PASSWORD
      - DAGSTER_POSTGRES_DB
    network: docker_example_network
    container_kwargs:
      volumes: # Make docker client accessible to any launched containers as well
        - /var/run/docker.sock:/var/run/docker.sock
        - /tmp/io_manager_storage:/tmp/io_manager_storage

run_storage:
  module: dagster_postgres.run_storage
  class: PostgresRunStorage
  config:
    postgres_db:
      hostname: docker_example_postgresql
      username:
        env: DAGSTER_POSTGRES_USER
      password:
        env: DAGSTER_POSTGRES_PASSWORD
      db_name:
        env: DAGSTER_POSTGRES_DB
      port: 5432

schedule_storage:
  module: dagster_postgres.schedule_storage
  class: PostgresScheduleStorage
  config:
    postgres_db:
      hostname: docker_example_postgresql
      username:
        env: DAGSTER_POSTGRES_USER
      password:
        env: DAGSTER_POSTGRES_PASSWORD
      db_name:
        env: DAGSTER_POSTGRES_DB
      port: 5432

event_log_storage:
  module: dagster_postgres.event_log
  class: PostgresEventLogStorage
  config:
    postgres_db:
      hostname: docker_example_postgresql
      username:
        env: DAGSTER_POSTGRES_USER
      password:
        env: DAGSTER_POSTGRES_PASSWORD
      db_name:
        env: DAGSTER_POSTGRES_DB
      port: 5432

```

`./code/definitions.py`:
```
import dagster as dg


@dg.asset(
    op_tags={"operation": "example"},
    partitions_def=dg.DailyPartitionsDefinition("2024-01-01"),
)
def example_asset(context: dg.AssetExecutionContext):
    context.log.info(context.partition_key)


partitioned_asset_job = dg.define_asset_job("partitioned_job", selection=[example_asset])

defs = dg.Definitions(assets=[example_asset], jobs=[partitioned_asset_job])

```

`./code/docker-compose.yml`:
```
version: "3.7"

services:
  # This service runs the postgres DB used by dagster for run storage, schedule storage,
  # and event log storage. Depending on the hardware you run this Compose on, you may be able
  # to reduce the interval and timeout in the healthcheck to speed up your `docker-compose up` times.
  docker_example_postgresql:
    image: postgres:11
    container_name: docker_example_postgresql
    environment:
      POSTGRES_USER: "postgres_user"
      POSTGRES_PASSWORD: "postgres_password"
      POSTGRES_DB: "postgres_db"
    networks:
      - docker_example_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres_user -d postgres_db"]
      interval: 10s
      timeout: 8s
      retries: 5

  # This service runs the gRPC server that loads your user code, in both dagster-webserver
  # and dagster-daemon. By setting DAGSTER_CURRENT_IMAGE to its own image, we tell the
  # run launcher to use this same image when launching runs in a new container as well.
  # Multiple containers like this can be deployed separately - each just needs to run on
  # its own port, and have its own entry in the workspace.yaml file that's loaded by the
  # webserver.
  docker_example_user_code:
    build:
      context: .
      dockerfile: ./Dockerfile_user_code
    container_name: docker_example_user_code
    image: docker_example_user_code_image
    restart: always
    environment:
      DAGSTER_POSTGRES_USER: "postgres_user"
      DAGSTER_POSTGRES_PASSWORD: "postgres_password"
      DAGSTER_POSTGRES_DB: "postgres_db"
      DAGSTER_CURRENT_IMAGE: "docker_example_user_code_image"
    networks:
      - docker_example_network

  # This service runs dagster-webserver, which loads your user code from the user code container.
  # Since our instance uses the QueuedRunCoordinator, any runs submitted from the webserver will be put on
  # a queue and later dequeued and launched by dagster-daemon.
  dagster_webserver:
    build:
      context: .
      dockerfile: ./Dockerfile_dagster
    entrypoint:
      - dagster-webserver
      - -h
      - "0.0.0.0"
      - -p
      - "3000"
      - -w
      - workspace.yaml
    container_name: dagster_webserver
    expose:
      - "3000"
    ports:
      - "3000:3000"
    environment:
      DAGSTER_POSTGRES_USER: "postgres_user"
      DAGSTER_POSTGRES_PASSWORD: "postgres_password"
      DAGSTER_POSTGRES_DB: "postgres_db"
    volumes: # Make docker client accessible so we can terminate containers from the webserver
      - /var/run/docker.sock:/var/run/docker.sock
      - /tmp/io_manager_storage:/tmp/io_manager_storage
    networks:
      - docker_example_network
    depends_on:
      docker_example_postgresql:
        condition: service_healthy
      docker_example_user_code:
        condition: service_started

  # This service runs the dagster-daemon process, which is responsible for taking runs
  # off of the queue and launching them, as well as creating runs from schedules or sensors.
  dagster_daemon:
    build:
      context: .
      dockerfile: ./Dockerfile_dagster
    entrypoint:
      - dagster-daemon
      - run
    container_name: dagster_daemon
    restart: on-failure
    environment:
      DAGSTER_POSTGRES_USER: "postgres_user"
      DAGSTER_POSTGRES_PASSWORD: "postgres_password"
      DAGSTER_POSTGRES_DB: "postgres_db"
    volumes: # Make docker client accessible so we can launch containers using host docker
      - /var/run/docker.sock:/var/run/docker.sock
      - /tmp/io_manager_storage:/tmp/io_manager_storage
    networks:
      - docker_example_network
    depends_on:
      docker_example_postgresql:
        condition: service_healthy
      docker_example_user_code:
        condition: service_started

networks:
  docker_example_network:
    driver: bridge
    name: docker_example_network

```

`./code/Dockerfile_dagster`:
```
# Dagster libraries to run both dagster-webserver and the dagster-daemon. Does not
# need to have access to any pipeline code.

FROM python:3.10-slim

RUN pip install \
    dagster \
    dagster-graphql \
    dagster-webserver \
    dagster-postgres \
    dagster-docker

# Set $DAGSTER_HOME and copy dagster instance and workspace YAML there
ENV DAGSTER_HOME=/opt/dagster/dagster_home/

RUN mkdir -p $DAGSTER_HOME

COPY dagster.yaml workspace.yaml $DAGSTER_HOME

WORKDIR $DAGSTER_HOME

```

`./code/Dockerfile_user_code`:
```
FROM python:3.10-slim

# Checkout and install dagster libraries needed to run the gRPC server
# exposing your repository to dagster-webserver and dagster-daemon, and to load the DagsterInstance

RUN pip install \
    dagster \
    dagster-postgres \
    dagster-docker

# Add repository code

WORKDIR /opt/dagster/app

COPY definitions.py /opt/dagster/app

# Run dagster gRPC server on port 4000

EXPOSE 4000

CMD ["dagster", "api", "grpc", "-h", "0.0.0.0", "-p", "4000", "-f", "definitions.py"]

```

`./code/__init__.py`:
```

```

`./code/README.md`:
```
View this example in the Dagster docs at https://docs.dagster.io/examples/deploy_docker.

```

`./code/requirements.txt`:
```
dagster
dagster-webserver
dagster-docker

```

`./code/tox.ini`:
```
[tox]
skipsdist = True

[testenv]
download = True
passenv =
    CI_*
    BUILDKITE*
    DEPLOY_DOCKER_WEBSERVER_HOST
    PYTEST_ADDOPTS
    PYTEST_PLUGINS
    DAGSTER_GIT_REPO_DIR
install_command = python3 {env:DAGSTER_GIT_REPO_DIR}/scripts/uv-retry-install.py {opts} {packages}
deps =
  -e ../../python_modules/dagster[test]
  -e ../../python_modules/dagster-pipes
  -e ../../python_modules/libraries/dagster-shared
allowlist_externals =
  /bin/bash
  uv
commands =
  !windows: /bin/bash -c '! pip list --exclude-editable | grep -e dagster'
  pytest -vv -s {posargs}

```

`./code/workspace.yaml`:
```
load_from:
  # Each entry here corresponds to a service in the docker-compose file that exposes user code.
  - grpc_server:
      host: docker_example_user_code
      port: 4000
      location_name: "example_user_code"

```

