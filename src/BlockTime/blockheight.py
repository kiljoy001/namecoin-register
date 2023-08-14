import asyncio
from src.namecoin_command import execute_namecoin_command


def get_blockheight():
    blockheight = execute_namecoin_command("getblockcount")
    return {"blockheight": blockheight}


async def wait_for_blocks(blocks_to_wait, func_to_call):
    current_height_query = get_blockheight()
    target_block = blocks_to_wait + current_height_query["blockheight"]
    while get_blockheight() < target_block:
        await asyncio.sleep(60)
    await func_to_call()
