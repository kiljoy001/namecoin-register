import logging
import subprocess

from fastapi import FastAPI, HTTPException, Depends

app = FastAPI()


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def execute_namecoin_command(*args):
    try:
        response = subprocess.check_output(["namecoin.cli", *args]).decode('utf-8')
        return response.strip()
    except subprocess.CalledProcessError as e:
        error_text = f"Error executing namecoin command {e.output.decode('utf-8')}"
        logger.error(error_text)
        raise HTTPException(status_code=400, detail=error_text)


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0 0", port=8000)

