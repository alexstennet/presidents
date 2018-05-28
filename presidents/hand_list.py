from typing import Set
from hand import Hand
from json import dumps, loads


class HandList:
    """
    A simple data structure for storing hands that can be stored as JSON
    and has the following properties: it is not ordered (yet--need to
    decide how to implement ordering because right now hands with
    different id's cannot be compared and I kind of want to avoid that),
    ...
    """
    def __init__(self, _hands=set()) -> None:
        self._hands: Set[Hand] = set(_hands)

    @classmethod
    def from_json(cls, json_hand_list: str):
        return cls(list(map(Hand.from_json, loads(json_hand_list))))

    def __iter__(self):  # TODO: return type for this
        return self._hands.__iter__()

    def __contains__(self, hand: Hand):
        return hand in self._hands

    def __repr__(self):  # TODO: i don't like this
        pretty = ""
        for hand in self:
            pretty += repr(hand) + "\n"
        return pretty

    def add(self, hand: Hand) -> None:
        self._hands.add(hand)

    def remove(self, hand: Hand) -> None:
        self._hands.remove(hand)

    def to_json(self) -> str:
        return dumps(list(self), default=lambda x: x.to_json())
