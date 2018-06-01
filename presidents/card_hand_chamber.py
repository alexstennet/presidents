import numpy as np
from llist import sllist, sllistnode, dllist, dllistnode
from typing import List, Union
from hand import Hand


class CardHandChamber:
    """
    storage for cards and hands specifically designed for fast runtimes
    in context of front end interaction
    """
    def __init__(self, cards: np.ndarray) -> None:
        self._num_cards = 0
        self._cards = np.empty(shape=53, dtype=np.object)
        for card in cards:
            self[card] = dllist()  # a dllist of HandPointerNodes
            self._num_cards += 1
        self._hands: dllist = dllist()  # a dllist of ConsciousHandNodes

    def __getitem__(self, key: Union[int, slice]) -> dllist:
        return self._cards[key]

    def __setitem__(self, key: Union[int, slice], value: dllist) -> None:
        self._cards[key] = value

    def add_hand(self, hand: Hand) -> None:
        cards: List[int] = list()
        hand_pointer_nodes: List[dllistnode] = list()
        for card in hand:
            cards.append(card)
            hand_pointer_dllnode = self[card].append(None)
            hand_pointer_node = HandPointerNode(hand_pointer_dllnode)
            hand_pointer_dllnode.value = hand_pointer_node
            hand_pointer_nodes.append(hand_pointer_node)
        hand_dllnode = self._hands.append(None)
        hand_dllnode.value = ConsciousHandNode(hand_dllnode, cards,
                                               hand_pointer_nodes, str(hand))

    def remove_card(self, card: int) -> None:
        assert self[card], "Bug: this card is not here."  # TODO: ehh
        for hand_pointer_node in self[card]:
            hand_pointer_dllnode = hand_pointer_node.hand_pointer_dllnode
            hand_dllnode = hand_pointer_node.hand_dllnode
            hand_node = hand_dllnode.value
            for card_node in hand_node:
                if card_node.hand_pointer_dllnode is hand_pointer_dllnode:
                    continue
                self[card_node.card].remove(card_node.hand_pointer_dllnode)
            self._hands.remove(hand_dllnode)
        self[card] = None


class HandPointerNode:  # contained by a hand_pointer_dllnode
    def __init__(self, hand_pointer_dllnode: dllistnode) -> None:
        self.hand_dllnode = None
        self.hand_pointer_dllnode = hand_pointer_dllnode

    def set_hand_dllnode(self, hand_dllnode: dllistnode) -> None:
        self.hand_dllnode = hand_dllnode

    def __repr__(self):
        return self.hand_dllnode.value.__repr__()


class ConsciousHandNode:  # contained by a hand_dllnode
    def __init__(self, hand_dllnode: dllistnode, cards: List[int],
                 hand_pointer_nodes: List[HandPointerNode], dom_id: str) -> None:
        self._dom_id = dom_id
        self._num_cards_selected = 0
        self._card_nodes: List[CardNode] = list()
        for card, hand_pointer_node in zip(cards, hand_pointer_nodes):
            hand_pointer_node.set_hand_dllnode(hand_dllnode)
            card_node = CardNode(card, hand_pointer_node.hand_pointer_dllnode)
            self._card_nodes.append(card_node)

    def __iter__(self):
        return self._card_nodes.__iter__()

    def __repr__(self):
        return self._dom_id


class CardNode:
    def __init__(self, card: int, hand_pointer_dllnode: dllistnode) -> None:
        self.card = card
        self.hand_pointer_dllnode = hand_pointer_dllnode

    def __repr__(self) -> str:
        return str(self.card)
