class Config:
    """
    Members of this class may change over time.
    """

    CURRENT_EXPLORATION_ITERATION: int = 0
    IS_PREVIOUS_OPPONENT_WIN: bool = False
    DISCOUNT_FACTOR = 0.998
    # the learning rate and decay rate has to be aligned to the number of games played
    # currently set for 4000 games (1000 * 4 matches)
    LEARNING_RATE = 0.74
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
