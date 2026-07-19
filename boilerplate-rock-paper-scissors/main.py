# This entrypoint file to be used in development. Start by reading README.md
import logging
import sys
from collections.abc import Callable
from logging import Logger

from RPS import player
from RPS_game import abbey, kris, mrugesh, play, quincy, random_player
from shared import Config

logging.basicConfig(
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger: Logger = logging.getLogger(__name__)

opponents: list[Callable] = [kris, mrugesh, abbey, quincy, random_player]

# defines which games to play against a given opponent for learning the
# strategy against them
learning_games_against_oppoinent: dict[Callable, int] = {
    kris: Config.NUM_OF_ROUNDS,
    mrugesh: Config.NUM_OF_ROUNDS,
    abbey: Config.NUM_OF_ROUNDS * 2,
    quincy: Config.NUM_OF_ROUNDS,
    random_player: int(Config.NUM_OF_ROUNDS / 10),
}

# NOTE: this could be set on a game-by-game basis,
# but currently all games are played for 1000 rounds

logger.info("-- Starting exploration --")
for opponent in learning_games_against_oppoinent:
    Config.CURRENT_OPPONENT = opponent
    logger.info(f"Playing against {opponent.__name__}")
    Config.END_OF_CURRENT_EXPLORATION = True
    Config.CURRENT_EXPLORATION_ITERATION = 0
    num_of_rounds: int = learning_games_against_oppoinent[opponent]
    Config.NUM_OF_ROUNDS = num_of_rounds
    play(player, opponent, num_of_rounds)
    Config.END_OF_CURRENT_EXPLORATION = False
logger.info("Done")

Config.SHOULD_READ_EXPLORATION_FROM_JSON = True

Config.EXPLORATION_ENABLED = False

logger.info("-- Starting exploitation --")
for opponent in opponents:
    Config.CURRENT_OPPONENT = opponent
    Config.IS_EXPLORATION_READ_FROM_JSON = False
    logger.info(f"Playing against {opponent.__name__}")
    play(player, opponent, Config.NUM_OF_ROUNDS)

# Uncomment line below to play interactively against a bot:
# play(human, abbey, 20, verbose=True)

# Uncomment line below to play against a bot that plays randomly:
# play(human, random_player, 1000)


# Uncomment line below to run unit tests automatically
# main(module='test_module', exit=False)
