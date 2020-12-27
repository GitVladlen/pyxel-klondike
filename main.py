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

    def update(self):
        for card in self.cards:
            card.update()

    def addCard(self, card):
        card.x = self.x
        card.y = self.y + self.y_offset * len(self.cards)

        self.cards.append(card)

    def popCard(self):
        return self.cards.pop()

    def isSelected(self):
        if self.cards:
            for card in self.cards:
                if card.is_focus:
                    return True
            return False
        else:
            return self.is_focus

    def unselect(self):
        if self.cards:
            for card in self.cards:
                if card.is_focus:
                    card.is_focus = False
                    break
        else:
            self.is_focus = False

    def select(self):
        if self.cards:
            self.cards[-1].is_focus = True
        else:
            self.is_focus = True

    def getSelectedCard(self):
        if not self.cards:
            return None
        for card in self.cards:
            if card.is_focus:
                return card

    def getNextCard(self, card):
        if not self.cards:
            return None
        if card not in self.cards:
            return None
        index = self.cards.index(card)
        return self.cards[index + 1 - len(self.cards)]

    def getPrevCard(self, card):
        if not self.cards:
            return None
        if card not in self.cards:
            return None
        index = self.cards.index(card)
        return self.cards[index - 1]

    def hasCards(self):
        return bool(self.cards)

    def moveCardsFromStack(self, stack):
        self.unselect()
        stack.selectBottomCard()

        temp_cards = []
        while stack.hasCards():
            card = stack.popCard()
            temp_cards.append(card)

        while temp_cards:
            self.addCard(temp_cards.pop())

    def popFromSelectedToStack(self, stack):
        selected_card = self.getSelectedCard()

        if selected_card is None:
            return

        if not selected_card.is_faced:
            return

        temp_cards = []

        card = self.popCard()
        temp_cards.append(card)
        while card is not selected_card:
            card = self.popCard()
            temp_cards.append(card)

        while temp_cards:
            stack.addCard(temp_cards.pop())

        stack.unselect()
        self.selectTopCard()

    def selectTopCard(self):
        if self.cards:
            self.cards[-1].is_focus = True
        else:
            self.is_focus = True

    def selectBottomCard(self):
        if self.cards:
            self.cards[0].is_focus = True
        else:
            self.is_focus = True

    def hasFacedCards(self):
        if not self.hasCards():
            return False

        return self.cards[-1].is_faced

    def openCard(self):
        if not self.hasCards():
            return

        self.cards[-1].is_faced = True


class CardDeck(CardStack):
    def __init__(self):
        super().__init__()
        self.y_offset = 0

    def moveCardsFromStack(self, stack):
        if len(stack.cards) != 1:
            return
        super().moveCardsFromStack(stack)


class HandStack(CardStack):
    def __init__(self):
        super().__init__()
        self.y_middle_offset = 5
        self.from_stack = None

    def draw(self):
        if len(self.cards):
            for card in self.cards:
                card.draw()

    def addCard(self, card):
        super().addCard(card)
        if len(self.cards) <= 3:
            return

        for prev_card, cur_card in zip(self.cards[1:-1], self.cards[2:-1]):
            cur_card.y = prev_card.y + self.y_middle_offset

        self.cards[-1].y = self.cards[-2].y + self.y_offset


