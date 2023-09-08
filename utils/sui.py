import random
import time

from loguru import logger
from pysui.abstracts import SignatureScheme
from pysui.sui.sui_clients.common import handle_result
from pysui.sui.sui_clients.sync_client import SuiClient
from pysui.sui.sui_config import SuiConfig
from pysui.sui.sui_txn import SyncTransaction
from pysui.sui.sui_txresults.single_tx import SuiCoinObjects, SuiCoinObject
from pysui.sui.sui_types import SuiString, SuiU64, ObjectID, SuiArray, SuiU8, SuiInteger
from pysui.sui.sui_types.address import SuiAddress
from pysui.sui.sui_types.bcs import Argument

from config import sui_rpc
from data import *
from datatypes import Arrow, Sui8192MoveResult, SuiTxResult, CoinflipSide, SuiBalance, SuiTransferConfig, SuiTx
from utils.other_tools import short_address


def get_list_of_sui_configs(mnemonics: list[str]) -> list[SuiConfig]:
    list_of_sui_configs = []

    for mnemonic in mnemonics:
        sui_config = SuiConfig.user_config(rpc_url=sui_rpc)
        if '0x' in mnemonic:
            sui_config.add_keypair_from_keystring(keystring={
                'wallet_key': mnemonic,
                'key_scheme': SignatureScheme.ED25519
            })
        else:
            sui_config.recover_keypair_and_address(
                scheme=SignatureScheme.ED25519,
                mnemonics=mnemonic,
                derivation_path=SUI_DEFAULT_DERIVATION_PATH
            )
        sui_config.set_active_address(address=SuiAddress(sui_config.addresses[0]))
        list_of_sui_configs.append(sui_config)

    return list_of_sui_configs


def get_list_of_transfer_configs(mnemonics: list[str]) -> list[SuiTransferConfig]:
    list_of_sui_configs = []

    for mnemonic_line in mnemonics:
        mnemonic = mnemonic_line.split(':')[0]
        address = mnemonic_line.split(':')[1]
        sui_config = SuiConfig.user_config(rpc_url=sui_rpc)
        if '0x' in mnemonic:
            sui_config.add_keypair_from_keystring(keystring={
                'wallet_key': mnemonic,
                'key_scheme': SignatureScheme.ED25519
            })
        else:
            sui_config.recover_keypair_and_address(
                scheme=SignatureScheme.ED25519,
                mnemonics=mnemonic,
                derivation_path=SUI_DEFAULT_DERIVATION_PATH
            )
        sui_config.set_active_address(address=SuiAddress(sui_config.addresses[0]))
        list_of_sui_configs.append(SuiTransferConfig(config=sui_config, address=address))

    return list_of_sui_configs


def get_sui_balance(sui_config: SuiConfig, coin_type: SuiString = None, denomination: int = None) -> SuiBalance:
    tries = 0
    while True:
        tries += 1
        try:
            client = SuiClient(config=sui_config)
            if coin_type:
                coin_objects: SuiCoinObjects = client.get_coin(coin_type=coin_type, address=sui_config.active_address,
                                                               fetch_all=True).result_data
            else:
                coin_objects: SuiCoinObjects = client.get_gas(address=sui_config.active_address,
                                                              fetch_all=True).result_data

            balance = 0
            for obj in list(coin_objects.data):
                balance += int(obj.balance)

            if denomination:
                return SuiBalance(
                    int=balance,
                    float=round(balance / 10 ** denomination, 2)
                )
            else:
                return SuiBalance(
                    int=balance,
                    float=round(balance / 10 ** SUI_DENOMINATION, 2)
                )
        except:
            if tries <= 5:
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


def build_and_execute_tx(sui_config: SuiConfig,
                         transaction: SyncTransaction,
                         gas_object: ObjectID = None) -> SuiTxResult:
    # rpc_result = transaction.execute(use_gas_object=gas_object, gas_budget=SUI_DEFAULT_GAS_BUDGET)
    build = transaction.inspect_all()
    gas_used = build.effects.gas_used
    gas_budget = int((int(gas_used.computation_cost) + int(gas_used.non_refundable_storage_fee) +
                      abs(int(gas_used.storage_cost) - int(gas_used.storage_rebate))) * 1.1)

    if build.error:
        return SuiTxResult(
            address=str(sui_config.active_address),
            digest='',
            reason=build.error
        )
    else:
        try:
            if gas_object:
                rpc_result = transaction.execute(use_gas_object=gas_object, gas_budget=str(gas_budget))
            else:
                rpc_result = transaction.execute(gas_budget=str(gas_budget))
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


