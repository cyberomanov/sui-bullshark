import concurrent.futures

from loguru import logger
from pysui import SuiConfig

from utils import get_bullshark_id, get_associated_kiosk
from utils.sui import get_sui_balance


def single_executor(sui_config: SuiConfig):
    try:
        balance = get_sui_balance(sui_config=sui_config)

        capy_addr = None
        bullshark_addr = None

        associated_kiosk_addr = get_associated_kiosk(address=str(sui_config.active_address))
        if associated_kiosk_addr:
            kiosk_dynamic_fields = get_bullshark_id(kiosk_addr=associated_kiosk_addr).result.data
            for field in kiosk_dynamic_fields:
                if 'bullshark' in str(field.objectType).lower():
                    bullshark_addr = field.objectId
                elif 'capy' in str(field.objectType).lower():
                    capy_addr = field.objectId

            if capy_addr:
                logger.info(f'{str(sui_config.active_address)}: {balance.float} $SUI | CAPY.')
            elif bullshark_addr:
                logger.info(f'{str(sui_config.active_address)}: {balance.float} $SUI | BULLSHARK.')
            else:
                logger.warning(f'{str(sui_config.active_address)}: {balance.float} $SUI | no any SUIFREN.')
        else:
            logger.warning(f'{str(sui_config.active_address)}: {balance.float} $SUI | no any SUIFREN.')
    except Exception as e:
        logger.exception(e)


def main_balance_executor(sui_configs: list[SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)
