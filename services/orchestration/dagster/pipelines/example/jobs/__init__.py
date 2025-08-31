# ======================================================
# A job is the main unit of execution and monitoring,
# encapsulating a graph of assets or ops that can be
# run on a schedule or triggered externally.
#
# https://docs.dagster.io/guides/build/jobs
#
# ======================================================

# Local - all jobs

from .example import example_job

all_jobs = [example_job]