def independent_merge_sui_coins_tx(sui_config: SuiConfig):
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

    if len(non_zero_coins) > 1:
        logger.info(f'{short_address(str(sui_config.active_address))} | trying to merge non_zero_coins.')
        non_zero_coins.remove(richest_coin)

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


def get_pre_merged_tx(sui_config: SuiConfig, transaction: SyncTransaction) -> SuiTx:
    merge_count = 0

    zero_coins, non_zero_coins, richest_coin = get_sui_coin_objects_for_merge(sui_config=sui_config)
    if len(zero_coins) and len(non_zero_coins):
        merge_count += 1
        transaction.merge_coins(merge_to=transaction.gas, merge_from=zero_coins)
    if len(non_zero_coins) > 1:
        non_zero_coins.remove(richest_coin)
        merge_count += 1
        transaction.merge_coins(merge_to=transaction.gas, merge_from=non_zero_coins)

    return SuiTx(builder=transaction, gas=ObjectID(richest_coin.object_id), merge_count=merge_count)


def transfer_sui_tx(sui_config: SuiConfig, recipient: str, amount: SuiBalance) -> SuiTxResult:
    tx_object = get_pre_merged_tx(sui_config=sui_config, transaction=init_transaction(sui_config=sui_config))
    transaction = tx_object.builder
    # transaction = init_transaction(sui_config=sui_config, merge_gas_budget=True)

    transaction.transfer_sui(
        recipient=SuiAddress(recipient),
        from_coin=transaction.gas,
        amount=amount.int,
    )

    return build_and_execute_tx(sui_config=sui_config, transaction=transaction, gas_object=tx_object.gas)


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
        rpc_result = transaction.execute(gas_budget=SuiString(SUI_DEFAULT_GAS_BUDGET))
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

    bet_amount_in_dec = int(bet_amount * 10 ** SUI_DENOMINATION)
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


def save_quest_tx(sui_config: SuiConfig,
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


def navi_deposit_sui_tx(sui_config: SuiConfig, amount: SuiBalance):
    tx_object = get_pre_merged_tx(sui_config=sui_config, transaction=init_transaction(sui_config=sui_config))
    transaction = tx_object.builder

    split = transaction.split_coin(
        coin=transaction.gas,
        amounts=[amount.int]
    )

    transaction.move_call(
        target=SuiString(NAVI_LENDING_SUI_TARGET),
        arguments=[
            ObjectID(NAVI_LENDING_SUI_ARG0),
            ObjectID(NAVI_LENDING_SUI_ARG1),
            ObjectID(NAVI_LENDING_SUI_ARG2),
            SuiU8(0),
            split,
            SuiU64(amount.int),
            ObjectID(NAVI_LENDING_SUI_ARG6)
        ],
        type_arguments=[
            '0x2::sui::SUI'
        ]
    )
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction, gas_object=tx_object.gas)


def navi_borrow_sui_tx(sui_config: SuiConfig, amount: SuiBalance):
    tx_object = get_pre_merged_tx(sui_config=sui_config, transaction=init_transaction(sui_config=sui_config))
    transaction = tx_object.builder

    transaction.move_call(
        target=SuiString(NAVI_BORROW_SUI_TARGET),
        arguments=[
            ObjectID(NAVI_LENDING_SUI_ARG0),
            ObjectID(NAVI_BORROW_SUI_ARG0),
            ObjectID(NAVI_LENDING_SUI_ARG1),
            ObjectID(NAVI_LENDING_SUI_ARG2),
            SuiU8(0),
            SuiU64(amount.int),
        ],
        type_arguments=[
            '0x2::sui::SUI'
        ]
    )
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction, gas_object=tx_object.gas)


