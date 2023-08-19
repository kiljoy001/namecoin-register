import sqlite3
import hashlib
import base64
from pymerkle import InmemoryTree


async def create_new_database(local_copy_location):
    """Creates a new database & table if database does not exist"""
    connection = sqlite3.connect(local_copy_location)
    db_cursor = connection.cursor()
    db_cursor.execute("CREATE TABLE IF NOT EXISTS addresses_keys (address TEXT, key TEXT, key_hash BLOB, row_hash BLOB)")
    connection.commit()
    connection.close()


async def create_hash(data):
    """Hash a string using SHA256"""
    return hashlib.sha256(data.encode('utf-8'),  usedforsecurity=True).digest()


async def insert_into_db(db_location, address, key):
    """inserts data into the database"""
    connection = sqlite3.connect(db_location)
    db_cursor = connection.cursor()
    key_hash = await create_hash(key)
    row_data = f"{address}{key}"
    row_hash = await create_hash(row_data)
    db_cursor.execute("INSERT INTO addresses_keys (address, key, key_hash, row_hash) VALUES (?,?,?,?)",
                      (address, key, key_hash, row_hash))
    connection.commit()
    connection.close()


async def calculate_merkle_roots(db_location):
    """creates merkle roots for insertion."""
    connection = sqlite3.connect(db_location)
    db_cursor = connection.cursor()
    db_cursor.execute("SELECT key_hash, row_hash FROM addresses_keys")
    hashes = db_cursor.fetchall()
    key_hashes = [item[0] for item in hashes]
    row_hashes = [item[1] for item in hashes]
    key_tree, row_tree = InmemoryTree.init_from_entries(key_hashes), InmemoryTree.init_from_entries(row_hashes)
    key_tree_root, row_tree_root = key_tree.get_state(), row_tree.get_state()
    b64_key_root, b64_row_root = base64.b64encode(key_tree_root), base64.b64encode(row_tree_root)
    return {"key_root": b64_key_root, "row_root": b64_row_root}








