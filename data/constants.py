GAME_8192_MAIN_ADDRESS = '0x225a5eb5c580cb6b6c44ffd60c4d79021e79c5a6cea7eb3e60962ee5f9bc6cb2'
GAME_8192_MAKE_MOVE_TARGET = f'{GAME_8192_MAIN_ADDRESS}::game_8192::make_move'
GAME_8192_CREATE_TARGET = f'{GAME_8192_MAIN_ADDRESS}::game_8192::create'
GAME_8192_CREATE_ARG = f'{GAME_8192_MAIN_ADDRESS}::game_8192::Game8192Maintainer'
GAME_8192_MINT_GAME_ADDRESS = '0x1d6d6770b9929e9d8233b31348f035a2a552d8427ae07d6413d1f88939f3807f'
GAME_8192_MINT_PRICE = 200_000_000

GAME_COINFLIP_MAIN_ADDRESS = '0xdf01804f7fd9c01f747b3e08f21db5e8071790a1494d450766660ccd3d9fa1ba'
GAME_COINFLIP_TARGET = f'{GAME_COINFLIP_MAIN_ADDRESS}::coin_flip::start_game_with_bullshark'
GAME_COINFLIP_ARG5 = '0xbb7708b6e690aa57bfac4af1f7a520c51365bb82e47376e2795e262699b07a02'

GAME_JOURNEY_MAIN_ADDRESS = '0x57138e18b82cc8ea6e92c3d5737d6078b1304b655f59cf5ae9668cc44aad4ead'
GAME_JOURNEY_TARGET = f'{GAME_JOURNEY_MAIN_ADDRESS}::profile::create_profile'
GAME_JOURNEY_ARG0 = '0xd6eb0ca817dfe0763af9303a6bea89b88a524844d78e657dc25ed8ba3877deac'
SAVE_QUEST_MAIN_ADDRESS = '0x7c423c0f1ab19c99155c24e98fdb971453b699c90ab579b23b38103060ea26db'
SAVE_QUEST_TARGET = f'{SAVE_QUEST_MAIN_ADDRESS}::journey::save_quest'

SUI_RESERVE_COIN_TYPE = '0xefe8b36d5b2e43728cc323298626b83177803521d195cfb11e15b910e892fddf::reserve::MarketCoin<0x2::sui::SUI>'
USDC_COIN_TYPE = '0x5d4b302506645c37ff133b98c4b50a5ae14841659738d6d733d59d0d217a93bf::coin::COIN'

NAVI_LENDING_SUI_MAIN_ADDRESS = '0xd92bc457b42d48924087ea3f22d35fd2fe9afdf5bdfe38cc51c0f14f3282f6d5'
NAVI_LENDING_SUI_TARGET = f'{NAVI_LENDING_SUI_MAIN_ADDRESS}::lending::deposit'
NAVI_BORROW_SUI_TARGET = f'{NAVI_LENDING_SUI_MAIN_ADDRESS}::lending::borrow'
NAVI_REPAY_SUI_TARGET = f'{NAVI_LENDING_SUI_MAIN_ADDRESS}::lending::repay'
NAVI_LENDING_SUI_ARG0 = '0x0000000000000000000000000000000000000000000000000000000000000006'
NAVI_LENDING_SUI_ARG1 = '0xbb4e2f4b6205c2e2a2db47aeb4f830796ec7c005f88537ee775986639bc442fe'
NAVI_LENDING_SUI_ARG2 = '0x96df0fce3c471489f4debaaa762cf960b3d97820bd1f3f025ff8190730e958c5'
NAVI_LENDING_SUI_ARG6 = '0xaaf735bf83ff564e1b219a0d644de894ef5bdc4b2250b126b2a46dd002331821'
NAVI_BORROW_SUI_ARG0 = '0x1568865ed9a0b5ec414220e8f79b3d04c77acc82358f6e5ae4635687392ffbef'
NAVI_REPAY_FEE = 1_000

SCALLOP_LENDING_SUI_MAIN_ADDRESS = '0xc05a9cdf09d2f2451dea08ca72641e013834baef3d2ea5fcfee60a9d1dc3c7d9'
SCALLOP_LENDING_SUI_TARGET = f'{SCALLOP_LENDING_SUI_MAIN_ADDRESS}::mint::mint'
SCALLOP_LENDING_SUI_ARG1 = '0x07871c4b3c847a0f674510d4978d5cf6f960452795e8ff6f189fd2088a3f6ac7'
SCALLOP_LENDING_SUI_ARG2 = '0xa757975255146dc9686aa823b7838b507f315d704f428cbadad2f4ea061939d9'
SCALLOP_LENDING_SUI_ARG3 = '0x0000000000000000000000000000000000000000000000000000000000000006'
SCALLOP_WITHDRAW_SUI_MAIN_ADDRESS = '0xefe8b36d5b2e43728cc323298626b83177803521d195cfb11e15b910e892fddf'
SCALLOP_WITHDRAW_SUI_TARGET = f'{SCALLOP_WITHDRAW_SUI_MAIN_ADDRESS}::redeem::redeem'
SCALLOP_LENDING_SUI_ARG0 = '0x07871c4b3c847a0f674510d4978d5cf6f960452795e8ff6f189fd2088a3f6ac7'

TURBOS_SUI_USDC_MAIN_ADDRESS = '0xeb9210e2980489154cc3c293432b9a1b1300edd0d580fe2269dd9cda34baee6d'
TURBOS_SUI_USDC_MAIN_TARGET = f'{TURBOS_SUI_USDC_MAIN_ADDRESS}::swap_router::swap_a_b'
TURBOS_SUI_USDC_ARG1 = '0x5eb2dfcdd1b15d2021328258f6d5ec081e9a0cdcfa9e13a0eaeb9b5f7505ca78'
TURBOS_SUI_USDC_ARG2 = '0xf1cf0e81048df168ebeb1b8030fad24b3e0b53ae827c25053fff0779c1445b6f'

KRIYA_SUI_USDC_MAIN_ADDRESS = '0xa0eba10b173538c8fecca1dff298e488402cc9ff374f8a12ca7758eebe830b66'
KRIYA_SUI_USDC_MAIN_TARGET = f'{KRIYA_SUI_USDC_MAIN_ADDRESS}::spot_dex::swap_token_y'
KRIYA_USDC_SUI_MAIN_TARGET = f'{KRIYA_SUI_USDC_MAIN_ADDRESS}::spot_dex::swap_token_x'
KRIYA_SUI_USDC_POOL = '0x5af4976b871fa1813362f352fa4cada3883a96191bb7212db1bd5d13685ae305'

TRANSFER_CRINGE_LIMIT = 50_000_000_000

SUI_DENOMINATION = 9
USDC_DENOMINATION = 6
SUI_DEFAULT_DERIVATION_PATH = "m/44'/784'/0'/0'/0'"

SUI_DEFAULT_GAS_BUDGET = 500_000_000
SUI_TRANSFER_GAS_BUDGET = 1_000_000
SUI_MINIMUM_TX_BUDGET = 780_000

VERSION = 'v2.0'
