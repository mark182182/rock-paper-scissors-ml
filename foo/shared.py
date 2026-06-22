class Config:
    """
    Members of this class may change over time.
    """

    CURRENT_EXPLORATION_ITERATION: int = 0
    IS_PREVIOUS_WIN: bool = False
    LEARNING_RATE = 0.5
    DISCOUNT_FACTOR = 0.94

    EXPLORATION_ENABLED: int = 1
    """
    Controls the exploration and exploitation.
    """
