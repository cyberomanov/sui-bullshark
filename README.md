# SUI-8192

this script plays in [sui8192](https://sui8192.ethoswallet.xyz/), [coinflip](https://desuicoinflip.io/) and [journey](https://journey.polymedia.app/) for points in [quests](https://quests.mystenlabs.com/).<br>
[donations are welcome](https://cyberomanov.tech/WTF_donate), if you find this tool helpful.

## Contents
1. [Installation](https://github.com/cyberomanov/brc20-checker#installation)

## Installation
1. make sure you have installed `python3.10` or newer.
2. setup your `config.py` and `data/mnemonic.txt`;
3. install requirements `pip3 install -r requirements.txt`
4. run the script `python3 8192.py` to play **8192** or `python3 coinflip.py` to play **coinflip** or `python3 journey.py` to play **journey**.
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
```bash
18:22:50 | INFO | loaded addresses:
18:22:50 | INFO | ------------------------------------------------------------------
18:22:50 | INFO | 0xe1a0...b61e
18:22:50 | INFO | ------------------------------------------------------------------
18:22:57 | INFO | 0xe1a0...b61e | COIN_MERGE | digest: 3rap28SGGvgBmK8znGZ4EFq1GsJjQMxFyA9ecGbFX3Ym
18:23:07 | INFO | 0xe1a0...b61e | HEADS | digest: CW7giReVvPs7YMxQXy1FD1YghCjpTifz5Y8SRv45BxGU
18:23:07 | INFO | 0xe1a0...b61e | sleep: 95s.
18:24:54 | INFO | 0xe1a0...b61e | TAILS | digest: 95sSPEnUmLyKD41e9YZy8uTWLMbfwt4nHsE88eTi85UA
18:24:54 | INFO | 0xe1a0...b61e | sleep: 161s.
18:27:46 | INFO | 0xe1a0...b61e | HEADS | digest: GjZywbJyE42eUoTpBwL6ScaPg5EUbL2BJb8GpbuiLZiV
18:27:46 | INFO | 0xe1a0...b61e | sleep: 176s.
18:30:48 | INFO | 0xe1a0...b61e | COIN_MERGE | digest: HSYZhf49fC11mBpVWSz5WvvqP76XRR89MDL4gx1hBr6s
18:30:57 | INFO | 0xe1a0...b61e | HEADS | digest: 9wqAhdPQGHmFe6b79HYihrGMsdjdoWrLteghNY75WxLn
18:30:57 | INFO | 0xe1a0...b61e | sleep: 75s.
18:32:12 | SUCCESS | 0xe1a0...b61e | has played 4 games.
```
```bash
17:33:36 | INFO | loaded addresses for journey:
17:33:51 | INFO | 0xe851...71ad | create_profile | digest: 8w18R8KzvuLgfoVrsgBEvtb8ME4dF9Uj4ksBU82sXvUG | sleep: 14s.
17:33:53 | INFO | 0xeb61...7275 | create_profile | digest: CiicAxu1xj4YHoKzitTsgN1otC75hdGnKQzRKT4ZcHUB | sleep: 9s.
17:34:08 | INFO | 0xeb61...7275 | save_quest | digest: 8qdLBNi1y8GYfnbSfSrCsUqUh4qFGc9rkPsBgjYA7VUc | sleep: 12s.
17:34:11 | INFO | 0xe851...71ad | save_quest | digest: 8F2dGi5MZLpu7cXwtp4BmRYJFe6mYpMWhfkzUFuho1tF | sleep: 10s.
```
## Update
1. `cd sui-bullshark`
2. `git fetch && git reset --hard && git pull`
3. `pip3 install -r requirements.txt`
4. `python3 8192.py` | `python3 coinflip.py` | `python journey.py`