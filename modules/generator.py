import datetime
import os

from loguru import logger
from pysui import SuiConfig
from pysui.abstracts import SignatureScheme

from config import sui_rpc, mnemonic_number_to_generate


def generator_print_divider(path: str):
    with open(path, 'a') as file:
        file.write(f'{datetime.datetime.now()}\n')


def generator_print_out(path: str, text: str):
    with open(path, 'a') as file:
        file.write(f'{text}\n')


def main_generator():
    try:
        generate_log_path = 'log/generate/'

        sui_config = SuiConfig.user_config(rpc_url=sui_rpc)
        if not os.path.exists(generate_log_path):
            os.makedirs(generate_log_path)

        for num in range(mnemonic_number_to_generate):
            mnemonic, address = sui_config.create_new_keypair_and_address(SignatureScheme.ED25519)
            logger.info(f'#{num + 1} | {address} | {mnemonic}')

            generator_print_out(path=f'{generate_log_path}/mnemonic.txt', text=mnemonic)
            generator_print_out(path=f'{generate_log_path}/address.txt', text=str(address))
            generator_print_out(path=f'{generate_log_path}/address_x_mnemonic.txt', text=f'{str(address)}:{mnemonic}')

        generator_print_divider(path=f'{generate_log_path}/mnemonic.txt')
        generator_print_divider(path=f'{generate_log_path}/address.txt')
        generator_print_divider(path=f'{generate_log_path}/address_x_mnemonic.txt')

        logger.success(f"results in './{generate_log_path}...'.")
    except Exception as e:
        logger.exception(e)
