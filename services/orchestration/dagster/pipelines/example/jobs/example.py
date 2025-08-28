# dagster
from dagster import define_asset_job

# subject
from example.assets.example import example_asset

example_job = define_asset_job("partitioned_job", selection=[example_asset])
