from collections.abc import Callable


class Config:
    """
    Members of this class may change over time.
    """

    END_OF_CURRENT_EXPLORATION: bool = False
    CURRENT_EXPLORATION_ITERATION: int = 0
    IS_PREVIOUS_OPPONENT_WIN: bool = False
    DISCOUNT_FACTOR = 0.998
    # the learning rate and decay rate has to be aligned to the number of games played
    # currently set for 1000 games
    LEARNING_RATE = 0.8
    LEARNING_RATE_DECAY_RATE = 0.009

    SHOULD_READ_EXPLORATION_FROM_JSON: bool = False
    IS_EXPLORATION_READ_FROM_JSON: bool = False
    IS_REMOVE_DONE: bool = False
    EXPLORATION_ENABLED: int = 1
    """
    Controls the exploration and exploitation.
    """

    # this is the the previous - 1 game
    LAST_GAME_OPPONENT_PLAY: str | None = None
    LAST_GAME_PLAYER_PLAY: str | None = None

    NUM_OF_ROUNDS: int = 100
    PREVIOUS_OPPONENT: Callable | None = None
    CURRENT_OPPONENT: Callable
