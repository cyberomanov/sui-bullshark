import random
import time

from loguru import logger
from pysui.abstracts import SignatureScheme
from pysui.sui.sui_clients.common import handle_result
from pysui.sui.sui_clients.sync_client import SuiClient
from pysui.sui.sui_config import SuiConfig
from pysui.sui.sui_txn import SyncTransaction
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
                  GAME_COINFLIP_TARGET, GAME_JOURNEY_TARGET, GAME_JOURNEY_ARG0, SAVE_QUEST_TARGET)
from datatypes import Arrow, Sui8192MoveResult, SuiTxResult, CoinflipSide, SuiBalance
from utils.other_tools import short_address


def get_list_of_sui_configs(mnemonics: list[str], check_derivation_paths: bool = False) -> list[SuiConfig]:
    list_of_sui_configs = []

    if check_derivation_paths:
        logger.info("collecting 'sui_configs' with checking derivation path, it may take some time.")

    for mnemonic in mnemonics:
        if check_derivation_paths:
            index = 0
            tries = 0
            while True:
                tries += 1
                try:
                    sui_config = SuiConfig.user_config(rpc_url=sui_rpc)
                    default_derivation_path = f"m/44'/784'/{index}'/0'/0'"

                    sui_config.recover_keypair_and_address(
                        scheme=SignatureScheme.ED25519,
                        mnemonics=mnemonic,
                        derivation_path=default_derivation_path
                    )
                    sui_config.set_active_address(address=SuiAddress(sui_config.addresses[0]))

                    objects = SuiClient(config=sui_config).get_objects()
                    if len(list(objects.result_data.data)):
                        list_of_sui_configs.append(sui_config)
                        index += 1
                    else:
                        break
                except:
                    if tries > 3:
                        break
                    else:
                        pass

        else:
            sui_config = SuiConfig.user_config(rpc_url=sui_rpc)
            sui_config.recover_keypair_and_address(
                scheme=SignatureScheme.ED25519,
                mnemonics=mnemonic,
                derivation_path=SUI_DEFAULT_DERIVATION_PATH
            )
            sui_config.set_active_address(address=SuiAddress(sui_config.addresses[0]))
            list_of_sui_configs.append(sui_config)

    if check_derivation_paths:
        logger.info(f"{len(list_of_sui_configs)} non-empty wallets has been found from {len(mnemonics)} mnemonics.")

    return list_of_sui_configs


def get_sui_balance(sui_config: SuiConfig) -> SuiBalance:
    tries = 0
    while True:
        tries += 1
        try:
            client = SuiClient(config=sui_config)
            sui_coin_objects: SuiCoinObjects = client.get_gas(address=sui_config.active_address,
                                                              fetch_all=True).result_data

            balance = 0
            for obj in list(sui_coin_objects.data):
                balance += int(obj.balance)

            return SuiBalance(
                int=balance,
                float=round(balance / 10 ** SUI_NATIVE_DENOMINATION, 2)
            )
        except:
            if tries <= 3:
                time.sleep(3)
            else:
                return SuiBalance(
                    int=0,
                    float=0
                )


def init_transaction(sui_config: SuiConfig, merge_gas_budget: bool = False) -> SyncTransaction:
    return SyncTransaction(
        client=SuiClient(sui_config),
        initial_sender=sui_config.active_address,
        merge_gas_budget=merge_gas_budget
    )


def build_and_execute_tx(sui_config: SuiConfig, transaction: SyncTransaction,
                         gas_object: ObjectID = None) -> SuiTxResult:
    build = transaction.inspect_all()
    if build.error:
        return SuiTxResult(
            address=str(sui_config.active_address),
            digest='',
            reason=build.error
        )
    else:
        try:
            if gas_object:
                rpc_result = transaction.execute(use_gas_object=gas_object, gas_budget=SuiString(SUI_GAS_BUDGET))
            else:
                rpc_result = transaction.execute(gas_budget=SuiString(SUI_GAS_BUDGET))
            if rpc_result.result_data:
                if rpc_result.result_data.status == 'success':
                    return SuiTxResult(
                        address=str(sui_config.active_address),
                        digest=rpc_result.result_data.digest
                    )
                else:
                    return SuiTxResult(
                        address=str(sui_config.active_address),
                        digest=rpc_result.result_data.digest,
                        reason=rpc_result.result_data.status
                    )
            else:
                return SuiTxResult(
                    address=str(sui_config.active_address),
                    digest='',
                    reason=str(rpc_result.result_string)
                )
        except Exception as e:
            logger.exception(e)


