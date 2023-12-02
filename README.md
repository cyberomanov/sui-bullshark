# SUI-QUEST

this script playing human for points in [quests](https://quests.mystenlabs.com/).<br>
[donations are welcome](https://cyberomanov.tech/WTF_donate), if you find this tool helpful.

## Contents
1. [Installation](https://github.com/cyberomanov/sui-bullshark#installation)

## Installation
1. make sure you have installed `python3.10` or newer;
2. setup your `config.py`, `data/mnemonic.txt`, `data/transfer.txt`;
3. install requirements `pip3 install -r requirements.txt`;
4. run the script `python3 quest.py`.
```bash
56. transfer(from="transfer.txt");
57. reward_claim(from="mnemonic.txt");
58. claim_x_transfer(from="transfer.txt");

61. capy_mint(from="mnemonic.txt");
62. balance_checker(from="mnemonic.txt");
63. mnemonic_generator(from="config.py");
```
## Update
1. `cd sui-bullshark`
2. `git fetch && git reset --hard && git pull`
3. `pip3 install -r requirements.txt`
4. `python3 quest.py`.