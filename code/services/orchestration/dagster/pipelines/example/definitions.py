# ======================================================
# definitions are the objects that encapsulate
# metadata and Python functions d
# escribing how Dagster entities—such as
# assets, jobs, schedules, sensors, and resources—should behave,
# and the top-level Definitions object aggregates all these entities
# for deployment and orchestration within a project.
# ======================================================

import dagster as dg

from example.assets import all_assets
from example.jobs import all_jobs

defs = dg.Definitions(assets=all_assets, jobs=all_jobs)
