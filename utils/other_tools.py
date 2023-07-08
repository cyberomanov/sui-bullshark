def read_mnemonics(path: str = 'data/mnemonic.txt'):
    with open(path) as file:
        not_empty = [line for line in file.read().splitlines() if line]
    return not_empty


def short_address(address: str) -> str:
    return address[:6] + "..." + address[-4:]
