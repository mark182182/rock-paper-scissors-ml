# The example function below keeps track of the opponent's history and plays whatever the opponent played two plays ago. It is not a very good player so you will need to change the code to pass the challenge.


# create all permutations of rock paper and scissors in a map and assign a zeroes for them, which will be updated later by the Q value
from math import ceil
import json
import os
import random
from pathlib import Path

from shared import Config

PROJECT_DIR: Path = Path(__file__).parent.absolute()


EXPLORATION_DIR_NAME: str = "exploration_iterations"
EXPLIRATION_DIR_PATH: Path = PROJECT_DIR / Path(EXPLORATION_DIR_NAME)
EXPLORATION_FILE_NAME: str = "it_{num}.json"

WIN_MOVE_REWARD: float = 0.3
# we don't want to set this a negative value, since we have to encourage playing/exploration
# to have better results in the future
LOSE_MOVE_REWARD: float = 0.2


MOVES: list[str] = ["R", "P", "S"]
WINNING_MOVES: dict[str, str] = {"R": "P", "P": "S", "S": "R"}
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
    for filename in os.listdir(EXPLIRATION_DIR_PATH):
        os.remove(EXPLIRATION_DIR_PATH / filename)


if Config.EXPLORATION_ENABLED:
    print("Removing exploration files")
    remove_all_exploration_files()


def pick_best_guess_from_q_table(last_three_merged, prev_play, updated_q_value):
    Q_TABLE[last_three_merged][prev_play] = updated_q_value

    possible_gusses = Q_TABLE[last_three_merged]
    # we need to get the guess with the greatest value
    guess = max(possible_gusses, key=lambda key: possible_gusses[key])

    return guess


def ceil(value_to_ceil, ceil_target):
    if value_to_ceil > ceil_target:
        return ceil_target
    else:
        return value_to_ceil


def player(prev_play: str, opponent_history: list[str] = []):
    opponent_history.append(prev_play)
    guess: str | None = None

    Config.IS_PREVIOUS_WIN = False
    if len(opponent_history) > 0 and opponent_history[-1] != "":
        winning_move = WINNING_MOVES[opponent_history[-1]]
        if prev_play == winning_move:
            Config.IS_PREVIOUS_WIN = True

    last_three_moves: list[str] = opponent_history[-3:]

    # the last three moves should only be empty when all rounds with a given bot ended and we change to a new bot
    if Config.EXPLORATION_ENABLED:
        if len(opponent_history) >= 3 and "" not in last_three_moves:
            last_three_merged: str = "".join(last_three_moves)
            current_q_value = Q_TABLE[last_three_merged][prev_play]
            # we need to calculate the optimal future value
            optimal_future_value = 1

            current_reward = LOSE_MOVE_REWARD

            if Config.IS_PREVIOUS_WIN:
                current_reward = WIN_MOVE_REWARD

            # TODO: need to decrease learning_rate gradually

            # Q new will be: (1-LEARNING_RATE) * current_q_value + LEARNING_RATE * (reward + DISCOUNT_FACTOR * optimal_future_value)
            updated_q_value = (
                1 - Config.LEARNING_RATE
            ) * current_q_value + Config.LEARNING_RATE * (
                current_reward + Config.DISCOUNT_FACTOR * optimal_future_value
            )

            updated_q_value = ceil(updated_q_value, 1)

            guess = pick_best_guess_from_q_table(
                last_three_merged, prev_play, updated_q_value
            )
        else:
            # we pick totally at random here, sice the opponent_history does not have enough moves from which we can update the Q_TABLE
            # we could utilize a 2 character (or second-order) Markov chain until we have the necessary values to update the third-order Markov chain in the Q_TABLE, but this would still be sufficient to defeat all opponents in the current game
            guess = MOVES[random.randint(0, 2)]
    else:
        if len(opponent_history) >= 3 and "" not in last_three_moves:
            last_three_merged: str = "".join(last_three_moves)
            current_q_value = Q_TABLE[last_three_merged][prev_play]
            guess = pick_best_guess_from_q_table(
                last_three_merged, prev_play, current_q_value
            )
        else:
            # we start explotation at random as noted above
            guess = MOVES[random.randint(0, 2)]

    if Config.EXPLORATION_ENABLED:
        it_file_path: Path = EXPLIRATION_DIR_PATH / Path(
            EXPLORATION_FILE_NAME.format(num=Config.CURRENT_EXPLORATION_ITERATION)
        )
        with open(
            it_file_path,
            "x",
            encoding="UTF-8",
        ) as exp_file:
            exp_file.write(json.dumps(Q_TABLE, indent=2))

        # later we want to create a pandas DataFrame.from_dict from the last iteration that will be exploited and pretty print it as a table

    Config.CURRENT_EXPLORATION_ITERATION += 1

    return guess
