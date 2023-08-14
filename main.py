from fastapi import FastAPI
from src.namecoin_command import execute_namecoin_command
from src.BlockTime.Blockheight import get_blockheight

app = FastAPI()


@app.post("/name_new/")
async def name_new(name: str):
    response = execute_namecoin_command("name_new", name)
    return {"response": response}


@app.post("/name_firstupdate/")
async def name_firstupdate(name: str, rand: str, txid: str, value: str):
    response = execute_namecoin_command("name_firstupdate", name, rand, txid, value)
    return {"response": response}


# wallet endpoints - will need security no endpoints for sending funds, only address generation for receiving
@app.post("/get_balance/")
async def get_balance():
    balance: str = execute_namecoin_command("getbalance")
    return {"balance": balance}


@app.post("/generate_address/")
async def generate_address():
    address = execute_namecoin_command("getnewaddress")
    return {"address": address}


@app.post("/get_blockheight/")
async def show_height():
    return get_blockheight()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0 0", port=8000)
