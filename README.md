# SUI-8192

this script plays in [sui8192](https://sui8192.ethoswallet.xyz/) for points in [quests](https://quests.mystenlabs.com/).<br>
[donations are welcome](https://cyberomanov.tech/WTF_donate), if you find this tool helpful.

## Contents
1. [Installation](https://github.com/cyberomanov/brc20-checker#installation)

## Installation
1. make sure you have installed `python3.10` or newer.
2. setup your `config.py` and `data/mnemonic.txt`;
3. install requirements `pip3 install -r requirements.txt`
4. run the script `python3 8192.py`
```bash
18:00:09 | INFO | loaded addresses:
18:00:09 | INFO | -------------
18:00:09 | INFO | 0x299a...4b3f
18:00:09 | INFO | 0xe1a0...b61e
18:00:09 | INFO | 0x318a...634b
18:00:09 | INFO | -------------
18:00:10 | SUCCESS | 0x299a...4b3f | played 4 games.
18:00:10 | SUCCESS | 0xe1a0...b61e | played 4 games.
18:00:28 | INFO | 0x318a...634b | digest: 8FxqkMphgDoioaiAW93UXQvEFR4ExAzeabBd9xa3Xvwi
18:00:34 | INFO | 0x318a...634b | current_game_id: 0x10380bb4a184a1568a54d4c478dc83ff10c1b3d5c137f2c3d96b4ba52f08a4dd.
18:00:38 | INFO | 0x318a...634b | LEFT | digest: D9HZ19tY46piK8cDQahsmeaT4ppYc9V8ZhUkqY5uc7z1
18:00:46 | INFO | 0x318a...634b | DOWN | digest: 824KSV1fawU9Sp4abmCWtByj9NHk6geQaYqSRiM7MvUA
```

## Update
1. `cd sui-bullshark`
2. `git fetch && git pull && git reset --hard`
3. `pip3 install -r requirements.txt`
4. `python3 8192.py`