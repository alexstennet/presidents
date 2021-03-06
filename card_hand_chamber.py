import numpy as np
from llist import sllist, sllistnode, dllist, dllistnode
from typing import List, Union, Generator
from hand import Hand
from flask_socketio import emit


# TODO: use del for hand?
# TODO: add is not None checks for cards existing
# TODO: utilize weakrefs from the hand nodes to their parents instead of
#       storing the card number in a card node allowing to get rid of 
#       card nodes


class CardHandChamber:
    """
    storage for cards and hands specifically designed for fast runtimes
    in context of front end interaction
    """
    def __init__(self, cards: np.ndarray, player_sid: str) -> None:
        self._num_cards = 0
        self._cards = np.empty(shape=53, dtype=np.object)
        for card in cards:
            self[card] = dllist()  # a dllist of HandPointerNodes
            self._num_cards += 1
        self._hands: dllist = dllist()  # a dllist of ConsciousHandNodes
        self._player_sid = player_sid

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
        hand_dllnode.value = ConsciousHandNode(hand, hand_dllnode, hand_pointer_nodes)

    def select_card(self, card: int):
        emit('select card', {'card': int(card)}, room=self._player_sid)
        for hand_pointer_node in self[card]:
            hand_node = hand_pointer_node.hand_dllnode.value
            hand_node.increment_num_selected_cards()

    def deselect_card(self, card: int):
        emit('deselect card', {'card': int(card)}, room=self._player_sid)
        for hand_pointer_node in self[card]:
            hand_node = hand_pointer_node.hand_dllnode.value
            hand_node.decrement_num_selected_cards()

    def remove_card(self, card: int) -> None:
        for hand_pointer_node in self[card]:
            hand_pointer_dllnode = hand_pointer_node.hand_pointer_dllnode
            hand_dllnode = hand_pointer_node.hand_dllnode
            hand_node = hand_dllnode.value
            for card_node in hand_node:
                if card_node.hand_pointer_dllnode is hand_pointer_dllnode:
                    continue
                self[card_node.card].remove(card_node.hand_pointer_dllnode)
            hand_node.remove_hand()
            self._hands.remove(hand_dllnode)
        emit('remove card', {'card': int(card)}, room=self._player_sid)
        self[card] = None
        self._num_cards -= 1
        if self._num_cards == 0:
            emit('finished')

    def add_card(self, card: int) -> None:
        self[card] = dllist()
        self._num_cards += 1
        emit('add card', {'card': int(card)}, room=self._player_sid)

    def clear_hands(self) -> None:
        for hand_node in self._hands:
            hand_node.remove_hand()
        self._hands.clear()
        self._reset_card_dllists()

    def _reset_card_dllists(self) -> None:  # TODO: can be done better
        for card, dll in enumerate(self._cards):
            if dll is not None:
                self[card].clear()

    def contains_card(self, card: int) -> bool:
        return self._cards[card] is not None

    def contains_hand(self, hand: Hand) -> bool:
        for hand_node in self._hands:
            if hand_node.hand == hand:
                return True
        return False

    def iter_cards(self) -> Generator[int, None, None]:
        for card in range(1, 53):
            if self.contains_card(card):
                yield card


class HandPointerNode:  # contained by a hand_pointer_dllnode
    def __init__(self, hand_pointer_dllnode: dllistnode) -> None:
        self.hand_dllnode = None
        self.hand_pointer_dllnode = hand_pointer_dllnode

    def set_hand_dllnode(self, hand_dllnode: dllistnode) -> None:
        self.hand_dllnode = hand_dllnode

    def __repr__(self):
        return self.hand_dllnode.value.__repr__()


class ConsciousHandNode:  # contained by a hand_dllnode
    def __init__(self, hand: Hand, hand_dllnode: dllistnode,
                 hand_pointer_nodes: List[HandPointerNode]) -> None:
        self.hand = Hand.copy(hand)
        self._num_cards_selected = 0
        self._card_nodes: List[CardNode] = list()
        for card, hand_pointer_node in zip(hand, hand_pointer_nodes):
            hand_pointer_node.set_hand_dllnode(hand_dllnode)
            card_node = CardNode(card, hand_pointer_node.hand_pointer_dllnode)
            self._card_nodes.append(card_node)
        self.store_hand()

    def __iter__(self):
        return self._card_nodes.__iter__()

    def __str__(self):
        return str(self.hand)

    def increment_num_selected_cards(self) -> None:
        self._num_cards_selected += 1
        if self._num_cards_selected == 1:
            emit('select hand', {'hand': str(self)}, broadcast=False)

    def decrement_num_selected_cards(self) -> None:
        self._num_cards_selected -= 1
        if self._num_cards_selected == 0:
            emit('deselect hand', {'hand': str(self)}, broadcast=False)

    def store_hand(self) -> None:
        emit('store hand', {'hand': str(self), 'cards': list(map(int, self.hand))}, broadcast=False)

    def remove_hand(self) -> None:
        emit('remove hand', {'hand': str(self)}, broadcast=False)


class CardNode:
    def __init__(self, card: int, hand_pointer_dllnode: dllistnode) -> None:
        self.card = card
        self.hand_pointer_dllnode = hand_pointer_dllnode

    def __repr__(self) -> str:
        return f"CardNode({str(self.card)})"
