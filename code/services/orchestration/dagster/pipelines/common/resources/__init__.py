from minio import Minio
import psycopg
import os


def minio_client():

    use_secure = (
        True if os.getenv("DATALAKE_MINIO_SECURE", "False").lower() == "true" else False
    )

    return Minio(
        endpoint=f"localhost:{os.getenv('DATALAKE_MINIO_PORT_API', '9000')}",
        access_key=os.getenv("DATALAKE_MINIO_ROOT_USER"),
        secret_key=os.getenv("DATALAKE_MINIO_ROOT_PASSWORD"),
        secure=use_secure,
    )


def postgres_client():

    return psycopg.connect(
        host="localhost",
        port=os.getenv("WAREHOUSE_POSTGRES_PORT"),
        user=os.getenv("WAREHOUSE_POSTGRES_USER"),
        password=os.getenv("WAREHOUSE_POSTGRES_PASSWORD"),
        dbname=os.getenv("WAREHOUSE_POSTGRES_DB"),
    )


all_resources = {
    "minio_client": minio_client,
    "postgres_client": postgres_client,
}
