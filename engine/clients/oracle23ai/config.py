import os

CS = '''(DESCRIPTION=(CONNECT_TIMEOUT=5)(TRANSPORT_CONNECT_TIMEOUT=3)(RETRY_COUNT=3)
        (ADDRESS_LIST=(LOAD_BALANCE=on)(ADDRESS=(PROTOCOL=TCP)(HOST=192.168.0.77)(PORT=1521)))
        (CONNECT_DATA=(SERVICE_NAME=vectordb_h7k_yny.adatvcn.tonyvcn.oraclevcn.com)))'''

ORACLE23AI_USER = os.getenv("ORACLE23AI_USER", "vector")
ORACLE23AI_PASSWORD = os.getenv("ORACLE23AI_PASSWORD", "VectorDB#_123")
ORACLE23AI_DSN = os.getenv("ORACLE23AI_DSN", CS)

# ORACLE23AI_PORT = int(os.getenv("ORACLE23AI_PORT", 1521))
# ORACLE23AI_DB = os.getenv("ORACLE23AI_DB", "vector")
# ORACLE23AI_USER = os.getenv("ORACLE23AI_USER", "vector")
# ORACLE23AI_PASSWORD = os.getenv("ORACLE23AI_PASSWORD", "vector")
# ORACLE23AI_SERVICE_NAME = os.getenv("ORACLE23AI_SERVICE_NAME", "")


def get_db_config(host, connection_params):
    return {
        "host": host or "localhost",
        "user": ORACLE23AI_USER,
        "password": ORACLE23AI_PASSWORD,
        "dsn": CS,

        # "port": ORACLE23AI_PORT,
        # "dbname": ORACLE23AI_DB,
        # "user": ORACLE23AI_USER,
        # "password": ORACLE23AI_PASSWORD,
        # "service_name": ORACLE23AI_SERVICE_NAME,

        "autocommit": True,
        **connection_params,
    }
