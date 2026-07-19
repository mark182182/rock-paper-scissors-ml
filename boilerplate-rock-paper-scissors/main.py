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
learning_games_against_oppoinent: dict[Callable, list[Callable]] = {
    kris: [kris, mrugesh, quincy],
    mrugesh: [kris, mrugesh, abbey, quincy, random_player],
    abbey: [kris, random_player, abbey],
    quincy: [quincy],
    random_player: [random_player],
}

# NOTE: this could be set on a game-by-game basis,
# but currently all games are played for 1000 rounds
Config.NUM_OF_ROUNDS = 1000

# logger.info("-- Starting exploration --")
# for opponent in opponents:
#     Config.CURRENT_OPPONENT = opponent
#     logger.info(f"Playing against {opponent.__name__}")
#     games_to_play: list[Callable] = learning_games_against_oppoinent[opponent]
#     for i, game_to_play in enumerate(games_to_play):
#         if i == len(games_to_play) - 1:
#             Config.END_OF_CURRENT_EXPLORATION = True
#         Config.CURRENT_EXPLORATION_ITERATION = 0
#         play(player, game_to_play, Config.NUM_OF_ROUNDS)
#     Config.END_OF_CURRENT_EXPLORATION = False
# logger.info("Done")

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
