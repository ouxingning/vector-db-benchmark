import os

ORACLE23AI_PORT = int(os.getenv("ORACLE23AI_PORT", 1521))
ORACLE23AI_DB = os.getenv("ORACLE23AI_DB", "vector")
ORACLE23AI_USER = os.getenv("ORACLE23AI_USER", "vector")
ORACLE23AI_PASSWORD = os.getenv("ORACLE23AI_PASSWORD", "vector")
ORACLE23AI_SERVICE_NAME = os.getenv("ORACLE23AI_SERVICE_NAME", "")


def get_db_config(host, connection_params):
    return {
        "host": host or "localhost",
        "port": ORACLE23AI_PORT,
        "dbname": ORACLE23AI_DB,
        "user": ORACLE23AI_USER,
        "password": ORACLE23AI_PASSWORD,
        "service_name": ORACLE23AI_SERVICE_NAME,
        "autocommit": True,
        **connection_params,
    }
