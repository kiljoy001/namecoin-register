import subprocess

COMMANDS = {
    "generate_ca_key": ("openssl", "genpkey", "-algorithm", "RSA", "-out", "ca_private_key.pem"),
    "generate_ca_cert": ("openssl", "req", "-new", "-x509", "-key", "ca_private_key.pem", "-out",
                         "ca_certificate.pem", "-days", "365"),
    "generate_key": ("openssl", "genpkey", "-algorithm", "RSA", "-out", "{cert_name}_private_key.pem"),
    "generate_cert": ("openssl", "req", "-new", "-key", "{cert_name}_private_key.pem", "-out", "{cert_name}.csr"),
    "sign_cert": ("openssl", "x509", "-req", "-in", "{cert_name}.csr", "-CA", "ca_certificate.pem",
                  "-CAkey", "ca_private_key.pem", "-CAcreateserial", "-out", "{cert_name}_certificate.pem",
                  "-days", "365")
}


def run_command(command_type, cert_name=None):
    if command_type not in COMMANDS:
        raise ValueError("Invalid command type")
    command = tuple(arg.replace("{cert_name}", cert_name) if
                    "{cert_name}" in arg else arg for arg in COMMANDS[command_type])
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed with error: {stderr.decode()}")
    return stdout.decode()


def generate_x509_cert(cert_name):
    run_command("generate_key", cert_name=f"{cert_name}_private_key.pem")
    run_command("generate_cert", cert_name=f"{cert_name}.csr")
    run_command("sign_cert", cert_name=f"{cert_name}_certificate.pem")


def generate_ca():
    run_command("generate_ca_key")
    run_command("generate_ca_cert")

