from .hand import Hand


class Player:
    """
    a presidents player

    contains single cards and hands
    """
    def __init__(self) -> None:
        self._cards = list(range(1, 14))
        self._hands = [Hand()]
