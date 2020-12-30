import pyxel
import random

# constants
WINDOW_W = 120
WINDOW_H = 180
COLKEY = 0
CARD_H = 16
CHAR_W = 4


def setupCardStack(card_stack, row, col, id):
    card_stack.x = 1 + (16 + 1) * col
    card_stack.y = 1 + (16 + 2) * row
    card_stack.id = id
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

    def getHeight(self):
        return self.h


class CardStack:
    def __init__(self):
        self.x = 0
        self.y = 0

        self.y_faced_offset = 11
        self.y_not_faced_offset = 5
        self.cards = []
        self.is_focus = False

        self.id = 0

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
        card.y = self.y

        if self.cards:
            if card.is_faced and self.cards[-1].is_faced:
                card.y = self.cards[-1].y + self.y_faced_offset
            else:
                card.y = self.cards[-1].y + self.y_not_faced_offset

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

    def isTopCard(self, card):
        if not self.cards:
            return False

        return self.cards[-1] is card

    def isBottomCard(self, card):
        if not self.cards:
            return False

        return self.cards[0] is card

    def isBottomFacedCard(self, card):
        if not self.cards:
            return False

        for it_card in self.cards:
            if it_card.is_faced is True:
                return it_card is card

        return False

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

    def selectBottomFacedCard(self):
        if self.cards:
            for card in self.cards:
                if card.is_faced is True:
                    card.is_focus = True
                    break
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

    def calcHeight(self):
        if self.cards:
            return self.cards[-1].y + CARD_H - self.y
        else:
            return CARD_H


class CardDeck(CardStack):
    def __init__(self):
        super().__init__()
        self.y_faced_offset = 0
        self.y_not_faced_offset = 0

    def moveCardsFromStack(self, stack):
        if len(stack.cards) != 1:
            return
        super().moveCardsFromStack(stack)


class HandStack(CardStack):
    def __init__(self):
        super().__init__()
        self.y_middle_offset = 5
        self.from_stack = None

        self.y_select_offset = 5

    def draw(self):
        if len(self.cards):
            for card in self.cards:
                card.draw()

    def addCard(self, card):
        super().addCard(card)
        if len(self.cards) <= 3:
            return

        a = self.cards[2:]
        b = self.cards[1:]
        for cur_card, prev_card in zip(a, b):
            cur_card.y = prev_card.y + self.y_middle_offset

    def updatePositionBehindStack(self, card_stack):
        self.x = card_stack.x
        self.y = card_stack.y + card_stack.calcHeight() + self.y_select_offset

        temp_cards = []
        while self.cards:
            card = self.popCard()
            temp_cards.append(card)

        while temp_cards:
            card = temp_cards.pop()
            self.addCard(card)


