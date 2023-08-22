import json

import requests
from loguru import logger

from data import SUI_DENOMINATION, USDC_DENOMINATION
from datatypes import SuiBalance
from datatypes.coingecko import SuiPrice


def get_sui_price() -> float:
    response = requests.get(url="https://api.coingecko.com/api/v3/simple/price?ids=sui&vs_currencies=usd")
    try:
        response_parsed = SuiPrice.parse_obj(json.loads(response.content))
        return response_parsed.sui.usd
    except Exception as e:
        logger.exception(e)
        return 0


def get_minimum_usdc_to_receive(sui_amount: SuiBalance, sui_price: float) -> int:
    usdc_amount_float = sui_amount.float * sui_price * 0.9
    return int(usdc_amount_float * 10 ** USDC_DENOMINATION)


def get_minimum_sui_to_receive(usdc_amount: SuiBalance, sui_price: float) -> int:
    sui_amount_float = usdc_amount.float / sui_price * 0.9
    return int(sui_amount_float * 10 ** SUI_DENOMINATION)
