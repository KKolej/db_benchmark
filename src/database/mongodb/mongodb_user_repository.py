import time
from typing import Dict, List, Tuple, Optional, Union

from pymongo import ASCENDING, WriteConcern

from .mongodb_connection import MongoDBConnection
from ..common.config_manager import ConfigManager
from ..common.repository import Repository
from ..common.index_types import IndexType
from ..utils.logging_config import ProgressLogger


class MongoDBUserRepository(Repository):
    def __init__(
        self,
        connection_str: Optional[str] = None,
        db_name: Optional[str] = None,
        collection_name: Optional[str] = None,
        config_manager: Optional[ConfigManager] = None,
    ):
        cfg = config_manager or ConfigManager()
        self.conn = MongoDBConnection(
            connection_str or cfg.get_mongodb_connection_string(),
            db_name or cfg.get("mongodb_database"),
            cfg,
        )
        with self.conn as c:
            self.collection = c.get_collection(collection_name)
            self.system_profile = c.get_collection("system.profile")

    def _op_time(self, operation_type: str) -> float:
        crud_ops = {
            "insert": {"op": {"$in": ["insert", "command"]}, "command.insert": {"$exists": True}},
            "find": {"op": {"$in": ["query", "getmore", "command"]}, "command.find": {"$exists": True}},
            "update": {"op": {"$in": ["update", "command"]}, "command.update": {"$exists": True}},
            "delete": {"op": {"$in": ["remove", "command"]}, "command.delete": {"$exists": True}},
        }

        if operation_type not in crud_ops:
            raise ValueError("operation_type must be one of: insert, find, update, delete")

        query = {"$and": [{"$or": [crud_ops[operation_type]]}]}
        latest = self.system_profile.find_one(query, sort=[("ts", -1)])
        if not latest:
            raise Exception("Nie znaleziono operacji.")

        lsid = latest.get("command", {}).get("lsid")
        if not lsid:
            return latest.get("millis", 0)

        cursor = self.system_profile.find({
            "command.lsid": lsid,
            "op": {"$in": ["query", "getmore", "insert", "update", "remove", "command"]}
        })

        i = sum(op.get("millis", 0) for op in cursor)
        return i


    def clear_collection(self) -> bool:
        self.collection.drop()
        return True

    def verify_empty_collection(self) -> bool:
        db = self.collection.database
        if self.collection_name not in db.list_collection_names():
            return True
        if self.collection.count_documents({}):
            return False
        idx_names = [i["name"] for i in self.collection.list_indexes()]
        return idx_names in ([], ["_id_"])

    def setup_profiling(self) -> None:
        db = self.collection.database
        db.command("profile", 0)
        db["system.profile"].drop()
        db.command("profile", 2, slowms=0)

    def create_users_bulk(self, docs: List[Dict]) -> Tuple[List[str], float]:
        self.setup_profiling()

        res = self.collection.with_options(write_concern=WriteConcern(w=1)).insert_many(docs, ordered=True)

        op_time = self._op_time('insert')
        return [str(_id) for _id in res.inserted_ids], op_time

    def get_all_users(self, client_id: int = None) -> Tuple[List[Dict], float]:
        self.setup_profiling()
        flt = {"client_id": client_id}
        q = self.collection.find(flt)
        result = list(q)
        op_time = self._op_time('find')

        return result, op_time

    def _create_idx(self, spec, name) -> bool:
        try:
            self.collection.create_index(spec, name=name)
            return True
        except Exception as err:
            ProgressLogger.error(f"index {name} error: {err}")
            return False

    def ensure_foreign_key_index(self) -> bool:
        return self._create_idx([("client_id", ASCENDING)], "client_id_index")

    def create_indexes(self, index_type: IndexType, collection_name: str) -> bool:
        mapper = {
            IndexType.FOREIGN_KEY.value: self.ensure_foreign_key_index,
        }
        fn = mapper.get(index_type)
        return fn() if fn else False

    def close(self) -> None:
        self.conn.client.close()
