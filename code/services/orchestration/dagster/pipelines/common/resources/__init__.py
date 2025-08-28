# python
import os

# third-party
import psycopg


def postgres_client():

    return psycopg.connect(
        host="localhost",
        port=os.getenv("WAREHOUSE_POSTGRES_PORT"),
        user=os.getenv("WAREHOUSE_POSTGRES_USER"),
        password=os.getenv("WAREHOUSE_POSTGRES_PASSWORD"),
        dbname=os.getenv("WAREHOUSE_POSTGRES_DB"),
    )


all_resources = {
    "postgres_client": postgres_client,
}