class Game:
    def __init__(self):
        self.left_deck = None
        self.right_deck = None

        self.final_decks = []
        self.card_stacks = []

        self.hand_stack = None

        self.up_transitions = [[7, 1], [8, 2], [9, 2], [10, 3], [11, 4], [12, 5], [13, 6]]
        self.down_transitions = [[1, 7], [2, 8], [3, 10], [4, 11], [5, 12], [6, 13]]

        self.is_game_over = False
        self.is_instructions_active = False

    def run(self):
        pyxel.run(self.update, self.draw)

    def initialize(self):
        pyxel.init(WINDOW_W, WINDOW_H, caption="Pyxel Klondike", quit_key=pyxel.KEY_NONE)
        pyxel.load("assets/game.pyxres")
        pyxel.mouse(False)

        self.reset()

    def reset(self):
        # clear all
        self.is_game_over = False
        self.left_deck = None
        self.right_deck = None
        self.final_decks = []
        self.card_stacks = []
        self.hand_stack = []

        # create all
        self.left_deck = setupCardStack(CardDeck(), 0, 0, 1)
        self.right_deck = setupCardStack(CardDeck(), 0, 1, 2)

        self.final_decks.append(setupCardStack(CardDeck(), 0, 3, 3))
        self.final_decks.append(setupCardStack(CardDeck(), 0, 4, 4))
        self.final_decks.append(setupCardStack(CardDeck(), 0, 5, 5))
        self.final_decks.append(setupCardStack(CardDeck(), 0, 6, 6))

        self.card_stacks.append(setupCardStack(CardStack(), 1, 0, 7))
        self.card_stacks.append(setupCardStack(CardStack(), 1, 1, 8))
        self.card_stacks.append(setupCardStack(CardStack(), 1, 2, 9))
        self.card_stacks.append(setupCardStack(CardStack(), 1, 3, 10))
        self.card_stacks.append(setupCardStack(CardStack(), 1, 4, 11))
        self.card_stacks.append(setupCardStack(CardStack(), 1, 5, 12))
        self.card_stacks.append(setupCardStack(CardStack(), 1, 6, 13))

        self.hand_stack = setupCardStack(HandStack(), 5, 0, 14)

        # init cards

        # Suits (total 4):
        # 0 - clubs, 1 - diamonds, 2 - hearts, 3 - spades
        # Ranks (total 13):
        # 0 - Ace, 1 - 2, 2 - 3, 3 - 4, 4 - 5, 5 - 6, 6 - 7, 7 - 8, 8 - 9, 9 - 10, 10 - Jack, 11 - Queen, 12 - King
        # total cards in deck 52

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
                if i == counter - 1:
                    card.is_faced = True
                card_stack.addCard(card)
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
        elif pyxel.btnp(pyxel.KEY_ESCAPE):
            self.onEscape()
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
        elif pyxel.btnp(pyxel.KEY_SPACE):
            self.onSpace()
        elif pyxel.btnp(pyxel.KEY_N):  # N - new game
            self.reset()
        elif pyxel.btnp(pyxel.KEY_I):
            self.is_instructions_active = not self.is_instructions_active
        elif pyxel.btnp(pyxel.KEY_G):  # G - game over debug cheat
            self.is_game_over = True

        for card_stack in self.getAllStacks():
            card_stack.update()

    def getAllCardStacks(self):
        return [self.left_deck, self.right_deck] + self.final_decks + self.card_stacks

    def getAllStacks(self):
        return [self.left_deck, self.right_deck] + self.card_stacks + self.final_decks + [self.hand_stack]

    def getUpTransitionToId(self, card_stack_id):
        for from_id, to_id in self.up_transitions:
            if card_stack_id == from_id:
                return to_id
        return None

    def getDownTransitionToId(self, card_stack_id):
        for from_id, to_id in self.down_transitions:
            if card_stack_id == from_id:
                return to_id
        return None

    def selectCardStackById(self, card_stack_id):
        for card_stack in self.getAllStacks():
            if card_stack.id == card_stack_id:
                card_stack.select()
                break

    def getCardStackById(self, card_stack_id):
        for card_stack in self.getAllStacks():
            if card_stack.id == card_stack_id:
                return card_stack
        return None

    def tryMakeUpSelectTransition(self, card_stack):
        to_id = self.getUpTransitionToId(card_stack.id)

        if to_id is None:
            return False

        card_stack.unselect()
        self.selectCardStackById(to_id)
        return True

    def tryMakeDownSelectTransition(self, card_stack):
        to_id = self.getDownTransitionToId(card_stack.id)

        if to_id is None:
            return False

        card_stack.unselect()
        to_stack = self.getCardStackById(to_id)
        if to_stack.hasFacedCards():
            to_stack.selectBottomFacedCard()
        else:
            to_stack.select()
        return True

    def updateHandStackPosition(self):
        if self.hand_stack.hasCards():
            focused_stack = None
            for card_stack in self.getAllCardStacks():
                if card_stack.isSelected():
                    focused_stack = card_stack
                    break
            if focused_stack is None:
                return
            if focused_stack in [self.left_deck, self.right_deck] + self.final_decks:
                to_stack = None
                for from_id, to_id in self.down_transitions:
                    if focused_stack.id == from_id:
                        to_stack = self.getCardStackById(to_id)
                        break
                if to_stack is not None:
                    self.hand_stack.updatePositionBehindStack(to_stack)
                else:
                    self.hand_stack.updatePositionBehindStack(focused_stack)
            else:
                self.hand_stack.updatePositionBehindStack(focused_stack)

    def isGameOver(self):
        # check left, right and bottom stacks for emptyness
        for card_stack in [self.left_deck, self.right_deck] + self.card_stacks:
            if card_stack.hasCards():
                return False

        # TO DO

        return True

    def onMoveRight(self):
        print("right")
        if self.is_game_over:
            return
        all_stacks = self.getAllCardStacks()
        shifted_stacks = all_stacks[1:] + [all_stacks[0]]
        for cur_stack, next_stack in zip(all_stacks, shifted_stacks):
            if cur_stack.isSelected() is True:
                cur_stack.unselect()
                next_stack.select()
                break

        self.updateHandStackPosition()

    def onMoveLeft(self):
        print("left")
        if self.is_game_over:
            return
        all_stacks = self.getAllCardStacks()
        shifted_stacks = [all_stacks[-1]] + all_stacks[0:-1]
        for cur_stack, next_stack in zip(reversed(all_stacks), reversed(shifted_stacks)):
            if cur_stack.isSelected() is True:
                cur_stack.unselect()
                next_stack.select()
                break

        self.updateHandStackPosition()

    def onMoveUp(self):
        print("up")

        if self.is_game_over:
            return

        # idea for cursor move to top decks from bottom stacks and vice versa:
        # 1. add to each card stack unique id:
        #   [1 ][2 ]____[3 ][4 ][5 ][6 ]
        #   [7 ][8 ][9 ][10][11][12][13]
        # 2. define vector of up and down transitions:
        #   transitions = [
        #       [7, 1], [8, 2], [9, 2], [10, 3], [11, 4], [12, 5], [13, 6],   # up
        #       [1, 7], [2, 8], [3, 10], [4, 11], [5, 12], [6, 13]            # down
        #   ]
        # 3. when prev_card is None try to do transition according to

        focus_card_stack = None

        for card_stack in self.card_stacks:
            if card_stack.isSelected() is True:
                focus_card_stack = card_stack
                break

        if focus_card_stack is None:
            for card_stack in [self.left_deck, self.right_deck] + self.final_decks:
                if card_stack.isSelected() is True:
                    focus_card_stack = card_stack
            if focus_card_stack:
                self.tryMakeUpSelectTransition(focus_card_stack)
            return

        if not focus_card_stack.hasCards():
            self.tryMakeUpSelectTransition(focus_card_stack)
            return

        selected_card = focus_card_stack.getSelectedCard()

        if (selected_card.is_faced is False or focus_card_stack.isBottomFacedCard(selected_card)) and self.tryMakeUpSelectTransition(focus_card_stack):
            return

        prev_card = focus_card_stack.getPrevCard(selected_card)

        selected_card.is_focus = False

        if prev_card.is_faced:
            prev_card.is_focus = True
        else:
            focus_card_stack.selectTopCard()

    def onMoveDown(self):
        print("down")

        if self.is_game_over:
            return

        focus_card_stack = None

        for card_stack in self.card_stacks:
            if card_stack.isSelected() is True:
                focus_card_stack = card_stack
                break

        if focus_card_stack is None:
            for card_stack in [self.left_deck, self.right_deck] + self.final_decks:
                if card_stack.isSelected() is True:
                    focus_card_stack = card_stack
            if focus_card_stack:
                self.tryMakeDownSelectTransition(focus_card_stack)
            return

        if not focus_card_stack.hasCards():
            return

        selected_card = focus_card_stack.getSelectedCard()

        if (selected_card.is_faced is False or focus_card_stack.isTopCard(selected_card)) and self.tryMakeDownSelectTransition(focus_card_stack):
            return

        next_card = focus_card_stack.getNextCard(selected_card)

        selected_card.is_focus = False

        if next_card.is_faced:
            next_card.is_focus = True
        else:
            if focus_card_stack.hasFacedCards():
                focus_card_stack.selectBottomFacedCard()
            else:
                focus_card_stack.select()

    def getSelectedStack(self):
        all_stacks = self.getAllCardStacks()

        for card_stack in all_stacks:
            if card_stack.isSelected():
                return card_stack

        return None

    def checkPlaceFromHandToNotEmptyStack(self, stack):
        hand_stack_card = self.hand_stack.cards[0]
        card_stack_card = stack.cards[-1]

        if stack in self.card_stacks:
            if hand_stack_card.rank != card_stack_card.rank - 1:
                return False

            if (hand_stack_card.suit == 0 or hand_stack_card.suit == 3) and\
                    (card_stack_card.suit == 1 or card_stack_card.suit == 2):
                return True
            elif (hand_stack_card.suit == 1 or hand_stack_card.suit == 2) and\
                    (card_stack_card.suit == 0 or card_stack_card.suit == 3):
                return True
        elif stack in self.final_decks:
            if hand_stack_card.rank != card_stack_card.rank + 1:
                return False

            if hand_stack_card.suit == card_stack_card.suit:
                return True
        return False

    def checkPlaceFromHandToEmptyStack(self, stack):
        if stack in self.card_stacks:
            if self.hand_stack.cards[0].rank == 12:  # King
                return True
        elif stack in self.final_decks:
            if self.hand_stack.cards[0].rank == 0:  # Ace
                return True
        return False

    def holdCardsToHandStack(self):
        selected_card_stack = self.getSelectedStack()

        if selected_card_stack is None:
            return

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

        self.updateHandStackPosition()

    def placeCardsFromHandStack(self):
        selected_card_stack = self.getSelectedStack()

        if selected_card_stack is None:
            return

        if selected_card_stack is self.hand_stack.from_stack:
            selected_card_stack.moveCardsFromStack(self.hand_stack)
            self.hand_stack.from_stack = None
            # BACK CARDS TO FROM STACK
        elif selected_card_stack not in [self.left_deck, self.right_deck]:
            if selected_card_stack.hasFacedCards():
                # DROP ON FACED CARDS
                if self.checkPlaceFromHandToNotEmptyStack(selected_card_stack):
                    selected_card_stack.moveCardsFromStack(self.hand_stack)
                    self.hand_stack.from_stack = None
            elif not selected_card_stack.hasCards():
                # DROP ON EMPTY STACK
                if self.checkPlaceFromHandToEmptyStack(selected_card_stack):
                    selected_card_stack.moveCardsFromStack(self.hand_stack)
                    self.hand_stack.from_stack = None
        if not self.hand_stack.hasCards():
            if self.isGameOver():
                self.is_game_over = True

    def onEnter(self):
        print("enter")
        if self.is_game_over:
            return

        if self.hand_stack.hasCards():
            self.placeCardsFromHandStack()
        else:
            self.holdCardsToHandStack()

    def onSpace(self):
        print("space")
        if self.is_game_over:
            return

        if self.hand_stack.hasCards():
            self.placeCardsFromHandStack()
        else:
            self.holdCardsToHandStack()

    def onEscape(self):
        print("escape")
        if self.is_game_over:
            return

        if self.hand_stack.from_stack is None:
            return

        selected_card_stack = self.getSelectedStack()
        selected_card_stack.unselect()

        self.hand_stack.from_stack.moveCardsFromStack(self.hand_stack)
        self.hand_stack.from_stack = None

    def drawBackground(self):
        pyxel.cls(11)

    def drawCardStacks(self):
        for card_stack in self.getAllStacks():
            card_stack.draw()

    def drawInstructions(self):
        x, y = self.calcScreenCenterPosition()
        msg = """
           RULES
           - + -

To win Klondike Solitaire 
you must move all the cards
to the four goals. Each
foundation can only hold
one suit and you must put
the cards sequencing from
Ace to King: Ace, 2, 3, 4,
5, 6, 7, 8, 9, Jack, Queen
and King. You have to
complete all suits to win
the game: clubs, diamonds,
hearts and spades. 

   <I> - SHOW CONTROLLS"""
        half_msg_width = self.calcTextWidth(msg) // 2
        pyxel.text(x - half_msg_width, y - 24, msg, 3)

    def drawCotrollsInfo(self):
        x, y = self.calcScreenCenterPosition()
        msg = """   KEYBOARD CONTROLLS
   - - - - + - - - - 
 
    ARROWS - MOVE
   <SPACE> - HOLD/PLACE
   <ENTER> - HOLD/PLACE
     <ESC> - DROP
     
       <N> - NEW GAME
       <I> - GAME  (!)
             RULES
       <Q> - EXIT"""
        half_msg_width = self.calcTextWidth(msg) // 2
        pyxel.text(x - half_msg_width, y, msg, 3)

    def calcTextWidth(self, msg):
        lens = []
        cur_len = 0
        for char in msg:
            if char == '\n':
                lens.append(cur_len)
                cur_len = 0
            else:
                cur_len += 1
        if lens:
            max_len = max(lens)
        else:
            max_len = cur_len
        return max_len * CHAR_W

    def calcScreenCenterPosition(self):
        x = WINDOW_W // 2
        y = WINDOW_H // 2
        return x, y

    def drawGaveOver(self):
        x, y = self.calcScreenCenterPosition()
        msg = "G A M E   O V E R"
        half_msg_width = self.calcTextWidth(msg) // 2

        COL_1 = 1
        COL_2 = 15

        pyxel.text(x - half_msg_width + 1, y- 7, msg, COL_1)
        pyxel.text(x - half_msg_width, y + 1- 7, msg, COL_1)
        pyxel.text(x - half_msg_width - 1, y- 7, msg, COL_1)
        pyxel.text(x - half_msg_width, y - 1- 7, msg, COL_1)

        pyxel.text(x - half_msg_width - 1, y - 1- 7, msg, COL_1)
        pyxel.text(x - half_msg_width - 1, y + 1- 7, msg, COL_1)
        pyxel.text(x - half_msg_width + 1, y + 1- 7, msg, COL_1)
        pyxel.text(x - half_msg_width + 1, y - 1- 7, msg, COL_1)

        pyxel.text(x - half_msg_width, y- 7, msg, COL_2)

    def draw(self):
        self.drawBackground()
        if self.is_instructions_active:
            self.drawInstructions()
        else:
            self.drawCotrollsInfo()

        self.drawCardStacks()

        if self.is_game_over:
            self.drawGaveOver()

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
