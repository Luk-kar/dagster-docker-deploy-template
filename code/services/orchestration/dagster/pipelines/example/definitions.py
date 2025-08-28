import dagster as dg

from example.assets import all_assets
from example.jobs import all_jobs

defs = dg.Definitions(assets=all_assets, jobs=all_jobs)
