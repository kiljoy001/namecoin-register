import aiosqlite
import hashlib
import base64
from pymerkle import BaseMerkleTree
from contextlib import contextmanager


class CustomMerkleTree(BaseMerkleTree):
    """assumes that data is already hashed"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.leaves = []

    def _encode_entry(self, data):
        """assumes that data is already hashed"""
        return data

    def _store_leaf(self, digest):
        """Store new leaf in the internal list"""
        self.leaves.append(digest)
        return len(self.leaves)

    def _get_leaf(self, index):
        """get leaf by index"""
        if 0 < index <= len(self.leaves):
            return self.leaves[index - 1]
        return None

    def _get_leaves(self, offset, width):
        return self.leaves[offset: offset + width]

    def _get_size(self):
        return len(self.leaves)

    def _hash_entry(self, data):
        """Returns the same input, as it assumed it's hashed"""
        return data

    @classmethod
    def init_from_entries(cls, list_of_hashes):
        tree = cls()
        for hashed_item in list_of_hashes:
            tree.leaves.append(hashed_item)
        return tree

    def get_state(self, size=None):
        """Computes the root-hash of the entire tree"""
        if size is None:
            size = self._get_size()
        return self._get_root(0, size)

    def add_leaf(self, value):
        """Method to add new leaf to the tree"""
        self._store_leaf(value)


async def create_new_database(local_copy_location):
    """Creates a new database & table if database does not exist"""
    with get_db_cursor(local_copy_location) as db_cursor:
        db_cursor.execute("CREATE TABLE IF NOT EXISTS addresses_keys (address TEXT, key TEXT, key_hash BLOB, row_hash BLOB)")
    # create sqlite table to store tree roots
        db_cursor.execute("CREATE TABLE IF NOT EXISTS db_roots (table_name TEXT, root BLOB) ")


async def create_hash(data):
    """Hash a string using SHA256"""
    return hashlib.sha256(data.encode('utf-8'),  usedforsecurity=True).digest()


async def insert_keys_into_db(db_location, address, key):
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
        key_tree, row_tree = CustomMerkleTree.init_from_entries(key_hashes), CustomMerkleTree.init_from_entries(row_hashes)
        key_tree_root, row_tree_root = key_tree.get_state(), row_tree.get_state()
        b64_key_root, b64_row_root = base64.b64encode(key_tree_root), base64.b64encode(row_tree_root)
        return {"key_root": b64_key_root, "row_root": b64_row_root}, key_tree, row_tree


async def store_tree_to_table(db_location, tree, table_name):
    """write tree to db to preserve memory space"""
    with tree:
        with get_db_cursor(db_location) as db_cursor:
            db_cursor.execute(f"CREATE TABLE IF NOT EXSITS {table_name} (hash BLOB)")
        for hash_item in tree.leaves:
            db_cursor.execute(f"INSERT INTO {table_name} (hash) VALUES (?)", (hash_item,))


async def update_tree(tree, value):
    """Updates a tree with a new leaf
    :type tree: CustomMerkleTree
    :type value: Sha256 Hash
    """
    tree.add_leaf(value)


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

