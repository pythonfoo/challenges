#!/usr/bin/env python3

import operator
import os
import sys

class foundWord():
    DIRECTION_ROW = 0
    DIRECTION_COLUMN = 1
    DIRECRION_DIAGONAL_UP = 2
    DIRECRION_DIAGONAL_DOWN = 3

    def __init__(self, word, row, col, direction):
        self.word = word
        self.row = row
        self.col = col
        self.direction = direction

    def __str__(self):
        return '{0}: {1}, {2}, {3}'.format(self.word, self.row+1, self.col+1, foundWord.directionToString(self.direction))

    def directionToString(direction=-1):
        return ['ROW', 'COLUMN', 'UP', 'DOWN'][direction]

class detectWords():
    '''
    @:parameter charGridFile string
    @:parameter wordListFile string
    '''
    def __init__(self, charGridFile='', wordListFile=''):
        self.charGrid = ()
        self.wordList = set()
        self.minWordLength = 4
        self.foundWords = []

        charGridHandler = open(charGridFile, 'r')
        self.charGrid = charGridHandler.read().lower().split("\n")

        #print(self.charGrid)

        for row in open(wordListFile, 'r').read().split("\n"):
            word = row.strip().lower()
            if len(word) >= self.minWordLength:
                self.wordList.add(word)

    def process(self):
        self.findHorizontals(self.charGrid)
        self.findVertical()
        #self.findDiagonalUp()

    def addFoundWord(self, word, row, col, direction):
        #if not word in self.foundWords:
        #    self.foundWords[word] =
        #self.foundWords += 1
        self.foundWords.append(foundWord(word, row, col, direction))

    def printFound(self):
        #foundSorted = sorted(self.foundWords.items(), key=operator.itemgetter(1))
        print('found words:', len(self.foundWords))
        for foundWord in self.foundWords:
            print(foundWord)

    def findHorizontals(self, modCharGrid):
        self.foundWords.extend(self.getHorizontals(modCharGrid))
        #self.addFoundWord(word, xIndex, y, foundWord.DIRECTION_ROW)

    def getHorizontals(self, modCharGrid):
        found = []
        rowCount = len(modCharGrid)
        for word in self.wordList:
            for colIndex in range(rowCount):
                rowIndex = modCharGrid[colIndex].find(word)
                if rowIndex != -1:
                    found.append(foundWord(word, colIndex, rowIndex, foundWord.DIRECTION_ROW))
        return found

    def findVertical(self):
        rotatedGrid = []
        for colIndex in range(len(self.charGrid[0])):
            for row in self.charGrid:
                if len(rotatedGrid) -1 < colIndex:
                    rotatedGrid.append('')
                rotatedGrid[colIndex] += row[colIndex]

        foundWords = self.getHorizontals(rotatedGrid)
        for found in foundWords:
            found.row, found.col = found.col, found.row
            found.direction = foundWord.DIRECTION_COLUMN
            self.foundWords.append(found)

    def findDiagonalDown(self):
        #TODO: use generators!
        return
        rowCount = len(self.charGrid)
        colCount = len(self.charGrid[0])
        for rowIndex in range(rowCount):
            rebuildRow = ''
            for char in self.charGrid[rowIndex]:
                pass


    def findDiagonalUp(self):
        return
        rowCount = len(self.charGrid)
        colCount = len(self.charGrid[0])

        for rowIndex in range(rowCount):
            rebuildRow = ''

            for colIndex in range(rowIndex -1, 0, -1):
                rebuildRow += self.charGrid[rowIndex][colIndex]
                rowIndex -= 1

            print(rebuildRow)
        sys.exit()

if __name__ == '__main__':
    dw = detectWords('../chargrid.txt', '../zingarelli2005.txt')
    if os.path.exists('../Collins_Scrabble_Words_2015.txt'):
        print('collins')
        dw = detectWords('../chargrid.txt', '../Collins_Scrabble_Words_2015.txt')

    dw.process()
    dw.printFound()