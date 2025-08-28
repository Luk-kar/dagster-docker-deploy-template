import dagster as dg

from example.assets import all_assets

defs = dg.Definitions(assets=all_assets)
