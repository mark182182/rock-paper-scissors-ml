# The example function below keeps track of the opponent's history
# and plays whatever the opponent played two plays ago.
# It is not a very good player so you will need to
# change the code to pass the challenge.

import copy
import json
import logging
import os
import random
from logging import Logger
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from shared import Config

logger: Logger = logging.getLogger(__name__)

PROJECT_DIR: Path = Path(__file__).parent.absolute()

# TODO: Fixes to make in order:
# - Make sure random exploration only happens during learning
# - Random moves calculate the reward, but never update the Q-table. Random moves should also update the Q-table
# - Make sure to track the player's moves instead of the opponent's moves, as the opponents react to the player's move, so the player can exploit the Q-learning table in a better way


EXPLORATION_DIR_NAME: str = "exploration_iterations"
EXPLORATION_DIR_PATH: Path = PROJECT_DIR / Path(EXPLORATION_DIR_NAME)
EXPLORATION_FILE_NAME: str = "it_{num}.json"

STRATEGIES_DIR_NAME: str = "strategies"
STRATEGIES_DIR_PATH: Path = PROJECT_DIR / Path(STRATEGIES_DIR_NAME)
STRATEGIES_FILE_NAME: str = "{name}.json"

PLOTS_DIR_NAME: str = "plots"
PLOTS_DIR_PATH: Path = PROJECT_DIR / Path(PLOTS_DIR_NAME)

# TODO: provide descriptions for each property

WIN_MOVE_REWARD: float = 1.0
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
ORIGINAL_Q_TABLE = copy.deepcopy(Q_TABLE)

num_of_games_played_plot_x: list[int] = []

exploration_rate_plot_y: list[int] = []
explorations_plot_y: list[int] = []

prev_iteration_plot_x: list[int] = []
prev_it_reward_plot_y: list[float] = []


def _remove_all_exploration_files():
    for filename in os.listdir(EXPLORATION_DIR_PATH):
        os.remove(EXPLORATION_DIR_PATH / filename)


def _create_plot_base(
    filename: str,
    plot_x: list,
    plot_x_label: str,
    plot_y: list,
    plot_y_label: str,
    plot_fn: Callable,
):
    fig = Figure(figsize=(5, 4), dpi=120)

    ax = fig.add_subplot()
    ax.set_title(filename)
    ax.set_xlabel(plot_x_label)
    ax.set_ylabel(plot_y_label)
    ax.grid(True, axis="x")
    plot_fn(ax, plot_x, plot_y)

    fig.savefig(PLOTS_DIR_PATH / Path(f"{filename}.png"))


def _create_plot(
    filename: str, plot_x: list, plot_x_label: str, plot_y: list, plot_y_label: str
) -> None:
    _create_plot_base(
        filename,
        plot_x,
        plot_x_label,
        plot_y,
        plot_y_label,
        lambda ax, plot_x, plot_y: ax.plot(plot_x, plot_y),
    )


def _create_scatter(
    filename: str, plot_x: list, plot_x_label: str, plot_y: list, plot_y_label: str
):
    _create_plot_base(
        filename,
        plot_x,
        plot_x_label,
        plot_y,
        plot_y_label,
        lambda ax, plot_x, plot_y: ax.scatter(plot_x, plot_y, s=10, edgecolors="red"),
    )


def _create_bar(filename: str, x_label: str, y_label: tuple, bar_x: list, xerror: list):
    fig, ax = plt.subplots()

    # TODO: add error bar array here

    ax.barh(y_label, bar_x, xerr=xerror, align="center")  # todo add xerr=error here
    ax.yaxis.set_inverted(True)  # arrange data from top to bottom
    ax.set_xlabel(x_label)
    ax.set_title(filename)
    ax.grid(True, axis="x")

    fig.savefig(PLOTS_DIR_PATH / Path(f"{filename}.png"))


def _pick_best_guess_from_q_table(three_moves: str):
    """
    Gets the opponent's guess from the Q_TABLE based on the 3 moves (e.g. RRR)
    """
    possible_gusses = Q_TABLE[three_moves]
    # we need to get the guess with the greatest value
    opponent_guess = max(possible_gusses, key=lambda key: possible_gusses[key])

    return opponent_guess


def _get_current_reward_for_prev_play(opponent_history: list[str]) -> float:
    if len(opponent_history) >= 0 and "" not in opponent_history[-1:]:
        prev_iteration_plot_x.append(Config.CURRENT_GAME_ITERATION)

        Config.IS_PREVIOUS_OPPONENT_WIN = False
        previous_winning_move = WINNING_MOVES[opponent_history[-1]]
        # if the player did not win the last time, then it was an opponent win
        if opponent_history[-1] == Config.LAST_GAME_PLAYER_PLAY:
            # both played the same: tie
            current_reward = TIE_MOVE_REWARD
            prev_it_reward_plot_y.append(TIE_MOVE_REWARD)
        elif previous_winning_move != Config.LAST_GAME_PLAYER_PLAY:
            # player did not play the winning hand: lose
            Config.IS_PREVIOUS_OPPONENT_WIN = True
            current_reward = LOSE_MOVE_REWARD
            prev_it_reward_plot_y.append(LOSE_MOVE_REWARD)
        else:
            # player plyed the winning hand: win
            Config.IS_PREVIOUS_OPPONENT_WIN = False
            current_reward = WIN_MOVE_REWARD
            prev_it_reward_plot_y.append(WIN_MOVE_REWARD)

        return current_reward


