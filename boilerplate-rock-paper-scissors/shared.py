class Config:
    """
    Members of this class may change over time.
    """

    CURRENT_EXPLORATION_ITERATION: int = 0
    IS_PREVIOUS_WIN: bool = False
    DISCOUNT_FACTOR = 0.98
    # the learning rate and decay rate has to be aligned to the number of games played
    # currently set for 4000 games (1000 * 4 matches)
    LEARNING_RATE = 0.6
    LEARNING_RATE_DECAY_RATE = 0.009

    EXPLORATION_ENABLED: int = 1
    """
    Controls the exploration and exploitation.
    """
