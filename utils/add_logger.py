from sys import stderr

from loguru import logger

LOG_OUTPUT = "./log/stargaze.log"
LOG_ROTATION = "50 MB"


def add_logger(log_output: str = LOG_OUTPUT, log_rotation: str = LOG_ROTATION, version: str = 'v1.0'):
    logger.remove()
    logger.add(
        stderr,
        format="<bold><blue>{time:HH:mm:ss}</blue> | <level>{level}</level> | <level>{message}</level></bold>"
    )
    logger.add(sink=log_output, rotation=log_rotation)

    print(
        "┌ ----------------------------------------------- ┐\n"
        "|                  SUI-GAME  {sv}                 |\n"
        "| ----------------------------------------------- |\n"
        "|            with love by @cyberomanov            |\n"
        "└ ----------------------------------------------- ┘".format(sv=version)
    )
