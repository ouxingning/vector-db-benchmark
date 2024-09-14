from typing import List, Tuple

import numpy as np
import oracledb

from dataset_reader.base_reader import Query
from engine.base_client.distances import Distance
from engine.base_client.search import BaseSearcher
from engine.clients.oracle23ai.config import get_db_config
from engine.clients.oracle23ai.parser import Oracle23aiConditionParser

from engine.clients.oracle23ai.npconfig import input_type_handler, output_type_handler


class Oracle23aiSearcher(BaseSearcher):
    conn = None
    cur = None
    distance = None
    search_params = {}
    parser = Oracle23aiConditionParser()

    @classmethod
    def init_client(cls, host, distance, connection_params: dict, search_params: dict):
        cls.conn = oracledb.connect(**get_db_config(host, connection_params))
        cls.conn.inputtypehandler = input_type_handler
        cls.conn.outputtypehandler = output_type_handler
        cls.cur = cls.conn.cursor()
        #cls.cur.execute(f"SET hnsw.ef_search = {search_params['config']['hnsw_ef']}")
        # if distance == Distance.COSINE:
        #     cls.query = "SELECT id, embedding <=> %s AS _score FROM items ORDER BY _score LIMIT %s"
        # elif distance == Distance.L2:
        #     cls.query = "SELECT id, embedding <-> %s AS _score FROM items ORDER BY _score LIMIT %s"
        # else:
        #     raise NotImplementedError(f"Unsupported distance metric {cls.distance}")
        if distance == Distance.COSINE:
            cls.query = "SELECT id, VECTOR_DISTANCE(embedding, to_vector(:1), COSINE) AS _score FROM items ORDER BY _score FETCH APPROXIMATE FIRST :2 ROWS ONLY WITH TARGET ACCURACY" # PARAMETERS (efsearch :3)"
        elif distance == Distance.L2:
            cls.query = "SELECT id, VECTOR_DISTANCE(embedding, to_vector(:1), EUCLIDEAN) AS _score FROM items ORDER BY _score FETCH APPROXIMATE FIRST :2 ROWS ONLY WITH TARGET ACCURACY" # PARAMETERS (efsearch :3)"
        elif distance == Distance.DOT:
            cls.query = "SELECT id, VECTOR_DISTANCE(embedding, to_vector(:1), DOT) AS _score FROM items ORDER BY _score FETCH APPROXIMATE FIRST :2 ROWS ONLY WITH TARGET ACCURACY" # PARAMETERS (efsearch :3)"
        else:
            raise NotImplementedError(f"Unsupported distance metric {cls.distance}")
        

    @classmethod
    def search_one(cls, query: Query, top) -> List[Tuple[int, float]]:
        # TODO: Use query.metaconditions for datasets with filtering
        cls.cur.setinputsizes(oracledb.DB_TYPE_VECTOR)
        cls.cur.execute(
            #cls.query, (np.array(query.vector), top), binary=True, prepare=True
            cls.query, [np.array(query.vector), top]
        )
        return cls.cur.fetchall()

    @classmethod
    def delete_client(cls):
        if cls.cur:
            cls.cur.close()
            cls.conn.close()
