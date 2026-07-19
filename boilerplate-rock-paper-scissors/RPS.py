# The example function below keeps track of the opponent's history
# and plays whatever the opponent played two plays ago.
# It is not a very good player so you will need to
# change the code to pass the challenge.


import json
import os
import random
from pathlib import Path

from shared import Config

PROJECT_DIR: Path = Path(__file__).parent.absolute()


EXPLORATION_DIR_NAME: str = "exploration_iterations"
EXPLORATION_DIR_PATH: Path = PROJECT_DIR / Path(EXPLORATION_DIR_NAME)
EXPLORATION_FILE_NAME: str = "it_{num}.json"

WIN_MOVE_REWARD: float = 0.4
TIE_MOVE_REWARD: float = 0.1
# we don't want to set this a negative value,
# since we have to encourage playing/exploration
# to have better results in the future
LOSE_MOVE_REWARD: float = 0.01


MOVES: list[str] = ["R", "P", "S"]
WINNING_MOVES: dict[str, str] = {"R": "P", "P": "S", "S": "R"}
# stores the opponent's moves in a table which can be used
# for predicting the future value by storing the Q values
Q_TABLE: dict[str, dict[str, float]] = {
    "RRR": {"R": 0, "P": 0, "S": 0},
    "RRP": {"R": 0, "P": 0, "S": 0},
    "RRS": {"R": 0, "P": 0, "S": 0},
    "RPR": {"R": 0, "P": 0, "S": 0},
    "RPP": {"R": 0, "P": 0, "S": 0},
    "RPS": {"R": 0, "P": 0, "S": 0},
    "RSR": {"R": 0, "P": 0, "S": 0},
    "RSP": {"R": 0, "P": 0, "S": 0},
    "RSS": {"R": 0, "P": 0, "S": 0},
    "PRR": {"R": 0, "P": 0, "S": 0},
    "PRP": {"R": 0, "P": 0, "S": 0},
    "PRS": {"R": 0, "P": 0, "S": 0},
    "PPR": {"R": 0, "P": 0, "S": 0},
    "PPP": {"R": 0, "P": 0, "S": 0},
    "PPS": {"R": 0, "P": 0, "S": 0},
    "PSR": {"R": 0, "P": 0, "S": 0},
    "PSP": {"R": 0, "P": 0, "S": 0},
    "PSS": {"R": 0, "P": 0, "S": 0},
    "SRR": {"R": 0, "P": 0, "S": 0},
    "SRP": {"R": 0, "P": 0, "S": 0},
    "SRS": {"R": 0, "P": 0, "S": 0},
    "SPR": {"R": 0, "P": 0, "S": 0},
    "SPP": {"R": 0, "P": 0, "S": 0},
    "SPS": {"R": 0, "P": 0, "S": 0},
    "SSR": {"R": 0, "P": 0, "S": 0},
    "SSP": {"R": 0, "P": 0, "S": 0},
    "SSS": {"R": 0, "P": 0, "S": 0},
}


def remove_all_exploration_files():
    for filename in os.listdir(EXPLORATION_DIR_PATH):
        os.remove(EXPLORATION_DIR_PATH / filename)


def pick_best_guess_from_q_table(three_moves: str):
    """
    Gets the opponent's guess from the Q_TABLE based on the 3 moves (e.g. RRR)
    """
    possible_gusses = Q_TABLE[three_moves]
    # we need to get the guess with the greatest value
    opponent_guess = max(possible_gusses, key=lambda key: possible_gusses[key])

    return opponent_guess


def load_or_remove_exploration_files():
    if Config.SHOULD_READ_EXPLORATION_FROM_JSON:
        if not Config.IS_EXPLORATION_READ_FROM_JSON:
            print(
                "No exploration and all Q values are 0, loading last exploration iteration from JSON"  # noqa
            )
            Config.IS_EXPLORATION_READ_FROM_JSON = True

            all_exploration_files: list[str] = os.listdir(EXPLORATION_DIR_PATH)
            file_with_max_time: str | None = None
            max_exp_ctime: float = 0
            for exp_file in all_exploration_files:
                ctime_of_exp_file = os.path.getctime(EXPLORATION_DIR_PATH / exp_file)
                if ctime_of_exp_file > max_exp_ctime:
                    max_exp_ctime = ctime_of_exp_file
                    file_with_max_time = exp_file

            assert file_with_max_time, "Expected to have at least 1 exploration file"
            path_to_exp_file: Path = EXPLORATION_DIR_PATH / file_with_max_time
            print(f"Max exploration file is: {path_to_exp_file}")

            exp_file_lines: list[str] = []
            with open(path_to_exp_file, encoding="UTF-8") as exp_file:
                exp_file_lines.extend(exp_file.readlines())

            exp_file_jsonstr: str = "".join(exp_file_lines)

            global Q_TABLE
            Q_TABLE = json.loads(exp_file_jsonstr)
    else:
        if not Config.IS_REMOVE_DONE:
            Config.IS_REMOVE_DONE = True
            print("Removing exploration files")
            remove_all_exploration_files()


