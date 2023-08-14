import subprocess
from fastapi import HTTPException
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def execute_namecoin_command(*args):
    try:
        response = subprocess.check_output(["namecoin.cli", *args]).decode('utf-8')
        return response.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing namecoin command:{e}")
        error_text = "Error executing command"
        logger.error(error_text)
        raise HTTPException(status_code=400, detail=error_text)
