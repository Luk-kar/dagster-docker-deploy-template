# ======================================================
# definitions are the objects that encapsulate
# metadata and Python functions d
# escribing how Dagster entities—such as
# assets, jobs, schedules, sensors, and resources—should behave,
# and the top-level Definitions object aggregates all these entities
# for deployment and orchestration within a project.
#
# https://docs.dagster.io/guides/build/projects/moving-to-components/migrating-definitions
#
# ======================================================

import dagster as dg

from example.assets import all_assets
from example.jobs import all_jobs
from common.resources import all_resources

defs = dg.Definitions(assets=all_assets, jobs=all_jobs, resources=all_resources)