class Game:
    def __init__(self):
        self.left_deck = None
        self.right_deck = None

        self.final_decks = []
        self.card_stacks = []

        self.hand_stack = None

    def run(self):
        pyxel.run(self.update, self.draw)

    def initialize(self):
        pyxel.init(120, 180, caption="Pyxel Klondike")
        pyxel.load("assets/game.pyxres")
        pyxel.mouse(True)

        self.left_deck = setupCardStackPosition(CardDeck(), 0, 0)
        self.right_deck = setupCardStackPosition(CardDeck(), 0, 1)

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

        # init cards
        cards = []
        for suit in range(4):
            for rank in range(13):
                cards.append(self.createCard(rank, suit, False))

        random.shuffle(cards)

        # place cards to stacks
        for card in cards:
            self.left_deck.addCard(card)

        counter = 1
        for card_stack in self.card_stacks:
            for i in range(counter):
                card = self.left_deck.popCard()
                card_stack.addCard(card)
                if i == counter - 1:
                    card.is_faced = True
            counter += 1

        self.card_stacks[0].cards[-1].is_focus = True

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

        for card_stack in self.getAllStacks():
            card_stack.update()

    def getAllCardStacks(self):
        return [self.left_deck, self.right_deck] + self.final_decks + self.card_stacks

    def getAllStacks(self):
        return [self.left_deck, self.right_deck] + self.card_stacks + self.final_decks + [self.hand_stack]

    def onMoveRight(self):
        print("right")
        all_stacks = self.getAllCardStacks()
        shifted_stacks = all_stacks[1:] + [all_stacks[0]]
        for cur_stack, next_stack in zip(all_stacks, shifted_stacks):
            if cur_stack.isSelected() is True:
                cur_stack.unselect()
                next_stack.select()
                break

    def onMoveLeft(self):
        print("left")
        all_stacks = self.getAllCardStacks()
        shifted_stacks = [all_stacks[-1]] + all_stacks[0:-1]
        for cur_stack, next_stack in zip(reversed(all_stacks), reversed(shifted_stacks)):
            if cur_stack.isSelected() is True:
                cur_stack.unselect()
                next_stack.select()
                break

    def onMoveUp(self):
        print("up")
        focus_card_stack = None

        for card_stack in self.card_stacks:
            if card_stack.isSelected() is True:
                focus_card_stack = card_stack
                break

        if focus_card_stack is None:
            return

        selected_card = focus_card_stack.getSelectedCard()
        prev_card = focus_card_stack.getPrevCard(selected_card)

        if prev_card is None:
            return

        if not prev_card.is_faced:
            return

        selected_card.is_focus = False
        prev_card.is_focus = True

    def onMoveDown(self):
        print("down")
        focus_card_stack = None

        for card_stack in self.card_stacks:
            if card_stack.isSelected() is True:
                focus_card_stack = card_stack
                break

        if focus_card_stack is None:
            return

        selected_card = focus_card_stack.getSelectedCard()
        next_card = focus_card_stack.getNextCard(selected_card)

        if next_card is None:
            return

        if not next_card.is_faced:
            return

        selected_card.is_focus = False
        next_card.is_focus = True

    def onEnter(self):
        print("enter")
        all_stacks = self.getAllCardStacks()

        selected_card_stack = None
        for card_stack in all_stacks:
            if card_stack.isSelected():
                selected_card_stack = card_stack
                break

        if self.hand_stack.hasCards():
            if selected_card_stack not in [self.left_deck, self.right_deck] and selected_card_stack.hasFacedCards() or selected_card_stack is self.hand_stack.from_stack:
                selected_card_stack.moveCardsFromStack(self.hand_stack)
                self.hand_stack.from_stack = None
        else:
            if selected_card_stack is self.left_deck:
                if self.left_deck.hasCards():
                    card = self.left_deck.popCard()
                    card.is_faced = True
                    self.right_deck.addCard(card)
                else:
                    while self.right_deck.hasCards():
                        card = self.right_deck.popCard()
                        card.is_faced = False
                        self.left_deck.addCard(card)
                self.right_deck.unselect()
                self.left_deck.selectTopCard()
            else:
                if selected_card_stack.hasCards() and not selected_card_stack.hasFacedCards():
                    selected_card_stack.openCard()
                else:
                    selected_card_stack.popFromSelectedToStack(self.hand_stack)
                    self.hand_stack.from_stack = selected_card_stack

    def drawBackground(self):
        pyxel.cls(11)

    def drawCardStacks(self):
        for card_stack in self.getAllStacks():
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
