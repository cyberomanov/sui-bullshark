import random

from loguru import logger
from pysui.abstracts import SignatureScheme
from pysui.sui.sui_clients.common import handle_result
from pysui.sui.sui_clients.sync_client import SuiClient
from pysui.sui.sui_clients.transaction import SuiTransaction
from pysui.sui.sui_config import SuiConfig
from pysui.sui.sui_txresults.single_tx import SuiCoinObjects
from pysui.sui.sui_types import SuiString, SuiU64, ObjectID, SuiArray, SuiU8, SuiInteger
from pysui.sui.sui_types.address import SuiAddress
from pysui.sui.sui_types.bcs import Argument

from config import sui_rpc
from data import (SUI_DEFAULT_DERIVATION_PATH,
                  GAME_8192_MAKE_MOVE_TARGET,
                  SUI_GAS_BUDGET,
                  GAME_8192_MINT_PRICE,
                  GAME_8192_CREATE_TARGET,
                  GAME_8192_MINT_GAME_ADDRESS,
                  SUI_NATIVE_DENOMINATION,
                  GAME_COINFLIP_ARG5,
                  GAME_COINFLIP_TARGET)
from datatypes import Arrow, Sui8192MoveResult, SuiTxResult, CoinflipSide
from utils import short_address


def get_list_of_sui_configs(mnemonics: list[str]) -> list[SuiConfig]:
    list_of_sui_configs = []
    for mnemonic in mnemonics:
        sui_config = SuiConfig.user_config(rpc_url=sui_rpc)
        sui_config.recover_keypair_and_address(
            scheme=SignatureScheme.ED25519,
            mnemonics=mnemonic,
            derivation_path=SUI_DEFAULT_DERIVATION_PATH
        )
        sui_config.set_active_address(address=SuiAddress(sui_config.addresses[0]))
        list_of_sui_configs.append(sui_config)
    return list_of_sui_configs


def init_transaction(sui_config: SuiConfig) -> SuiTransaction:
    return SuiTransaction(
        client=SuiClient(sui_config),
        initial_sender=sui_config.active_address
    )


def build_and_execute_tx(sui_config: SuiConfig, transaction: SuiTransaction) -> SuiTxResult:
    build = transaction.inspect_all()
    if build.error:
        return SuiTxResult(
            address=str(sui_config.active_address),
            digest='',
            reason=build.error
        )
    else:
        rpc_result = transaction.execute(gas_budget=SuiString(SUI_GAS_BUDGET))
        if rpc_result.result_data.status == 'success':
            return SuiTxResult(
                address=str(sui_config.active_address),
                digest=rpc_result.result_data.digest,
            )
        else:
            return SuiTxResult(
                address=str(sui_config.active_address),
                digest=rpc_result.result_data.digest,
                reason=rpc_result.result_data.status
            )


def execute_move_tx(sui_config: SuiConfig, game_id: str, move: Arrow) -> Sui8192MoveResult:
    transaction = init_transaction(sui_config=sui_config)

    transaction.move_call(
        target=SuiString(GAME_8192_MAKE_MOVE_TARGET),
        arguments=[
            ObjectID(game_id),
            SuiU64(move.value)
        ],
    )

    build = transaction.inspect_all()
    if build.error:
        return Sui8192MoveResult(
            address=str(sui_config.active_address),
            digest='',
            move=move,
            reason=build.error
        )
    else:
        rpc_result = transaction.execute(gas_budget=SuiString(SUI_GAS_BUDGET))
        if rpc_result.result_data.status == 'success':
            return Sui8192MoveResult(
                address=str(sui_config.active_address),
                digest=rpc_result.result_data.digest,
                move=move
            )
        else:
            return Sui8192MoveResult(
                address=str(sui_config.active_address),
                digest=rpc_result.result_data.digest,
                move=move,
                reason=rpc_result.result_data.status
            )


def mint_game_tx(sui_config: SuiConfig) -> SuiTxResult:
    transaction = init_transaction(sui_config=sui_config)

    split = transaction.split_coin(
        coin=Argument("GasCoin"),
        amounts=[GAME_8192_MINT_PRICE]
    )
    move_vector = transaction.make_move_vector(
        items=[split]
    )
    transaction.move_call(
        target=SuiString(GAME_8192_CREATE_TARGET),
        arguments=[
            ObjectID(GAME_8192_MINT_GAME_ADDRESS),
            move_vector
        ],
    )
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction)


def play_coinflip_tx(sui_config: SuiConfig,
                     associated_kiosk_addr: str,
                     bullshark_addr: str,
                     coinflip_side: CoinflipSide,
                     bet_amount: int) -> SuiTxResult:
    transaction = init_transaction(sui_config=sui_config)

    bet_amount_in_dec = int(bet_amount * 10 ** SUI_NATIVE_DENOMINATION)
    split = transaction.split_coin(
        coin=transaction.gas,
        amounts=[bet_amount_in_dec]
    )

    transaction.move_call(
        target=SuiString(GAME_COINFLIP_TARGET),
        arguments=[
            ObjectID(associated_kiosk_addr),
            SuiAddress(bullshark_addr),
            SuiU8(coinflip_side.value),
            SuiArray([SuiInteger(random.randint(0, 255)) for _ in range(16)]),
            split,
            ObjectID(GAME_COINFLIP_ARG5),
        ]
    )
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction)


def merge_sui_coins_tx(sui_config: SuiConfig):
    transaction = init_transaction(sui_config=sui_config)

    e_coins: SuiCoinObjects = handle_result(SuiClient(sui_config).get_gas(sui_config.active_address))
    if len(e_coins.data) > 1:
        transaction.merge_coins(merge_to=transaction.gas, merge_from=e_coins.data[1:])
        return build_and_execute_tx(sui_config=sui_config, transaction=transaction)


def merge_sui_coins(sui_config: SuiConfig):
    try:
        result = merge_sui_coins_tx(sui_config=sui_config)
        if result:
            if result.reason:
                logger.warning(f'{short_address(result.address)} | MERGE | digest: {result.digest} | '
                               f'reason: {result.reason}.')
            else:
                logger.info(f'{short_address(result.address)} | MERGE | digest: {result.digest}')
    except:
        pass
