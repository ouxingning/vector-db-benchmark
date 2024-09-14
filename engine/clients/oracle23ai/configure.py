import oracledb

from benchmark.dataset import Dataset
from engine.base_client import IncompatibilityError
from engine.base_client.configure import BaseConfigurator
from engine.base_client.distances import Distance
from engine.clients.oracle23ai.config import get_db_config

from engine.clients.oracle23ai.npconfig import input_type_handler, output_type_handler

class Oracle23aiConfigurator(BaseConfigurator):
    def __init__(self, host, collection_params: dict, connection_params: dict):
        super().__init__(host, collection_params, connection_params)
        self.conn = oracledb.connect(**get_db_config(host, connection_params))
        self.conn.inputtypehandler = input_type_handler
        self.conn.outputtypehandler = output_type_handler
        print("configure connection created")

    def clean(self):
        self.conn.execute(
            "DROP TABLE IF EXISTS items",
        )

    def recreate(self, dataset: Dataset, collection_params):
        # if dataset.config.distance == Distance.DOT:
        #     raise IncompatibilityError

        self.conn.execute(
            f"""CREATE TABLE items (
                id number PRIMARY KEY,
                embedding vector({dataset.config.vector_size}) NOT NULL
            );"""
        )
        # self.conn.execute("ALTER TABLE items ALTER COLUMN embedding SET STORAGE PLAIN")
        self.conn.close()

    def delete_client(self):
        self.conn.close()
