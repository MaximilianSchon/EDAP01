import datetime
import random
import sys
from copy import deepcopy
import math
import hashlib

lettersDigitMap = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                   'e': 4, 'f': 5, 'g': 6, 'h': 7,
                   0: 'a', 1: 'b', 2: 'c', 3: 'd',
                   4: 'e', 5: 'f', 6: 'g', 7: 'h'}
dark = 'd'
light = 'l'
empty = ' '
opp = 'r'
game = True
player1 = light
player2 = dark
timelimit = 1
table = {}


def printBoard(board):
    print([' ', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
    num = 1
    for row in board:
        print("[" + str(num) + "], " + str(row))
        num += 1


def toIndices(move):
    return int(move[1]) - 1, lettersDigitMap[move[0]]


def fromIndices(x, y):
    return lettersDigitMap[y] + str(x + 1)


def countColor(board, color):
    count = 0
    for row in board:
        for slot in row:
            if slot == color:
                count += 1
    return count


def countCorners(board, color):
    count = 0
    corners = [(7, 7), (0, 7), (0, 0), (7, 0)]
    for corner in corners:
        if board[corner[0]][corner[1]] == color:
            count += 1
    return count


def printResults(board):
    darkpoints = 0
    lightpoints = 0
    for row in board:
        for slot in row:
            if slot == light:
                lightpoints += 1
            elif slot == dark:
                darkpoints += 1
    print("------RESULTS------")
    print("DARK:            " + str(darkpoints))
    print("LIGHT:           " + str(lightpoints))
    print("AI is DARK" if player2 == dark else "AI is LIGHT")
    if darkpoints == lightpoints:
        print("TIE")
    else:
        print(("DARK " if darkpoints > lightpoints else "LIGHT ") + "WINS")
        return dark if darkpoints > lightpoints else light


def getLegalMoves(board, color):
    moves = []
    for x in range(8):
        for y in range(8):
            poss = traverseDiagonal(board, x, y, color) + traverseVertical(board, x, y, color) + traverseHorizontal(
                board, x, y, color)
            moves.append((fromIndices(x, y), poss))
    corners = []
    edges = []
    rest = []
    for move in [move for move in moves if move[1] != []]:
        if move[0] == 'a8' or move[0] == 'a1' or move[0] == 'h1' or move[0] == 'h8':
            corners.append(move)
        elif 'a' in move[0] or 'h' in move[0] or '1' in move[0] or '8' in move[0]:
            edges.append(move)
        else:
            rest.append(move)
    return corners + edges + rest


def countImportant(board, color):
    count = 0
    weights =  [[64, -8, 8, 8, 8, 8, -8, 64],
                [-8, -8, 0, 0, 0, 0, -8, -8],
                [ 8,  0, 0, 0, 0, 0,  0,  8],
                [ 8,  0, 0, 0, 0, 0,  0,  8],
                [ 8,  0, 0, 0, 0, 0,  0,  8],
                [ 8,  0, 0, 0, 0, 0,  0,  8],
                [-8, -8, 0, 0, 0, 0, -8, -8],
                [64, -8, 8, 8, 8, 8, -8, 64]]
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == color:
                count += weights[row][col]
    return count


def traverseDiagonal(board, x, y, color):
    diagonal = traverse(board, x, y, color, 1, 1) + traverse(board, x, y, color, -1, -1) + \
               traverse(board, x, y, color, -1, 1) + traverse(board, x, y, color, 1, -1)
    return diagonal if diagonal else []


def traverseVertical(board, x, y, color):
    vertical = traverse(board, x, y, color, 0, 1) + traverse(board, x, y, color, 0, -1)
    return vertical if vertical else []


def traverseHorizontal(board, x, y, color):
    horizontal = traverse(board, x, y, color, 1, 0) + traverse(board, x, y, color, -1, 0)
    return horizontal


def traverse(board, x, y, color, xDir, yDir):
    last = board[x][y]
    opponent = player1 if color == player2 else player2
    opponents = []
    if last != empty:
        return []
    else:
        x += xDir
        y += yDir
        last = 'okay to start'
    while last != empty and 0 <= x < 8 and 0 <= y < 8:
        if board[x][y] == opponent:
            placement = fromIndices(x, y)
            opponents.append(placement)
        if board[x][y] == color:
            return opponents
        last = board[x][y]
        x += xDir
        y += yDir
    return []


def getAIMove(board, turn):
    start = datetime.datetime.now()
    value, move = search(board, -sys.maxsize, sys.maxsize, turn, start, depth)
    print("Thought for: " + str((datetime.datetime.now() - start).seconds) + " second(s)")
    return move


def getrandommove(board, color):
    return random.choice(getLegalMoves(board, color))[0]


def search(board, alpha, beta, turn, startTime, depth):
    opponent = player1 if player2 == turn else player2
    myMoves = getLegalMoves(board, turn)
    oppMoves = getLegalMoves(board, opponent)
    if not myMoves and not oppMoves:
        return 9001 if countColor(board, turn) - countColor(board, opponent) > 0 else -9001, None
    elif depth == 0 or (datetime.datetime.now() - startTime).seconds >= timelimit:
        moves = (len(myMoves) - len(oppMoves))/(len(myMoves) + len(oppMoves))
        myCoins = countColor(board, turn)
        oppCoins = countColor(board, opponent)
        coins = (myCoins - oppCoins)/(myCoins + oppCoins)
        myCorners = countCorners(board, turn)
        oppCorners = countCorners(board, turn)
        corners = (myCorners - oppCorners)/(myCorners + oppCorners) if (myCorners + oppCorners) != 0 else 0
        myImportant = countImportant(board, turn)
        oppImportant = countImportant(board, opponent)
        important = (myImportant - oppImportant)/(myImportant + oppImportant) if (myImportant + oppImportant) != 0 else 0
        return 100 * coins + 100 * moves + 100 * corners + 100 * important, None
    if myMoves:
        move = myMoves[0][0]
        for m in myMoves:
            if alpha >= beta:
                break
            value = evaluate(playMove(board, m[0], turn), alpha, beta, opponent, startTime, depth)
            if value > alpha:
                alpha = value
                move = m[0]
        return alpha, move
    else:
        value = evaluate(board, alpha, beta, opponent, startTime, depth)
        return value, None


def evaluate(board, alpha, beta, opponent, startTime, depth):
    for deep in range(depth):
        h = hash(board, opponent, depth)
        if h in table.keys():
            return table[h]
    value = -search(board, -beta, -alpha, opponent, startTime, depth - 1)[0]
    if (datetime.datetime.now() - startTime).seconds < timelimit:
        table[h] = value
    return value


def hash(board, player, depth):
    return hashlib.sha1((str(board) + player + str(depth)).encode("utf-8")).hexdigest()


def playMove(board, move, color):
    copy = deepcopy(board)
    m = isLegal(board, move, color)
    if m is not None:
        indices = toIndices(move)
        copy[indices[0]][indices[1]] = color
        for replace in m[1]:
            opp = toIndices(replace)
            copy[opp[0]][opp[1]] = color
    return copy


def isLegal(board, move, color):
    moves = getLegalMoves(board, color)
    for m in moves:
        if move == m[0]:
            return m
    return None


def playgame():
    turn = dark
    board = [[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', 'l', 'd', ' ', ' ', ' '],
             [' ', ' ', ' ', 'd', 'l', ' ', ' ', ' '],
             [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
             [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']]

    while getLegalMoves(board, player1) or getLegalMoves(board, player2):
        move = None
        printBoard(board)
        print("Legal moves: " + str([move[0] for move in getLegalMoves(board, turn)]))
        while move is None and getLegalMoves(board, turn) != []:
            if turn == player1:
                if opp == 'u' and turn == player1:
                    move = input("What would you like to do (example: a1)?\n")
                else:
                    move = getrandommove(board, turn)
            else:
                move = getAIMove(board, turn)
            if isLegal(board, move, turn) is None:
                move = None
        if move:
            print("Playing move: " + str(move))
            board = playMove(board, move, turn)
        turn = player2 if turn == player1 else player1

    printBoard(board)
    return printResults(board)


AIPoints = 0
randomPoints = 0
color = input("Which color should the AI play as? (l\d, default = d (dark)): ")
opp = input("Should it play against random moves or against you? (r/u, default = r (random)): ")
try:
    timelimit = int(input("How much time should it receive to think? (seconds, default = 1): "))
except ValueError:
    timelimit = 1
depth = 5 if timelimit < 2 else math.ceil(math.log(2 ** timelimit, timelimit)) * 2

if color == dark:
    player2 = dark
    player1 = light
elif color == light:
    player2 = light
    player1 = dark

winner = playgame()
if player2 == winner:
    AIPoints += 1
elif player1 == winner:
    randomPoints += 1
else:
    AIPoints += 1
    randomPoints += 1
print("AI: " + str(AIPoints) + " - Random moves: " + str(randomPoints))
