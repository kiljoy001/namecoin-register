import subprocess
import json
from frozendict import frozendict
from src.BlockTime.blockheight import wait_for_blocks
from src.namecoin_command import execute_namecoin_command

COMMANDS = frozendict(
    {
        "generate_ca_key": (
            "openssl",
            "genpkey",
            "-algorithm",
            "RSA",
            "-out",
            "ca_private_key.pem",
        ),
        "generate_ca_cert": (
            "openssl",
            "req",
            "-new",
            "-x509",
            "-key",
            "ca_private_key.pem",
            "-out",
            "ca_certificate.pem",
            "-days",
            "365",
        ),
        "generate_key": (
            "openssl",
            "genpkey",
            "-algorithm",
            "RSA",
            "-out",
            "{cert_name}_private_key.pem",
        ),
        "generate_cert": (
            "openssl",
            "req",
            "-new",
            "-key",
            "{cert_name}_private_key.pem",
            "-out",
            "{cert_name}.csr",
        ),
        "sign_cert": (
            "openssl",
            "x509",
            "-req",
            "-in",
            "{cert_name}.csr",
            "-CA",
            "ca_certificate.pem",
            "-CAkey",
            "ca_private_key.pem",
            "-CAcreateserial",
            "-out",
            "{cert_name}_certificate.pem",
            "-days",
            "365",
        ),
        "validate_cert": {
            "openssl",
            "x509",
            "-in",
            "{cert_path}",
            "-noout",
        },
    }
)


def run_command(command_type, cert_name=None):
    if command_type not in COMMANDS:
        raise ValueError("Invalid command type")
    command = tuple(
        arg.replace("{cert_name}", cert_name) if "{cert_name}" in arg else arg
        for arg in COMMANDS[command_type]
    )
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed with error: {stderr.decode()}")
    return stdout.decode()


def generate_x509_cert(cert_name):
    run_command("generate_key", cert_name=cert_name)
    run_command("generate_cert", cert_name=cert_name)
    run_command("sign_cert", cert_name=cert_name)


def generate_ca():
    run_command("generate_ca_key")
    run_command("generate_ca_cert")


def is_valid_certificate(cert_path):
    try:
        run_command("validate_cert", cert_name=cert_path)
        return True
    except Exception:
        return False


async def name_firstupdate(name: str, rand: str, txid: str, value: str):
    response = execute_namecoin_command("name_firstupdate", name, rand, txid, value)
    return {"response": response}


async def register_new_domain(domain_name, on_chain_value):
    # check balance
    min_balance = 0.02
    balance = execute_namecoin_command("getbalance")
    if balance[balance] > min_balance:
        response = execute_namecoin_command("namenew")
        clean_response = json.loads(response["response"])
        txid = clean_response[0]
        rand_hex = clean_response[1]
        second_response = await wait_for_blocks(12, name_firstupdate, domain_name, rand_hex, txid, on_chain_value)
        return second_response

