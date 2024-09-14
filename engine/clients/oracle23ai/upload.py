from typing import List

import numpy as np
import oracledb

from dataset_reader.base_reader import Record
from engine.base_client import IncompatibilityError
from engine.base_client.distances import Distance
from engine.base_client.upload import BaseUploader
from engine.clients.oracle23ai.config import get_db_config

from engine.clients.oracle23ai.npconfig import input_type_handler, output_type_handler


class Oracle23aiUploader(BaseUploader):
    # DISTANCE_MAPPING = {
    #     Distance.L2: "vector_l2_ops",
    #     Distance.COSINE: "vector_cosine_ops",
    # }
    DISTANCE_MAPPING = {
        Distance.L2: "EUCLIDEAN",
        Distance.COSINE: "COSINE",
        Distance.DOT: "DOT",
    }
    conn = None
    cur = None
    upload_params = {}

    @classmethod
    def init_client(cls, host, distance, connection_params, upload_params):
        cls.conn = oracledb.connect(**get_db_config(host, connection_params))
        cls.conn.inputtypehandler = input_type_handler
        cls.conn.outputtypehandler = output_type_handler
        cls.cur = cls.conn.cursor()
        cls.upload_params = upload_params

    @classmethod
    def upload_batch(cls, batch: List[Record]):
        ids, vectors = [], []
        for record in batch:
            ids.append(record.id)
            vectors.append(record.vector)

        vectors = np.array(vectors)
        # Copy is faster than insert
        # with cls.cur.copy(
        #     "COPY items (id, embedding) FROM STDIN WITH (FORMAT BINARY)"
        # ) as copy:
        #     copy.set_types(["integer", "vector"])
        #     for i, embedding in zip(ids, vectors):
        #         copy.write_row((i, embedding))
        for i, embedding in zip(ids, vectors):
            data = [[i, embedding]]
            cls.cur.executemany("insert into items values (:1, :2)", data)

    @classmethod
    def post_upload(cls, distance):
        try:
            hnsw_distance_type = cls.DISTANCE_MAPPING[distance]
        except KeyError:
            raise IncompatibilityError(f"Unsupported distance metric: {distance}")

        # cls.conn.execute("SET max_parallel_workers = 128")
        # cls.conn.execute("SET max_parallel_maintenance_workers = 128")
        # cls.conn.execute(
        #     f"CREATE INDEX ON items USING hnsw (embedding {hnsw_distance_type}) WITH (m = {cls.upload_params['hnsw_config']['m']}, ef_construction = {cls.upload_params['hnsw_config']['ef_construct']})"
        # )

        # cls.conn.execute(
        #     f"""
        #         CREATE VECTOR INDEX hnsw_index ON items (embedding) 
        #         ORGANIZATION INMEMORY NEIGHBOR GRAPH DISTANCE {hnsw_distance_type}
        #         WITH TARGET ACCURACY {str(int(cls.upload_params['hnsw_config']['precision'] * 100))} 
        #         PARAMETERS (type HNSW, neighbors {cls.upload_params['hnsw_config']['m']}, efConstruction {cls.upload_params['hnsw_config']['ef_construct']})
        #         PARALLEL {cls.upload_params['hnsw_config']['parallel']}
        #     """
        # )
        cls.conn.execute(
            f"""
                CREATE VECTOR INDEX hnsw_index ON items (embedding) 
                ORGANIZATION INMEMORY NEIGHBOR GRAPH DISTANCE {hnsw_distance_type}
                WITH TARGET ACCURACY {str(int(0.92 * 100))} 
                PARAMETERS (type HNSW, neighbors {cls.upload_params['hnsw_config']['m']}, efConstruction {cls.upload_params['hnsw_config']['ef_construct']})
                PARALLEL 8
            """
        )

        return {}

    @classmethod
    def delete_client(cls):
        if cls.cur:
            cls.cur.close()
            cls.conn.close()
