import aiosqlite
import hashlib
import base64
from pymerkle import InmemoryTree
from contextlib import contextmanager


async def create_new_database(local_copy_location):
    """Creates a new database & table if database does not exist"""
    with get_db_cursor(local_copy_location) as db_cursor:
        db_cursor.execute("CREATE TABLE IF NOT EXISTS addresses_keys (address TEXT, key TEXT, key_hash BLOB, row_hash BLOB)")
    # create sqlite table to store tree


async def create_hash(data):
    """Hash a string using SHA256"""
    return hashlib.sha256(data.encode('utf-8'),  usedforsecurity=True).digest()


async def insert_into_db(db_location, address, key):
    """inserts data into the database"""
    with get_db_cursor(db_location) as db_cursor:
        key_hash = await create_hash(key)
        row_data = f"{address}{key}"
        row_hash = await create_hash(row_data)
        db_cursor.execute("INSERT INTO addresses_keys (address, key, key_hash, row_hash) VALUES (?,?,?,?)",
                          (address, key, key_hash, row_hash))


async def calculate_merkle_roots(db_location):
    """creates merkle roots for insertion."""
    with get_db_cursor(db_location) as db_cursor:
        db_cursor.execute("SELECT key_hash, row_hash FROM addresses_keys")
        hashes = db_cursor.fetchall()
        key_hashes = [item[0] for item in hashes]
        row_hashes = [item[1] for item in hashes]
        key_tree, row_tree = InmemoryTree.init_from_entries(key_hashes), InmemoryTree.init_from_entries(row_hashes)
        key_tree_root, row_tree_root = key_tree.get_state(), row_tree.get_state()
        b64_key_root, b64_row_root = base64.b64encode(key_tree_root), base64.b64encode(row_tree_root)
        return {"key_root": b64_key_root, "row_root": b64_row_root}, key_tree, row_tree


async def store_tree_to_table(db_location, tree, table_name):
    """write tree to db to preserve memory space"""
    with tree:
        with get_db_cursor(db_location) as db_cursor:
            db_cursor.execute(f"CREATE TABLE IF NOT EXSITS {table_name} (hash BLOB)")
        for hash_item in tree.leaves:
            db_cursor.execute(f"INSERT INTO {table_name} (hash) VALUES (?)", hash_item)


@contextmanager
async def get_db_cursor(db_location):
    """Abstracts the database creation, connection and cleanup"""
    connection = aiosqlite.connect(db_location)
    db_cursor = connection.cursor()
    try:
        yield db_cursor
    finally:
        await connection.commit()
        await connection.close()


async def check_full_tree(merkle_root, db_location):
    db_root, _, _ = await calculate_merkle_roots(db_location)
    return db_root["row_root"] == merkle_root
