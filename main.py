import pyxel
import random

# constants
COLKEY = 0


def setupCardStackPosition(card_stack, row, col):
    card_stack.x = 1 + (16 + 1) * col
    card_stack.y = 1 + (16 + 2) * row
    return card_stack


class Node:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.image = -1
        self.u = 0
        self.v = 0
        self.w = 0
        self.h = 0

    def draw(self):
        if self.image != -1:
            pyxel.blt(self.x, self.y, self.image, self.u, self.v, self.w, self.h, COLKEY)
        pass

    def update(self):
        self.onUpdate()
        pass

    def onUpdate(self):
        pass


class Card(Node):
    def __init__(self, rank, suit, is_faced=True):
        super().__init__()
        self.rank = rank
        self.suit = suit
        self.is_faced = is_faced
        self.is_focus = False
        self.is_selected = False

    def draw(self):
        if self.is_faced is True:
            super().draw()
            if self.is_selected is True:
                pyxel.blt(self.x, self.y, 0, 16 * 3, 16 * 4, 16, 16, COLKEY)
        else:
            pyxel.blt(self.x, self.y, self.image, 0, 16 * 4, self.w, self.h, COLKEY)

        if self.is_focus is True:
            pyxel.blt(self.x, self.y, 0, 16 * 2, 16 * 4, 16, 16, COLKEY)


class CardStack:
    def __init__(self):
        self.x = 0
        self.y = 0

        self.y_offset = 11
        self.cards = []
        self.is_focus = False

    def draw(self):
        if len(self.cards):
            for card in self.cards:
                card.draw()
        else:
            if self.is_focus is True:
                pyxel.blt(self.x, self.y, 0, 16 * 2, 16 * 4, 16, 16, COLKEY)
            pyxel.blt(self.x, self.y, 0, 16, 16 * 4, 16, 16, COLKEY)

    def addCard(self, card):
        card.x = self.x
        card.y = self.y + self.y_offset * len(self.cards)

        self.cards.append(card)

    def popCard(self):
        return self.cards.pop()


class CardDeck(CardStack):
    def __init__(self):
        super().__init__()
        self.y_offset = 0


class HandStack(CardStack):
    def draw(self):
        if len(self.cards):
            for card in self.cards:
                card.draw()


