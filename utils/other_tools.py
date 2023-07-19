import json

import requests
from random_username.generate import generate_username

from datatypes.nickname import NicknameResponse


def read_mnemonics(path: str = 'data/mnemonic.txt'):
    with open(path) as file:
        not_empty = [line for line in file.read().splitlines() if line]
    return not_empty


def short_address(address: str) -> str:
    return address[:6] + "..." + address[-4:]


def get_random_username() -> str:
    url = "https://randomuser.me/api/"
    response = requests.get(url=url)
    if response.status_code == 200:
        parsed_response = NicknameResponse.parse_obj(json.loads(response.content))
        return parsed_response.results[0].login.username
    else:
        return generate_username()[0]
