import requests


async def upload_to_ipfs(file_path):
    """
    Uploads file to IPFS network
    :param file_path: string path to file that needs to be uploaded
    :return: str hash of IPFS
    """
    api_url = 'http://127.0.0.1:5001/api/v0/'
    with open(file_path, 'rb') as file:
        response = requests.post(f"{api_url}/add", files={'file': file})
        if response.status_code == 200:
            ipfs_hash = response.json()['Hash']
            pin_url = f'{api_url}/pin/add?arg={ipfs_hash}'
            pin_response = requests.post(pin_url)
            if pin_response.status_code == 200:
                return ipfs_hash
            else:
                return None
        else:
            return None


async def get_peer_count_for_ipfs_hosted_file(ipfs_hash):
    api_url = 'http://127.0.0.1:5001/api/v0/'
    response = requests.post(f"{api_url}/dht/findprove?arg={ipfs_hash}")
    peers = [peer for peer in response.iter_lines()]
    return len(peers)