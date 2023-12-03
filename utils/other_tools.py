import base64
import json
import random
import time

import requests
from loguru import logger
from pysui import SuiConfig
from random_username.generate import generate_username
from twocaptcha import TwoCaptcha

from config import two_captcha_api_key
from data import SUI_DENOMINATION, TRANSFER_CRINGE_LIMIT, RECAPTCHA_SITEKEY
from datatypes.nickname import NicknameResponse
from datatypes.signature import SignatureResponse
from datatypes.sui import SuiBalance


def read_file(path: str = 'data/mnemonic.txt'):
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
    value_to_leave_in_sui_int = int(value_to_leave_in_sui * 10 ** SUI_DENOMINATION)
    if balance.int > TRANSFER_CRINGE_LIMIT:
        balance_to_transfer_float = round((TRANSFER_CRINGE_LIMIT - value_to_leave_in_sui_int) *
                                          random.uniform(0.5, 0.999) / 10 ** SUI_DENOMINATION,
                                          random.randint(2, 4))
        balance_to_transfer_int = int(balance_to_transfer_float * 10 ** SUI_DENOMINATION)
    else:
        balance_to_transfer_float = round(
            (balance.int - value_to_leave_in_sui_int) * 0.999 / 10 ** SUI_DENOMINATION,
            random.randint(2, 4))
        balance_to_transfer_int = int(balance_to_transfer_float * 10 ** SUI_DENOMINATION)

    return SuiBalance(
        int=balance_to_transfer_int,
        float=balance_to_transfer_float,
    )


def get_sui_balance_object_from_range(min_amount: float, max_amount: float,
                                      num_of_zero_after_decimal_point: int = 2,
                                      denomination: int = None) -> SuiBalance:
    random_amount_float = random.uniform(min_amount, max_amount)
    rounded_float = round(random_amount_float, num_of_zero_after_decimal_point)
    if denomination:
        rounded_int = int(rounded_float * 10 ** denomination)
    else:
        rounded_int = int(rounded_float * 10 ** SUI_DENOMINATION)
    return SuiBalance(
        int=rounded_int,
        float=rounded_float,
    )


def get_random_account_cluster(sui_configs: list[SuiConfig], randomize: bool = False) -> list[SuiConfig]:
    if randomize:
        sui_configs_len = len(sui_configs)

        min_accs_to_remove = int(0.05 * sui_configs_len)
        max_accs_to_remove = int(0.5 * sui_configs_len)

        accs_to_remove = random.sample(sui_configs, random.randint(min_accs_to_remove, max_accs_to_remove))
        return [element for element in sui_configs if element not in accs_to_remove]
    else:
        return sui_configs


def get_signature(address: str, quest_id: int = 3):
    captcha = get_recaptcha_answer(
        url="https://quests.mystenlabs.com/",
        sitekey=RECAPTCHA_SITEKEY,
        api_key=two_captcha_api_key
    )

    if captcha:
        url = 'https://quests.mystenlabs.com/api/trpc/redeem?batch=1'
        data = {
            "0":
                {
                    "address": address,
                    "questId": quest_id,
                    "captcha": captcha["code"]
                }
        }

        response = requests.post(url=url, json=data)
        if response.status_code == 500:
            return False, 'no more rewards'
        else:
            return SignatureResponse.parse_obj(json.loads(response.content)[0])
    else:
        return False, 'captcha error'


def get_recaptcha_answer(url: str, sitekey: str, api_key: str):
    while True:
        try:
            config = {
                'apiKey': api_key,
                'defaultTimeout': 120,
                'recaptchaTimeout': 600,
                'pollingInterval': 10,
            }
            solver = TwoCaptcha(**config)
            return solver.recaptcha(sitekey=sitekey, url=url)
        except Exception as e:
            if e.args[0] == 'ERROR_ZERO_BALANCE':
                logger.error(f'2captcha: [{api_key}] has zero balance.')
                return False
            else:
                logger.exception(e)
                time.sleep(1)


def encode_signature(signature: str) -> list:
    signature_bytes = base64.b64decode(signature)
    return list(signature_bytes)
