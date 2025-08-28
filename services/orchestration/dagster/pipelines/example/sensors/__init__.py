# ======================================================
# Sensor is mechanisms that automatically
# trigger jobs or actions
# in response to specific internal or external events, such as
# files arriving, asset changes, or job status updates,
# by polling for conditions at regular intervals and
# acting when criteria are met.
# ======================================================

## dagster
# from dagster import SensorDefinition, RunRequest, sensor

# local
# from subject.jobs.example import example_job

## Example sensor: Triggers job when external condition is met
# @sensor(job=example_job)
# def example_sensor(context):
#     # External check (e.g. file existence, DB flag, etc.)
#     if some_external_condition():
#         yield RunRequest(run_key=None, run_config={})
#
# def some_external_condition():
#     # Replace with your custom logic
#     return False

## Note:
## Sensors need to be registered in Definitions via 'sensors=[...]' if enabled.

# Local - all sensors

# all_sensors = [example_sensor]