def player(prev_play: str, opponent_history: list[str]):
    load_or_remove_exploration_files()

    # prev_play == opponent's previous play! not the player's
    opponent_history.append(prev_play)
    next_player_play: str | None = None

    last_three_moves: list[str] | None = None
    last_three_merged: str | None = None

    # the last three moves should only be empty when all rounds
    # with a given bot ended and we change to a new bot
    if len(opponent_history) >= 3 and "" not in opponent_history[-3:]:
        last_three_moves = opponent_history[-3:]
        last_three_merged = "".join(last_three_moves)

    if prev_play == "":
        print("foo")

    if Config.EXPLORATION_ENABLED:
        if last_three_merged and Config.LAST_GAME_OPPONENT_PLAY:
            current_q_value = Q_TABLE[Config.LAST_GAME_OPPONENT_PLAY][
                opponent_history[-1]
            ]

            next_opponent_guess = pick_best_guess_from_q_table(last_three_merged)

            Config.IS_PREVIOUS_OPPONENT_WIN = False
            winning_move = WINNING_MOVES[opponent_history[-1]]
            # if the player did not win the last time, then it was an opponent win
            if winning_move != Config.LAST_GAME_PLAYER_PLAY:
                Config.IS_PREVIOUS_OPPONENT_WIN = True

            current_reward = LOSE_MOVE_REWARD

            if Config.IS_PREVIOUS_OPPONENT_WIN:
                current_reward = WIN_MOVE_REWARD

            if opponent_history[-1] == Config.LAST_GAME_PLAYER_PLAY:
                current_reward = TIE_MOVE_REWARD

            optimal_future_value = Q_TABLE[last_three_merged][next_opponent_guess]

            # Q new will be: (1-LEARNING_RATE) * current_q_value + LEARNING_RATE * (reward + DISCOUNT_FACTOR * optimal_next_state_value) #noqa
            Q_TABLE[Config.LAST_GAME_OPPONENT_PLAY][opponent_history[-1]] = (
                1 - Config.LEARNING_RATE
            ) * current_q_value + Config.LEARNING_RATE * (
                current_reward + Config.DISCOUNT_FACTOR * optimal_future_value
            )

            next_player_play = WINNING_MOVES[next_opponent_guess]

            # if Config.LEARNING_RATE > 0.009:
            #     Config.LEARNING_RATE -= 0.009
            # if len(opponent_history) == 4000:
            #     print(Config.LEARNING_RATE)
        else:
            # we pick totally at random here, sice the opponent_history
            # does not have enough moves from which we can update the Q_TABLE
            # we could utilize a 2 character (or second-order) Markov chain
            # until we have the necessary values to update
            # the third-order Markov chain in the Q_TABLE,
            # but this would still be sufficient
            # to defeat all opponents in the current game
            next_player_play = MOVES[random.randint(0, 2)]
    else:
        if last_three_merged and Config.LAST_GAME_OPPONENT_PLAY:
            # this has to stay consistent with the exploration,
            # since that is what the "learned" Q_TABLE stores
            next_opponent_guess = pick_best_guess_from_q_table(last_three_merged)
            next_player_play = WINNING_MOVES[next_opponent_guess]
        else:
            # we start explotation at random as noted above
            next_player_play = MOVES[random.randint(0, 2)]

    if Config.EXPLORATION_ENABLED:
        it_file_path: Path = EXPLORATION_DIR_PATH / Path(
            EXPLORATION_FILE_NAME.format(num=Config.CURRENT_EXPLORATION_ITERATION)
        )
        with open(
            it_file_path,
            "x",
            encoding="UTF-8",
        ) as exp_file:
            exp_file.write(json.dumps(Q_TABLE, indent=2))

        # later we want to create a pandas DataFrame.from_dict
        # from the last iteration that will be exploited and pretty print it as a table

    Config.CURRENT_EXPLORATION_ITERATION += 1
    Config.LAST_GAME_PLAYER_PLAY = next_player_play
    Config.LAST_GAME_OPPONENT_PLAY = last_three_merged

    return next_player_play
