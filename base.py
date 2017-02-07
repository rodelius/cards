import pymysql
import random
import itertools


class base():
    def __init__(self, cards=[]):
        self.SUITS = 'cdhs'
        self.RANKS = '23456789TJQKA'
        if not cards:
            self.DECK = self.completeShuffledDeck()
        else:
            self.DECK = cards
        self.DISCARDED = []
        
    def completeShuffledDeck(self):
        DECK = [''.join(card) for card in itertools.product(self.RANKS, self.SUITS)]
        random.shuffle(DECK)
        return DECK
    
    def cut(self):
        cardsInDeck = len(self.DECK)
        if (cardsInDeck % 2 == 0):
            firstHalf = self.DECK[:cardsInDeck/2]
            secondHalf = self.DECK[cardsInDeck/2:]
            self.DECK = []
            return firstHalf, secondHalf
    
    def draw(self, numCards=1):
        if (len(self.DECK) >= numCards):
            drawn = self.DECK[:numCards]
            self.DECK = self.DECK[numCards:]
            return drawn
        else:
            raise Exception('End of deck')
        
    def numCards(self):
        return len(self.DECK)
    
class stressPlayer():
    def __init__(self, cards, playerIdentifier=''):
        self.playerId = playerIdentifier
        self.hiddenDeck = base(cards)
        self.visibleTable = []
        self.updateTable()
        
    def updateTable(self):
        while len(self.visibleTable) < 4 and self.hiddenDeck.numCards():
            newCardToTable = self.hiddenDeck.draw()
            addedAsDuplicate = False
            for cardAtTable in self.visibleTable:
                if cardAtTable[0][0] == newCardToTable[0][0]: # duplicate
                    self.visibleTable.remove(cardAtTable)
                    self.visibleTable.append(list(cardAtTable) + newCardToTable)
                    addedAsDuplicate = True
                    break
            
            if not addedAsDuplicate:
                self.visibleTable.append(newCardToTable)
                
            self.visibleTable.sort()
        
        print('Updated player %s four visible cards: %s' %(self.playerId, str(self.visibleTable)))
        
    def updatePile(self):
        return self.hiddenDeck.draw()
    
    def cardsAtHand(self):
        return bool(self.hiddenDeck.numCards())
    
    def finished(self):
        return (not self.cardsAtHand()) and (not self.visibleTable)
    
    def isPuttable(self, rank, pileRank):
        if (pileRank == '9') and (rank == '8' or rank == 'T'): return True
        if (pileRank == 'T') and (rank == '9' or rank == 'J'): return True
        if (pileRank == 'J') and (rank == 'T' or rank == 'Q'): return True
        if (pileRank == 'Q') and (rank == 'J' or rank == 'K'): return True
        if (pileRank == 'K') and (rank == 'Q' or rank == 'A'): return True
        if (pileRank == 'A') and (rank == 'K' or rank == '2'): return True
        if (pileRank == '2') and (rank == 'A' or rank == '3'): return True
        try:
            if (int(pileRank) == int(rank) + 1): return True
            if (int(pileRank) == int(rank) - 1): return True 
        except:
            pass
        
        return False
        
    def stuck(self, leftPile, rightPile):
        raw_input()       
        for topOfPile in (leftPile[-1], rightPile[-1]):
            for cardAtTable in self.visibleTable:
                if self.isPuttable(cardAtTable[0][0], topOfPile[0]):
                    self.visibleTable.remove(cardAtTable)
                    if topOfPile == leftPile[-1]: leftPile += cardAtTable
                    if topOfPile == rightPile[-1]: rightPile += cardAtTable
                    print('Player %s successfully put card %s' %(self.playerId, cardAtTable))
                    self.updateTable()
                    return False
        return True

if __name__ == '__main__':
    b = base() # create new deck object
    player1Cards, player2Cards = b.cut() # cut the deck
    player1 = stressPlayer(player1Cards, '1') # create two players
    player2 = stressPlayer(player2Cards, '2')

    rightPile = player1.updatePile() # seen from the perspective of player 1
    leftPile = player2.updatePile()
    print('Table piles initiated with: %s %s' %(leftPile[0], rightPile[0]))

    while (not player1.finished()) and (not player2.finished()) and (player1.cardsAtHand() or player2.cardsAtHand()):
        if random.uniform(0,1) < 0.5:
            p1Stuck = player1.stuck(leftPile, rightPile)
            p2Stuck = player2.stuck(rightPile, leftPile)
        else:
            p2Stuck = player2.stuck(rightPile, leftPile)
            p1Stuck = player1.stuck(leftPile, rightPile)
        
        if p1Stuck and p2Stuck:
            try:
                rightPile += player1.updatePile()
            except Exception:
                pass
            try:
                leftPile += player2.updatePile()
            except Exception:
                pass
            print('Table piles updated with: %s %s' %(leftPile[-1], rightPile[-1]))
            
    if player1.finished(): print ('Player 1 won!')
    if player2.finished(): print ('Player 2 won!')
    
    print('Table piles at finish seen from first player \nLeft: %s \nRight: %s' %(leftPile, rightPile))
    
    