def navi_repay_sui_tx(sui_config: SuiConfig, amount: SuiBalance):
    tx_object = get_pre_merged_tx(sui_config=sui_config, transaction=init_transaction(sui_config=sui_config))
    transaction = tx_object.builder

    split = transaction.split_coin(
        coin=transaction.gas,
        amounts=[amount.int + NAVI_REPAY_FEE]
    )

    transaction.move_call(
        target=SuiString(NAVI_REPAY_SUI_TARGET),
        arguments=[
            ObjectID(NAVI_LENDING_SUI_ARG0),
            ObjectID(NAVI_BORROW_SUI_ARG0),
            ObjectID(NAVI_LENDING_SUI_ARG1),
            ObjectID(NAVI_LENDING_SUI_ARG2),
            SuiU8(0),
            split,
            SuiU64(amount.int + NAVI_REPAY_FEE),
        ],
        type_arguments=[
            '0x2::sui::SUI'
        ]
    )
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction, gas_object=tx_object.gas)


def scallop_deposit_sui_tx(sui_config: SuiConfig, amount: SuiBalance):
    tx_object = get_pre_merged_tx(sui_config=sui_config, transaction=init_transaction(sui_config=sui_config))
    transaction = tx_object.builder

    split = transaction.split_coin(
        coin=transaction.gas,
        amounts=[amount.int]
    )

    default_nested_index = 0
    move_call = transaction.move_call(
        target=SuiString(SCALLOP_LENDING_SUI_TARGET),
        arguments=[
            ObjectID(SCALLOP_LENDING_SUI_ARG1),
            ObjectID(SCALLOP_LENDING_SUI_ARG2),
            Argument(name="NestedResult", value=(default_nested_index + tx_object.merge_count, 0)),
            ObjectID(SCALLOP_LENDING_SUI_ARG3),
        ],
        type_arguments=['0x2::sui::SUI']
    )

    transaction.transfer_objects(
        transfers=[move_call],
        recipient=SuiAddress(str(sui_config.active_address))
    )
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction,
                                gas_object=ObjectID(tx_object.gas.object_id))


def scallop_withdraw_sui_tx(sui_config: SuiConfig, amount: int, merge_list: list[SuiCoinObject]):
    tx_object = get_pre_merged_tx(sui_config=sui_config, transaction=init_transaction(sui_config=sui_config))
    transaction = tx_object.builder

    if len(merge_list) > 1:
        transaction.merge_coins(merge_to=merge_list[0], merge_from=merge_list[1:])
        tx_object.merge_count += 1

    split = transaction.split_coin(
        coin=merge_list[0],
        amounts=[amount]
    )

    transaction.transfer_objects(
        transfers=[merge_list[0]],
        recipient=SuiAddress(str(sui_config.active_address))
    )

    default_nested_index = 0
    move_call = transaction.move_call(
        target=SuiString(SCALLOP_WITHDRAW_SUI_TARGET),
        arguments=[
            ObjectID(SCALLOP_LENDING_SUI_ARG1),
            ObjectID(SCALLOP_LENDING_SUI_ARG2),
            Argument(name="NestedResult", value=(default_nested_index + tx_object.merge_count, 0)),
            ObjectID(SCALLOP_LENDING_SUI_ARG3),
        ],
        type_arguments=['0x2::sui::SUI']
    )

    transaction.transfer_objects(
        transfers=[move_call],
        recipient=SuiAddress(str(sui_config.active_address))
    )
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction,
                                gas_object=ObjectID(tx_object.gas.object_id))


