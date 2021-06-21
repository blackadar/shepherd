"""
Handles read and write of persistent Pool and Node ID.
"""
import pathlib
import pickle
import node.constants as const


def write_ids(node_id: int, pool_id: int) -> None:
    """
    Writes content to a memory file for the node
    :param node_id: id that the current node uses
    :param pool_id: pool that the node is a part of
    """
    file_content = (node_id, pool_id)
    with open(const.MEMORY_FILE, 'wb') as f:
        pickle.dump(file_content, f)
        f.close()


def read_ids():
    """
    Reads the content from a file as a tuple and returns the tuple
    :return: node_id, pool_id (or False if no file)
    """
    if not const.MEMORY_FILE.exists():
        return False
    with open(const.MEMORY_FILE, 'rb') as f:
        data = pickle.load(f)
        assert type(data) is tuple and len(data) == 2
        node_id, pool_id = data
        return node_id, pool_id
