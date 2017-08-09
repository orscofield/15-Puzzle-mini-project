# Sliding Puzzle Solver ##
# Made by Or Shlomo ##
import math
from heapq import heappush, heappop
# On a NxN sized panel there are 2^N-1 numbered plates


# just a way to make an enum in python
def enum(**enums):
    return type('Enum', (), enums)


# this is the enum i need
Direction = enum(LEFT='left', RIGHT='right', UP='up', DOWN='down')


class Puzzle:
    'the puzzle object'

    dimension = -1
    board = []
    path = []
    lastMove = None

    def __init__(self, dimension):
        self.dimension = dimension
        self.board = [[0 for x in range(dimension)]
                      for y in range(dimension)]
        self.path = []
        self.lastMove = None

        for i in range(0, dimension):
            for j in range(0, dimension):
                if (i == dimension - 1 and j == dimension - 1):
                    self.board[i][j] = 0
                else:
                    self.board[i][j] = dimension * i + j + 1

    # finds the location of the mission plate on the board
    def getZeroPosition(self):
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                if self.board[i][j] == 0:
                    return [i, j]

    # swaps two locations on the board
    def swap(self, i1, j1, i2, j2):
        temp = self.board[i1][j1]
        self.board[i1][j1] = self.board[i2][j2]
        self.board[i2][j2] = temp

    # return a possible legal move for the piece, or None otherwise
    def getMove(self, piece):
        zeroPosition = self.getZeroPosition()
        line = zeroPosition[0]
        column = zeroPosition[1]
        if (line > 0 and piece == self.board[line - 1][column]):
            return Direction.DOWN
        elif (
            line < self.dimension - 1 and
            piece == self.board[line + 1][column]
        ):
            return Direction.UP
        elif (column > 0 and piece == self.board[line][column - 1]):
            return Direction.RIGHT
        elif (
            column < self.dimension - 1 and
            piece == self.board[line][column + 1]
        ):
            return Direction.LEFT

    # pretty prints the current state of the board
    def printBoard(self):
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                print self.board[i][j], "\t",
                if (j == self.dimension - 1):
                    print "\n\n"

    # moves a piece if it is possible and returns the direction it was moved
    def move(self, piece):
        move = self.getMove(piece)
        if (move is not None):
            zeroPosition = self.getZeroPosition()
            line = zeroPosition[0]
            column = zeroPosition[1]
            if (move == Direction.LEFT):
                self.swap(line, column, line, column + 1)
            elif (move == Direction.RIGHT):
                self.swap(line, column, line, column - 1)
            elif (move == Direction.UP):
                self.swap(line, column, line + 1, column)
            elif (move == Direction.DOWN):
                self.swap(line, column, line - 1, column)
            self.lastMove = piece
            return move

    # BFS - origin of a piece is always
    # [(piece-1)/dimension][(piece-1)%dimension]
    def isGoal(self):
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                piece = self.board[i][j]
                if (piece != 0):
                    originLine = math.floor((piece - 1) / self.dimension)
                    originColumn = (piece - 1) % self.dimension
                    if (i != originLine or j != originColumn):
                        return False
        return True

    # returns all current allowed moves in an array
    def allowedMoves(self):
        allowedMoves = []
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                piece = self.board[i][j]
                if (self.getMove(piece) is not None):
                    allowedMoves.append(piece)
        return allowedMoves

    # copies current puzzle
    def getCopy(self):
        newPuzzle = Puzzle(self.dimension)
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                newPuzzle.board[i][j] = self.board[i][j]
        for i in range(0, len(self.path)):
            newPuzzle.path.append(self.path[i])
        return newPuzzle

    # BFS visit function
    def visit(self):
        children = []
        allowedMoves = self.allowedMoves()
        for i in range(0, len(allowedMoves)):
            move = allowedMoves[i]
            if (move != self.lastMove):
                newIns = self.getCopy()
                newIns.move(move)
                newIns.path.append(move)
                children.append(newIns)
        return children

    # BFS solution, runtime O(4^n)???
    def solBFS(self):
        counter = 0
        head = self.getCopy()
        head.path = []
        states = []
        states.append(head)
        print "Initial Board:"
        states[0].printBoard()
        while (len(states) > 0):
            state = states.pop(0)
            if (state.isGoal() is True):
                return state.path
            counter += 1
            # Too much moves, I stop the solution because it might take forever
            if (counter == 1000000):
                print "counter is ", counter
                return state.path
            states.extend(state.visit())

    # A* solution
    # using real cost function g() which is the number of moves from the start
    # and using heuristic function h() - cost from current state to solution

    def g(self):
        return len(self.path)

    # heuristic 1 - misplaced tiles - how many tiles are in the wrong position
    def h1(self):
        count = 0
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                piece = self.board[i][j]
                if (piece != 0):
                    originLine = math.floor((piece - 1) / self.dimension)
                    originColumn = (piece - 1) % self.dimension
                    if (i != originLine or j != originColumn):
                        count += 1
        return count

    # heuristic 2 - Manhattan Distance |X1-X2| + |Y1 - Y2|
    def h2(self):
        dist = 0
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                piece = self.board[i][j]
                if (piece != 0):
                    originLine = math.floor((piece - 1) / self.dimension)
                    originColumn = (piece - 1) % self.dimension
                    dist += math.fabs(i - originLine) +\
                        math.fabs(j - originColumn)
        return dist

    def solAStar(self, heuristic):
        counter = 0
        head = self.getCopy()
        head.path = []
        states = []
        heappush(states, (0, head))
        print "Initial Board:"
        states[0][1].printBoard()
        while (len(states) > 0):
            state = heappop(states)
            if (state[1].isGoal() is True):
                return state[1].path
            counter += 1
            children = state[1].visit()
            while (len(children) > 0):
                child = children.pop(0)
                if (heuristic is 1):
                    f = child.g() + child.h1()
                else:
                    f = child.g() + child.h2()
                heappush(states, (f, child))
        # print "counter is: ", counter
        # return heappop(states)

    # check if current puzzle can be solved -
    # by determing if the permutation is odd or even
    # odd - unsolvable, even - solvable
    # time complexity - O(n^2)
    def isSolvable(self):
        table = [x for sublist in self.board for x in sublist]
        print table
        counter = 0
        row = 0
        blankRow = 0
        for i in range(0, len(table)):
            if(i % self.dimension):
                row += 1
            if(table[i] == 0):
                blankRow = row
                continue
            for j in range(i+1, len(table)):
                if(table[i] > table[j] and table[j] != 0):
                    counter += 1
        print "Number of inversions: ", counter
        if (self.dimension %2 == 0):
            if (blankRow %2 == 0):
                if (counter % 2 == 0):
                    print "can be solved!"
                else:
                    print "can not be solved"
            elif (counter % 2 != 0):
                print "can be solved!"
            else:
                print "can not be solved"
        elif (counter % 2 == 0):
            print "can be solved!"
        else:
            print "can not be solved"

# A test showing a BFS solution (both BFS and A* return the same solution)
test1 = Puzzle(4)
test1.board = [[1, 0, 3, 4], [5, 2, 6, 8], [9, 10, 7, 12], [13, 14, 11, 15]]

test2 = Puzzle(5)
test2.board = [[1, 2, 3, 4, 5],
               [6, 7, 8, 9, 10],
               [11, 12, 13, 14, 15],
               [16, 0, 23, 18, 20],
               [21, 17, 22, 19, 24]]

test3 = Puzzle(4)
test3.board = [[1, 2, 3, 4], [12, 5, 6, 7], [8, 9, 13, 15], [0, 14, 10, 11]]

test4 = Puzzle(4)
test4.board = [[6, 1, 3, 7], [2, 9, 8, 4], [5, 10, 0, 12], [13, 14, 11, 15]]

# this one can not be solved - lloyd's riddle
test5 = Puzzle(4)
test5.board = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 15, 14, 0]]

# An indication that everything is interpeted
print "All done!"
