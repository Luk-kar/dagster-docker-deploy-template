# ======================================================
# Schedule is automation tools that define specific time intervals (using cron expressions)
# for jobs or workflows to execute automatically, enabling tasks to run periodically such as
# daily, weekly, or at custom times without manual intervention.
#
# https://docs.dagster.io/guides/automate/schedules#next-steps
#
# ======================================================

## dagster
# from dagster import ScheduleDefinition

## local
# from subject.jobs.example import example_job

## Example schedule: Runs daily at 7:00 AM
# example_schedule = ScheduleDefinition(
#     job=example_job,
#     cron_schedule="0 7 * * *",  # every day at 7:00 AM
#     execution_timezone="Europe/Warsaw",
# )

## Note:
## Register schedules in Definitions via 'schedules=[...]' argument if needed.

# Local - all schedules

# all_schedules = [example_schedule]
