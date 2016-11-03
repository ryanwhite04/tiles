from graphics import GraphWin, Point, Rectangle, Text
from random import random


def main():

    def key(event):
        print("pressed", repr(event.char))

    def click(win):
        def callback(event):
            win.focus_set()
            print("clicked at", event.x, event.y)

    win = GraphWin("Tile Game", 600, 600)

    win.bind("<Button-1>", click(win))
    win.bind("<Key>", key)

    best = drawButton(win, 'Best', 'yellow', [10, 10, 110, 30])
    resetButton = drawButton(win, 'Reset', 'green', [10, 40, 110, 60])
    quit = drawButton(win, 'Quit', 'red', [10, 70, 110, 90])

    # map(lambda shape: shape.draw(win), [best, reset, quit])

    score = Text(Point(60, 110), '')
    score.draw(win)

    state = Text(Point(60, 130), '')
    state.draw(win)

    lines = reset(win, score, state, 0.5)

    while 1:
        isClicked = getClickFunction(win.getMouse())

        def check(tile):
            if (isClicked(tile['square'])):
                return tile['direction']
            else:
                return False
        clickedTiles = list(filter(check, [j for i in lines for j in i]))
        if (clickedTiles and clickedTiles[0]['direction']):
            move(order(clickedTiles[0]['direction'], lines), score, state)
        if isClicked(best):
            # Perform the best move
            move(order(best(), lines), score, state)
        elif isClicked(resetButton):
            # Start was clicked
            lines = reset(win, score, state, 0.5, lines)
        elif isClicked(quit):
            # Quit was clicked
            win.close()
            break
        else:
            print('No Button was clicked')


# Alter the order of the lines so that the same move can be performed
# for instance, a down move is really just an up move when all the tiles are
# placed in reverse order in their respective lines and the line order is
# reversed
def order(direction, lines):
    if direction == 'left' or direction == 'right':
        # Rotate the grid clockwise 90 degrees
        lines = list(map(list, zip(*lines[::-1])))
    if direction == 'down' or direction == 'left':
        # Reverse the grid
        lines = list(map(lambda line: line[::-1], lines[::-1]))
    return lines


# Shift the lines according to the rules of the gameboard
# a line is a list of tiles along a common axis
def move(lines, score, state):

    # Shift a line of tiles
    def shift(line):

        def slide(line):
            for i in range(len(line) - 1):
                first = line[i]['number']
                second = line[i+1]['number']
                if (first.getText() == '' and second.getText() != ''):
                    first.setText(second.getText())
                    second.setText('')
            for i in range(len(line) - 1):
                for j in range(i + 1, len(line)):
                    first = line[i]['number']
                    other = line[j]['number']
                    if (first.getText() == '' and second.getText() != ''):
                        first.setText(other.getText())
                        second.setText('')
            return line

        def combine(line):
            for i in range(len(line) - 1):
                first = line[i]['number']
                second = line[i+1]['number']
                if (first.getText() == second.getText() != ''):
                    first.setText(str(2 * int(second.getText())))
                    second.setText('')
            return line

        slide(combine(slide(line)))  # Because not recursive
        # A tile can only participate in one combination during any given move
        return line

    def placeTwo(lines):
        lines[-1][-1]['number'].setText('2')
        return lines

    def canShift(line):

        # Return true if the line has at least 1 empty square before a
        # non-empty square
        def hasEmptyBeforeNonEmpty(line):
            for i in range(len(line) - 1):
                for j in range(i + 1, len(line)):
                    first = line[i]['number'].getText()
                    other = line[j]['number'].getText()
                    if (first == '' and other != ''):
                        return True
            return False

        # Return true if there is at least 1 pair of consecutive squares with
        # the same number
        def hasPair(line):
            for i in range(len(line) - 1):
                first = line[i]['number'].getText()
                second = line[i + 1]['number'].getText()
                if (first == second and second != ''):
                    return True
            return False
        empty = hasEmptyBeforeNonEmpty(line)
        pair = hasPair(line)
        print(empty, pair)
        return hasEmptyBeforeNonEmpty(line) or hasPair(line)

    if all(map(canShift, lines)):
        placeTwo(list(map(shift, lines)))
        score.setText(str(int(score.getText()) + 1))
        state.setText('Nice Move')
    else:
        score.setText(str(int(score.getText()) - 1))
        state.setText('Try Again')
    return lines