class Game:
    def __init__(self):
        self.left_decks = []
        self.final_decks = []

        self.card_stacks = []
        self.hand_stack = None
        self.temp_stack = None
        pass

    def run(self):
        pyxel.run(self.update, self.draw)
        pass

    def initialize(self):
        pyxel.init(120, 180, caption="Pyxel Klondike")

        pyxel.load("assets/game.pyxres")

        self.left_decks.append(setupCardStackPosition(CardDeck(), 0, 0))
        self.left_decks.append(setupCardStackPosition(CardDeck(), 0, 1))

        self.final_decks.append(setupCardStackPosition(CardDeck(), 0, 3))
        self.final_decks.append(setupCardStackPosition(CardDeck(), 0, 4))
        self.final_decks.append(setupCardStackPosition(CardDeck(), 0, 5))
        self.final_decks.append(setupCardStackPosition(CardDeck(), 0, 6))

        self.card_stacks.append(setupCardStackPosition(CardStack(), 1, 0))
        self.card_stacks.append(setupCardStackPosition(CardStack(), 1, 1))
        self.card_stacks.append(setupCardStackPosition(CardStack(), 1, 2))
        self.card_stacks.append(setupCardStackPosition(CardStack(), 1, 3))
        self.card_stacks.append(setupCardStackPosition(CardStack(), 1, 4))
        self.card_stacks.append(setupCardStackPosition(CardStack(), 1, 5))
        self.card_stacks.append(setupCardStackPosition(CardStack(), 1, 6))

        self.hand_stack = setupCardStackPosition(HandStack(), 5, 0)
        self.temp_stack = HandStack()

        # init cards
        cards = []
        for suit in range(4):
            for rank in range(13):
                cards.append(self.createCard(rank, suit, False))

        # here must be card shuffling
        random.shuffle(cards)

        # place cards to stacks
        for card in cards:
            self.left_decks[0].addCard(card)

        counter = 1
        for card_stack in self.card_stacks:
            for i in range(counter):
                card = self.left_decks[0].popCard()
                card_stack.addCard(card)
                if i == counter - 1:
                    card.is_faced = True
            counter += 1

        for deck in self.final_decks:
            card = self.left_decks[0].popCard()
            card.is_faced = True
            deck.addCard(card)

        card = self.left_decks[0].popCard()
        card.is_faced = True
        self.left_decks[1].addCard(card)

        # select card
        self.card_stacks[0].cards[-1].is_focus = True

        self.card_stacks[4].cards[-2].is_faced = True
        self.card_stacks[4].cards[-3].is_faced = True
        self.card_stacks[4].cards[-4].is_faced = True

        pyxel.mouse(True)
        pass

    def createCard(self, rank, suit, is_faced=True):
        card = Card(rank, suit)
        card.image = 0
        card.w = 16
        card.h = 16
        card.u = 16 * rank
        card.v = 16 * suit

        card.x = 0
        card.y = 0

        card.is_faced = is_faced

        return card

    def finalize(self):
        pass

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            self.onMoveRight()
        elif pyxel.btnp(pyxel.KEY_LEFT):
            self.onMoveLeft()
        elif pyxel.btnp(pyxel.KEY_UP):
            self.onMoveUp()
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.onMoveDown()
        elif pyxel.btnp(pyxel.KEY_ENTER):
            self.onEnter()

        for card_stack in self.left_decks + self.card_stacks:
            for card in card_stack.cards:
                card.update()

    def getUpSelectedCandidates(self):
        candidates = []
        for deck in self.left_decks + self.final_decks:
            if deck.cards:
                candidates.append(deck.cards[-1])
        return candidates

    def getDownSelectedCandidates(self):
        candidates = []
        for card_stack in self.card_stacks:
            if card_stack.cards:
                candidates.append(card_stack.cards[-1])
        return candidates

    def getSelectCandidates(self):
        return self.getUpSelectedCandidates() + self.getDownSelectedCandidates()

    def hasUpSelected(self):
        candidates = self.getUpSelectedCandidates()
        for card in candidates:
            if card.is_selected is True:
                return True
        return False

    def hasDownSelected(self):
        candidates = self.getDownSelectedCandidates()
        for card in candidates:
            if card.is_selected is True:
                return True
        return False

    def hasSelected(self):
        return self.hasUpSelected() is True or self.hasDownSelected() is True

    def onMoveRight(self):
        print("right")
        is_found = False
        all_stacks = self.left_decks + self.final_decks + self.card_stacks
        for card_stack in all_stacks:
            if is_found is True:
                if card_stack.cards:
                    card_stack.cards[-1].is_focus = True
                else:
                    card_stack.is_focus = True
                is_found = False
                break
            for card in card_stack.cards:
                if card_stack.is_focus is True:
                    is_found = True
                    card_stack.is_focus = False
                elif card.is_focus is True:
                    is_found = True
                    card.is_focus = False
                    break
        if is_found is True:
            if all_stacks[0].cards:
                all_stacks[0].cards[-1].is_focus = True
            else:
                all_stacks[0].is_focus = True

    def onMoveLeft(self):
        print("left")
        is_found = False
        all_stacks = self.left_decks + self.final_decks + self.card_stacks
        for card_stack in reversed(all_stacks):
            if is_found is True:
                if card_stack.cards:
                    card_stack.cards[-1].is_focus = True
                else:
                    card_stack.is_focus = True
                is_found = False
                break
            for card in card_stack.cards:
                if card_stack.is_focus is True:
                    is_found = True
                    card_stack.is_focus = False
                elif card.is_focus is True:
                    is_found = True
                    card.is_focus = False
                    break
        if is_found is True:
            if all_stacks[-1].cards:
                all_stacks[-1].cards[-1].is_focus = True
            else:
                all_stacks[-1].is_focus = True

    def onMoveUp(self):
        print("up")
        is_found = False
        focus_card_stack = None
        for card_stack in self.card_stacks:
            for card in card_stack.cards:
                if card.is_focus is True:
                    focus_card_stack = card_stack
                    break
            if focus_card_stack is not None:
                break
        if focus_card_stack is None:
            return
        for card in reversed(focus_card_stack.cards):
            if card.is_faced is False:
                break
            if is_found is True:
                card.is_focus = True
                is_found = False
                break
            if card.is_focus is True:
                card.is_focus = False
                is_found = True
        if is_found is True:
            focus_card_stack.cards[-1].is_focus = True

    def onMoveDown(self):
        print("down")
        is_found = False
        focus_card_stack = None
        for card_stack in self.card_stacks:
            for card in card_stack.cards:
                if card.is_focus is True:
                    focus_card_stack = card_stack
                    break
            if focus_card_stack is not None:
                break
        if focus_card_stack is None:
            return
        for card in focus_card_stack.cards:
            if card.is_faced is False:
                continue
            if is_found is True:
                card.is_focus = True
                is_found = False
                break
            if card.is_focus is True:
                card.is_focus = False
                is_found = True
        if is_found is True:
            for card in focus_card_stack.cards:
                if card.is_faced is True:
                    card.is_focus = True
                    break

    def onEnter(self):
        print("enter")
        all_stacks = self.left_decks + self.final_decks + self.card_stacks
        if self.hand_stack.cards:
            for card_stack in all_stacks:
                is_found = False
                for card in card_stack.cards:
                    if card.is_faced is False:
                        continue
                    if card.is_focus is False:
                        continue

                    is_found = True

                if is_found is True:
                    while self.hand_stack.cards:
                        self.temp_stack.addCard(self.hand_stack.popCard())
                    while self.temp_stack.cards:
                        card_stack.addCard(self.temp_stack.popCard())
                    break
        else:
            for card_stack in all_stacks:
                start_card = None
                for card in card_stack.cards:
                    if card.is_faced is False:
                        continue
                    if card.is_focus is False:
                        continue

                    start_card = card
                    break

                if start_card is not None:
                    card = card_stack.popCard()
                    self.temp_stack.addCard(card)
                    while card.is_focus is False:
                        card = card_stack.popCard()
                        self.temp_stack.addCard(card)
                    card.is_focus = False

                    while self.temp_stack.cards:
                        self.hand_stack.addCard(self.temp_stack.popCard())

                    if card_stack.cards:
                        card_stack.cards[-1].is_focus = True
                    else:
                        card_stack.is_focus = True
                    break

    def drawBackground(self):
        pyxel.cls(11)

    def drawCardStacks(self):
        for card_stack in self.left_decks + self.card_stacks + self.final_decks + [self.hand_stack]:
            card_stack.draw()

    def draw(self):
        self.drawBackground()
        self.drawCardStacks()

        # debug
        # self.__drawDebug(1, 130)

    def __drawDebug(self, x, y):
        s = "Elapsed frame count is {}\n" "Mouse position is ({},{})".format(
            pyxel.frame_count, pyxel.mouse_x, pyxel.mouse_y
        )

        pyxel.text(x + 1, y, s, 1)


if __name__ == "__main__":
    game = Game()

    game.initialize()
    game.run()
    game.finalize()