def kriya_swap_tx(sui_config: SuiConfig, amount: int, minimum_received: int, token_from: str = None):
    tx_object = get_pre_merged_tx(sui_config=sui_config, transaction=init_transaction(sui_config=sui_config))
    transaction = tx_object.builder

    if token_from == 'USDC':
        zero_coins, non_zero_coins, richest_coin = get_sui_coin_objects_for_merge(sui_config=sui_config,
                                                                                  coin_type=USDC_COIN_TYPE)

        if len(non_zero_coins + zero_coins) > 1:
            non_zero_coins.remove(richest_coin)
            transaction.merge_coins(merge_to=richest_coin, merge_from=zero_coins + non_zero_coins)

        move_call = transaction.move_call(
            target=SuiString(KRIYA_USDC_SUI_MAIN_TARGET),
            arguments=[
                ObjectID(KRIYA_SUI_USDC_POOL),
                ObjectID(richest_coin.coin_object_id),
                SuiU64(amount),
                SuiU64(minimum_received)
            ],
            type_arguments=[
                '0x5d4b302506645c37ff133b98c4b50a5ae14841659738d6d733d59d0d217a93bf::coin::COIN',
                '0x2::sui::SUI'
            ]
        )
    else:
        split = transaction.split_coin(
            coin=transaction.gas,
            amounts=[amount]
        )

        move_call = transaction.move_call(
            target=SuiString(KRIYA_SUI_USDC_MAIN_TARGET),
            arguments=[
                ObjectID(KRIYA_SUI_USDC_POOL),
                split,
                SuiU64(amount),
                SuiU64(minimum_received)
            ],
            type_arguments=[
                '0x5d4b302506645c37ff133b98c4b50a5ae14841659738d6d733d59d0d217a93bf::coin::COIN',
                '0x2::sui::SUI'
            ]
        )

    transaction.transfer_objects(transfers=[move_call], recipient=sui_config.active_address)
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction, gas_object=tx_object.gas)


def capy_mint_sui_tx(sui_config: SuiConfig):
    tx_object = get_pre_merged_tx(sui_config=sui_config, transaction=init_transaction(sui_config=sui_config))
    transaction = tx_object.builder

    split = transaction.split_coin(
        coin=transaction.gas,
        amounts=[CAPY_MINT_PRICE]
    )

    move_call_1 = transaction.move_call(
        target=SuiString(CAPY_MOVE_CALL_1_TARGET),
        arguments=[]
    )

    default_nested_index = 1
    move_call_2 = transaction.move_call(
        target=SuiString(CAPY_MOVE_CALL_2_TARGET),
        arguments=[
            ObjectID(CAPY_MINT_INPUT_1),
            ObjectID(SCALLOP_LENDING_SUI_ARG3),
            split,
            Argument(name="NestedResult", value=(default_nested_index + tx_object.merge_count, 0)),
            Argument(name="NestedResult", value=(default_nested_index + tx_object.merge_count, 1)),
            ObjectID(CAPY_MINT_INPUT_3),

        ],
        type_arguments=["0xee496a0cc04d06a345982ba6697c90c619020de9e274408c7819f787ff66e1a1::capy::Capy"]
    )

    default_nested_index = 1
    move_call_3 = transaction.move_call(
        target=SuiString(CAPY_MOVE_CALL_3_TARGET),
        arguments=[
            Argument(name="NestedResult", value=(default_nested_index + tx_object.merge_count, 0)),
        ],
        type_arguments=["0x2::kiosk::Kiosk"]
    )

    default_nested_index = 1
    transaction.transfer_objects(
        transfers=[Argument(name="NestedResult", value=(default_nested_index + tx_object.merge_count, 1)), split],
        recipient=SuiAddress(str(sui_config.active_address))
    )
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction,
                                gas_object=ObjectID(tx_object.gas.object_id))


def claim_reward(sui_config: SuiConfig, signature: list):
    tx_object = get_pre_merged_tx(sui_config=sui_config, transaction=init_transaction(sui_config=sui_config))
    transaction = tx_object.builder

    move_call = transaction.move_call(
        target=SuiString(REWARD_CLAIM_TARGET),
        arguments=[
            ObjectID(REWARD_CLAIM_ARG0),
            [SuiU8(x) for x in signature]
        ]
    )

    default_nested_index = 0
    transaction.transfer_objects(
        transfers=[Argument(name="NestedResult", value=(default_nested_index + tx_object.merge_count, 0))],
        recipient=SuiAddress(str(sui_config.active_address))
    )
    return build_and_execute_tx(sui_config=sui_config, transaction=transaction,
                                gas_object=ObjectID(tx_object.gas.object_id))