# Returns the directions of the best move
# kinda subjective
def best(lines):
    # TODO
    return 'left'


# Reset the gameboard including the grid, score, and state
def reset(win, score, state, difficulty, lines=[]):

    def draw(win, lines):
        for line in lines:
            for tile in line:
                tile['square'].draw(win)
                tile['number'].draw(win)
        return lines

    def clear(lines):
        for line in lines:
            for tile in line:
                tile['square'].undraw()
                tile['number'].undraw()
        return lines

    score.setText('0')
    state.setText('New Game')
    clear(lines)
    lines = draw(win, populate(difficulty, getGrid(120, 10, 50, 50, 3, 3)))

    return lines


# Create a grid of squares according to the arguments
def getGrid(x, y, width, height, across, down):
    # Returns a list of tiles
    def getLine(i):
        # Returns a tile
        def getTile(j):
            number = Text(Point(x+width*(i+1/2), y+height*(j+1/2)), '')
            return {
                'square': Rectangle(
                    Point(x + width * i, y + height * j),
                    Point(x + width * (i+1), y + height * (j+1))),
                'number': number,
                'direction': assign(i, j, across, down)
            }
        return list(map(getTile, list(range(down))))
    return list(map(getLine, list(range(across))))


# Fill the grid with a number of twos corresponding to the difficulty
def populate(difficulty, lines):

    # This just flattens the 2d array to make it easier to work with
    # This would make a nice exam question
    tiles = [j for i in lines for j in i]
    positions = list(range(len(tiles)))

    def getPosition(i):
        return positions.pop(int(len(positions) * random()))

    # Returns an array of the positions in tiles which should start as two
    twos = map(getPosition, list(range(++int(len(tiles) * difficulty))))
    list(map(lambda i: tiles[i]['number'].setText('2'), list(twos)))

    # return the 2d list, we don't need the 1d list of tiles anymore
    return lines


# Given the coordinates in the grid, assign a direction for a move to perform
# This could be simpler, TODO
def assign(i, j, across, down):
    if (i == 0 and j != 0 and j != (down - 1)):
        return 'left'
    elif (i == (across - 1) and j != 0 and j != (down - 1)):
        return 'right'
    elif (j == 0 and i != 0 and i != (across - 1)):
        return 'up'
    elif (j == (down - 1) and i != 0 and i != (across - 1)):
        return 'down'
    else:
        return False


# Draw a button given the following arguments
def drawButton(win, label, color, coordinates):
    [x1, y1, x2, y2] = coordinates
    button = Rectangle(Point(x1, y1), Point(x2, y2))
    button.setFill(color)
    button.draw(win)

    text = Text(Point((x1 + x2)/2, (y1 + y2)/2), label)
    text.draw(win)

    return button


# Return a function that returns true is passed an object containing the
# coordinates of the point
def getClickFunction(point):
    def isClicked(button):
        p1 = button.getP1()
        p2 = button.getP2()
        return (p1.x <= point.x <= p2.x and p1.y <= point.y <= p2.y)
    return isClicked

main()

# lines = [[1, 2], [3, 4]]
# print('up', order('up', lines))
# print([[1, 2], [3, 4]])
# print('down', order('down', lines))
# print([[4, 3], [2, 1]])
# print('right', order('right', lines))
# print([[3, 1], [4, 2]])
# print('left', order('left', lines))
# print([[2, 4], [1, 3]])
