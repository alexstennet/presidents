from uuid import uuid4
from player import Player


class Game:
    """
    a presidents game

    contains players
    """
    def __init__(self) -> None:
        self._id = str(uuid4())
        self._players = [Player()]
        self.test = 20