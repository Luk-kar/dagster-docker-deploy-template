# ======================================================
#  An asset represents a logical unit of data such as
# a table, dataset, or machine learning model.
#
# https://docs.dagster.io/dagster-basics-tutorial/assets
#
# ======================================================

# Dagster assets
from .example import example_asset

# All assets
all_assets = [example_asset]
