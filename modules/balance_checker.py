import concurrent.futures

from loguru import logger
from pysui import SuiConfig

from utils.sui import get_sui_balance


def single_executor(sui_config: SuiConfig):
    try:
        balance = get_sui_balance(sui_config=sui_config)
        logger.info(f'{str(sui_config.active_address)}: {balance.float} $SUI.')
    except Exception as e:
        logger.exception(e)


def main_balance_executor(sui_configs: list[SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)
