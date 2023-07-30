import json
import random

import requests
from random_username.generate import generate_username

from data import SUI_NATIVE_DENOMINATION
from datatypes.nickname import NicknameResponse
from datatypes.sui import SuiBalance


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


def get_balance_to_transfer(balance: SuiBalance, value_to_leave_in_sui: float) -> SuiBalance:
    value_to_leave_in_sui_int = int(value_to_leave_in_sui * 10 ** SUI_NATIVE_DENOMINATION)

    balance_to_transfer_float = round((balance.int - value_to_leave_in_sui_int) * 0.999 / 10 ** SUI_NATIVE_DENOMINATION,
                                      random.randint(2, 4))
    balance_to_transfer_int = int(balance_to_transfer_float * 10 ** SUI_NATIVE_DENOMINATION)

    return SuiBalance(
        int=balance_to_transfer_int,
        float=balance_to_transfer_float,
    )