def _load_or_remove_exploration_files():
    if Config.SHOULD_READ_EXPLORATION_FROM_JSON:
        if not Config.IS_EXPLORATION_READ_FROM_JSON:
            logger.info(
                "No exploration and all Q values are 0, loading strategy from JSON"  # noqa
            )
            Config.CURRENT_GAME_ITERATION = 0
            Config.CURRENT_EXPLORATION_RATE = Config.BASE_EXPLORATION_RATE
            Config.IS_EXPLORATION_READ_FROM_JSON = True

            all_stretegy_files: list[str] = os.listdir(STRATEGIES_DIR_PATH)
            current_opponent: str = Config.CURRENT_OPPONENT.__name__

            strategy_file_against_opponent: Path | None = None
            for strategy_file in all_stretegy_files:
                if STRATEGIES_FILE_NAME.format(name=current_opponent) == strategy_file:
                    strategy_file_against_opponent = STRATEGIES_DIR_PATH / Path(
                        strategy_file
                    )
                    break

            if not strategy_file_against_opponent:
                logger.info(
                    f"""Expected strategy against {current_opponent},
                    but got only {all_stretegy_files}"""
                )
                exit(1)

            strat_file_lines: list[str] = []
            with open(strategy_file_against_opponent, encoding="UTF-8") as strat_file:
                strat_file_lines.extend(strat_file.readlines())

            strat_file_jsonstr: str = "".join(strat_file_lines)

            global Q_TABLE
            Q_TABLE = json.loads(strat_file_jsonstr)
    else:
        if not Config.IS_REMOVE_DONE:
            Config.IS_REMOVE_DONE = True
            logger.info("Removing exploration files")
            _remove_all_exploration_files()


# used for debug purposes only
def _load_exploration_file():
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
    logger.info(f"Max exploration file is: {path_to_exp_file}")

    exp_file_lines: list[str] = []
    with open(path_to_exp_file, encoding="UTF-8") as exp_file:
        exp_file_lines.extend(exp_file.readlines())

    exp_file_jsonstr: str = "".join(exp_file_lines)

    global Q_TABLE
    Q_TABLE = json.loads(exp_file_jsonstr)