def get_provided_sui_balance(sui_config: SuiConfig) -> SuiBalance:
    sui_reserve_coin_objects: SuiCoinObjects = SuiClient(config=sui_config).get_coin(
        coin_type=SuiString(SUI_RESERVE_COIN_TYPE),
        fetch_all=True).result_data

    already_provided_int = sum(int(obj.balance) for obj in sui_reserve_coin_objects.data)
    already_provided_float = round(already_provided_int / 10 ** SUI_DENOMINATION, 2)

    return SuiBalance(
        int=already_provided_int,
        float=already_provided_float
    )


def merge_sui_coins(sui_config: SuiConfig):
    try:
        results = independent_merge_sui_coins_tx(sui_config=sui_config)
        if results:
            for result in results:
                if result:
                    if result.reason:
                        logger.warning(f'{short_address(result.address)} | MERGE | digest: {result.digest} | '
                                       f'reason: {result.reason}.')
                    else:
                        logger.info(f'{short_address(result.address)} | MERGE | digest: {result.digest}.')
        else:
            # logger.info(f'{short_address(str(sui_config.active_address))} | nothing to merge.')
            pass
    except:
        pass


def get_sui_coin_objects_for_merge(sui_config: SuiConfig, coin_type: SuiString = None):
    if coin_type:
        gas_coin_objects: SuiCoinObjects = handle_result(SuiClient(sui_config).get_coin(
            coin_type=coin_type,
            address=sui_config.active_address,
            fetch_all=True)
        )
    else:
        gas_coin_objects: SuiCoinObjects = handle_result(SuiClient(sui_config).get_gas(sui_config.active_address,
                                                                                       fetch_all=True))
    zero_coins = [x for x in gas_coin_objects.data if int(x.balance) == 0]
    non_zero_coins = [x for x in gas_coin_objects.data if int(x.balance) > 0]

    richest_coin = max(non_zero_coins, key=lambda x: int(x.balance), default=None)
    return zero_coins, non_zero_coins, richest_coin

# def turbos_swap_tx(sui_config: SuiConfig, pool_addr: str, amount: int):
#     transaction = init_transaction(sui_config=sui_config, merge_gas_budget=True)
#
#     split = transaction.split_coin(
#         coin=transaction.gas,
#         amounts=[amount]
#     )
#
#     transaction.make_move_vector(
#         [Argument(name="NestedResult", value=(0, 0))]
#     )
#
#     transaction.move_call(
#         target=SuiString(TURBOS_SUI_USDC_MAIN_TARGET),
#         arguments=[
#             ObjectID(TURBOS_SUI_USDC_ARG1),
#             split,
#             amount,
#             get_minimum_usdc_to_receive(sui_amount=amount, price=get_sui_price()),
#             457_111_694_183_490_676,
#             True,
#             ObjectID(str(sui_config.active_address)),
#             # u
#             ObjectID(NAVI_LENDING_SUI_ARG0),
#             ObjectID(TURBOS_SUI_USDC_ARG2),
#
#         ],
#         type_arguments=[
#             '0x2::sui::SUI',
#             '0x5d4b302506645c37ff133b98c4b50a5ae14841659738d6d733d59d0d217a93bf::coin::COIN',
#             '0x91bfbc386a41afcfd9b2533058d7e915a1d3829089cc268ff4333d54d6339ca1::fee3000bps::FEE3000BPS'
#         ]
#     )
#
#     return build_and_execute_tx(sui_config=sui_config, transaction=transaction)


# def get_every_event(sui_config: SuiConfig):
#     has_next_page = True
#     next_cursor = None
#     limit = 50
#
#     events = None
#
#     while has_next_page:
#         if next_cursor:
#             latest_events: EventQueryEnvelope = SuiClient(config=sui_config).get_events(
#                 query=SenderEventQuery(sender=sui_config.active_address), limit=limit, cursor=EventID(
#                     event_seq=next_cursor['eventSeq'],
#                     tx_seq=next_cursor['txDigest']
#                 )
#             ).result_data
#         else:
#             latest_events: EventQueryEnvelope = SuiClient(config=sui_config).get_events(
#                 query=SenderEventQuery(sender=sui_config.active_address), limit=limit
#             ).result_data
#         has_next_page = latest_events.has_next_page
#         next_cursor = latest_events.next_cursor
#
#         if events:
#             events.data += latest_events.data
#             # time.sleep(random.randint(3, 5))
#         else:
#             events = latest_events
#
#     return events
