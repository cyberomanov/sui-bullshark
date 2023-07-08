from pysui.abstracts import SignatureScheme
from pysui.sui.sui_clients.sync_client import SuiClient
from pysui.sui.sui_clients.transaction import SuiTransaction
from pysui.sui.sui_config import SuiConfig
from pysui.sui.sui_types import SuiAddress, SuiString, SuiU64, ObjectID

from data import (SUI_DEFAULT_DERIVATION_PATH,
                  GAME_8192_MAKE_MOVE_TARGET,
                  SUI_GAS_BUDGET,
                  SUI_MAINNET_RPC,
                  GAME_8192_MINT_PRICE,
                  GAME_8192_CREATE_TARGET,
                  GAME_8192_MINT_GAME_ADDRESS)
from datatypes import Arrow, Sui8192MoveResult, Sui8192CreateResult


def get_list_of_sui_configs(mnemonics: list[str]) -> list[SuiConfig]:
    list_of_sui_configs = []
    for mnemonic in mnemonics:
        sui_config = SuiConfig.user_config(rpc_url=SUI_MAINNET_RPC)
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


def execute_move(sui_config: SuiConfig, game_id: str, move: Arrow) -> Sui8192MoveResult:
    transaction = init_transaction(sui_config=sui_config)

    transaction.move_call(
        target=SuiString(GAME_8192_MAKE_MOVE_TARGET),
        arguments=[
            ObjectID(game_id),
            SuiU64(move.value)
        ],
    )
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


def mint_game(sui_config: SuiConfig) -> Sui8192CreateResult | None:
    transaction = init_transaction(sui_config=sui_config)

    split = transaction.split_coin(
        coin=transaction.gas,
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
    rpc_result = transaction.execute(gas_budget=SuiString(SUI_GAS_BUDGET))
    if rpc_result.result_data.status == 'success':
        return Sui8192CreateResult(
            address=str(sui_config.active_address),
            digest=rpc_result.result_data.digest,
        )
    else:
        return Sui8192CreateResult(
            address=str(sui_config.active_address),
            digest=rpc_result.result_data.digest,
            reason=rpc_result.result_data.status
        )