def player(
    prev_play: str,
    opponent_history: list[str] = [],  # noqa
):
    global Q_TABLE
    _load_or_remove_exploration_files()

    if Config.END_OF_CURRENT_EXPLORATION and prev_play == "":
        logger.info(f"Prepared for opponent {Config.CURRENT_OPPONENT.__name__}")

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

    # TODO: add exploration rate that decays over time
    # based on the exploration rate, when exploring the player should go down the Config.EXPLORATION_ENABLED case,
    # otherwise the player should pick from the currently exploited Q_TABLE (_pick_best_guess_from_q_table, same as exploiting without learning)

    # TODO: plot the following in different graphs using matplotlib,
    # both during exploration and exploitation (depending on the properties that exist during exploitation, e.g. learning rate does not):
    # - how the exploration rate changes over time
    # - how the Q_TABLE changes over time based on the rewards
    # - how the player moves change over time
    # - how the opponent moves change over time
    should_pick_randomly: bool = random.random() < Config.CURRENT_EXPLORATION_RATE

    exploration_rate_plot_y.append(Config.CURRENT_EXPLORATION_RATE)
    explorations_plot_y.append(should_pick_randomly)

    if should_pick_randomly:
        next_player_play = MOVES[random.randint(0, 2)]
        # calling this just to record the previous play
        _get_current_reward_for_prev_play(opponent_history)
    elif Config.EXPLORATION_ENABLED:
        if last_three_merged and Config.LAST_GAME_OPPONENT_PLAY:
            current_q_value = Q_TABLE[Config.LAST_GAME_OPPONENT_PLAY][
                opponent_history[-1]
            ]

            next_opponent_guess = _pick_best_guess_from_q_table(last_three_merged)

            current_reward: float = _get_current_reward_for_prev_play(opponent_history)

            optimal_future_value = Q_TABLE[last_three_merged][next_opponent_guess]

            # Q new will be: (1-LEARNING_RATE) * current_q_value + LEARNING_RATE * (reward + DISCOUNT_FACTOR * optimal_next_state_value) #noqa
            Q_TABLE[Config.LAST_GAME_OPPONENT_PLAY][opponent_history[-1]] = (
                1 - Config.LEARNING_RATE
            ) * current_q_value + Config.LEARNING_RATE * (
                current_reward + Config.DISCOUNT_FACTOR * optimal_future_value
            )

            next_player_play = WINNING_MOVES[next_opponent_guess]

            # should never be smaller than the decay rate to always retain
            # some amount of exploration
            if Config.CURRENT_EXPLORATION_RATE > Config.EXPLORATION_RATE_DECAY_RATE:
                Config.CURRENT_EXPLORATION_RATE -= Config.EXPLORATION_RATE_DECAY_RATE
                # logger.info(f"EXPLORATION_RATE: {Config.CURRENT_EXPLORATION_RATE}")
        else:
            # we pick totally at random here, sice the opponent_history
            # does not have enough moves from which we can update the Q_TABLE
            # we could utilize a 2 character (or second-order) Markov chain
            # until we have the necessary values to update
            # the third-order Markov chain in the Q_TABLE,
            # but this would still be sufficient
            # to defeat all opponents in the current game
            next_player_play = MOVES[random.randint(0, 2)]
            # calling this just to record the previous play
            _get_current_reward_for_prev_play(opponent_history)
    else:
        if last_three_merged and Config.LAST_GAME_OPPONENT_PLAY:
            # this has to stay consistent with the exploration,
            # since that is what the "learned" Q_TABLE stores
            next_opponent_guess = _pick_best_guess_from_q_table(last_three_merged)
            next_player_play = WINNING_MOVES[next_opponent_guess]
        else:
            # we start explotation at random as noted above
            next_player_play = MOVES[random.randint(0, 2)]
        # calling this just to record the previous play
        _get_current_reward_for_prev_play(opponent_history)

    Config.CURRENT_GAME_ITERATION += 1
    num_of_games_played_plot_x.append(Config.CURRENT_GAME_ITERATION)
    Config.CURRENT_EXPLORATION_ITERATION += 1
    Config.LAST_GAME_PLAYER_PLAY = next_player_play
    Config.LAST_GAME_OPPONENT_PLAY = last_three_merged

    if Config.EXPLORATION_ENABLED:
        it_file_path: Path = EXPLORATION_DIR_PATH / Path(
            EXPLORATION_FILE_NAME.format(num=Config.CURRENT_EXPLORATION_ITERATION)
        )
        _write_json(it_file_path, Q_TABLE)

        if (
            Config.END_OF_CURRENT_EXPLORATION
            and Config.CURRENT_EXPLORATION_ITERATION == Config.NUM_OF_ROUNDS
        ):
            logger.info(f"Final strategy for {Config.CURRENT_OPPONENT.__name__}")
            strategy_path: Path = STRATEGIES_DIR_PATH / Path(
                STRATEGIES_FILE_NAME.format(name=Config.CURRENT_OPPONENT.__name__)
            )
            # TODO: if the win rate is worse than before, don't write it out
            _write_json(strategy_path, Q_TABLE)

            logger.info("Resetting Q_TABLE for new player")
            Q_TABLE = copy.deepcopy(ORIGINAL_Q_TABLE)

            _create_plot(
                Config.CURRENT_OPPONENT.__name__ + "_exploration_rate",
                num_of_games_played_plot_x,
                "Number of games",
                exploration_rate_plot_y,
                "Exploration Rate",
            )

            _create_scatter(
                Config.CURRENT_OPPONENT.__name__ + "_explorations",
                num_of_games_played_plot_x,
                "Number of games",
                explorations_plot_y,
                "Is Exploring?",
            )

            _create_plot(
                filename=Config.CURRENT_OPPONENT.__name__ + "_reward",
                plot_x=prev_iteration_plot_x,
                plot_x_label="Number of games",
                plot_y=prev_it_reward_plot_y,
                plot_y_label=f"Player reward ({LOSE_MOVE_REWARD}=lose, {TIE_MOVE_REWARD}=tie, {WIN_MOVE_REWARD}=win)",
            )

            _create_bar(
                filename=Config.CURRENT_OPPONENT.__name__ + "_bar_reward",
                x_label="Number of games",
                y_label=("Win", "Tie", "Lose"),
                bar_x=[
                    prev_it_reward_plot_y.count(WIN_MOVE_REWARD),
                    prev_it_reward_plot_y.count(TIE_MOVE_REWARD),
                    prev_it_reward_plot_y.count(LOSE_MOVE_REWARD),
                ],
                xerror=[0, 0, 0],
            )

        # later we want to create a pandas DataFrame.from_dict
        # from the last iteration that will be exploited and pretty print it as a table

    return next_player_play


def _write_json(output_path: Path, payload: Any):
    output_path.unlink(True)

    with open(
        output_path,
        "x",
        encoding="UTF-8",
    ) as output_json_file:
        output_json_file.write(json.dumps(payload, indent=2))