def execute_move_tx(sui_config: SuiConfig, game_id: str, move: Arrow) -> Sui8192MoveResult:
    transaction = init_transaction(sui_config=sui_config, merge_gas_budget=True)

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
    transaction = init_transaction(sui_config=sui_config, merge_gas_budget=True)

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
    transaction = init_transaction(sui_config=sui_config, merge_gas_budget=True)

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
            SuiArray([SuiInteger(random.randint(1, 255)) for _ in range(16)]),
            split,
            ObjectID(GAME_COINFLIP_ARG5),
        ]
    )
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction)


def create_profile(sui_config: SuiConfig,
                   nickname: str,
                   img_url: str,
                   description: str) -> SuiTxResult:
    transaction = init_transaction(sui_config=sui_config, merge_gas_budget=True)

    transaction.move_call(
        target=SuiString(GAME_JOURNEY_TARGET),
        arguments=[
            ObjectID(GAME_JOURNEY_ARG0),
            SuiString(nickname),
            SuiString(img_url),
            SuiString(description),
            SuiString('')
        ]
    )
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction)


def save_quest(sui_config: SuiConfig,
               profile_addr: str) -> SuiTxResult:
    transaction = init_transaction(sui_config=sui_config, merge_gas_budget=True)

    t1 = random.randint(3500, 4500)
    t2 = t1 + random.randint(100, 500)
    random_dict = '{' + f'"ch":0,"c1":{random.randint(5, 6)},"t1":{t1},"c2":25,"t2":{t2}' + '}'

    transaction.move_call(
        target=SuiString(SAVE_QUEST_TARGET),
        arguments=[
            ObjectID(profile_addr),
            SuiString('Polymedia: Early Adopter'),
            SuiString('https://journey.polymedia.app/img/card_explorer.webp'),
            SuiString('The door to the invisible must be visible'),
            random_dict
        ]
    )
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction)


def get_sui_coin_objects_for_merge(sui_config: SuiConfig):
    gas_coin_objects: SuiCoinObjects = handle_result(SuiClient(sui_config).get_gas(sui_config.active_address,
                                                                                   fetch_all=True))
    zero_coins = [x for x in gas_coin_objects.data if int(x.balance) == 0]
    non_zero_coins = [x for x in gas_coin_objects.data if int(x.balance) > 0]

    richest_coin = max(non_zero_coins, key=lambda x: int(x.balance), default=None)

    if richest_coin:
        non_zero_coins.remove(richest_coin)

    return zero_coins, non_zero_coins, richest_coin


def merge_sui_coins_tx(sui_config: SuiConfig):
    merge_results = []

    zero_coins, non_zero_coins, richest_coin = get_sui_coin_objects_for_merge(sui_config=sui_config)
    if len(zero_coins) and len(non_zero_coins):
        logger.info(f'{short_address(str(sui_config.active_address))} | trying to merge zero_coins.')
        transaction = init_transaction(sui_config=sui_config)
        transaction.merge_coins(merge_to=transaction.gas, merge_from=zero_coins)
        build_result = build_and_execute_tx(
            sui_config=sui_config,
            transaction=transaction,
            gas_object=ObjectID(richest_coin.object_id)
        )
        if build_result:
            merge_results.append(build_result)
            time.sleep(5)
        zero_coins, non_zero_coins, richest_coin = get_sui_coin_objects_for_merge(sui_config=sui_config)

    if len(non_zero_coins):
        logger.info(f'{short_address(str(sui_config.active_address))} | trying to merge non_zero_coins.')
        transaction = init_transaction(sui_config=sui_config)
        transaction.merge_coins(merge_to=transaction.gas, merge_from=non_zero_coins)
        build_result = build_and_execute_tx(
            sui_config=sui_config,
            transaction=transaction,
            gas_object=ObjectID(richest_coin.object_id)
        )
        if build_result:
            merge_results.append(build_result)
            time.sleep(5)

    return merge_results


def merge_sui_coins(sui_config: SuiConfig):
    try:
        results = merge_sui_coins_tx(sui_config=sui_config)
        if results:
            for result in results:
                if result:
                    if result.reason:
                        logger.warning(f'{short_address(result.address)} | MERGE | digest: {result.digest} | '
                                       f'reason: {result.reason}.')
                    else:
                        logger.info(f'{short_address(result.address)} | MERGE | digest: {result.digest}.')
        else:
            logger.info(f'{short_address(str(sui_config.active_address))} | nothing to merge.')
    except:
        pass
