# This entrypoint file to be used in development. Start by reading README.md
import logging
import sys
from logging import Logger

from RPS import player
from RPS_game import abbey, kris, mrugesh, play, quincy
from shared import Config

logging.basicConfig(
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger: Logger = logging.getLogger(__name__)


# logger.info("-- Starting exploration --")
# play(player, random_player, 1000)
# play(player, abbey, 1000)
# play(player, kris, 1000)
# play(player, random_player, 1000)
# play(player, mrugesh, 1000)
# play(player, abbey, 1000)
# play(player, quincy, 1000)
# logger.info("Done")

Config.SHOULD_READ_EXPLORATION_FROM_JSON = True

Config.EXPLORATION_ENABLED = False

logger.info("-- Starting exploitation --")
logger.info("Playing against Kris")
play(player, kris, 1000)
logger.info("Playing against Mrugesh")
play(player, mrugesh, 1000)
logger.info("Playing against Abbey")
play(player, abbey, 1000)
logger.info("Playing against Quincy")
play(player, quincy, 1000)

# Uncomment line below to play interactively against a bot:
# play(human, abbey, 20, verbose=True)

# Uncomment line below to play against a bot that plays randomly:
# play(human, random_player, 1000)


# Uncomment line below to run unit tests automatically
# main(module='test_module', exit=False)
