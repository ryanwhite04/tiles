from graphics import GraphWin, Point, Rectangle, Text
from random import random
from functools import partial


def main():

    # Logs when a key is pressed, for diretional controls
    def key(event):
        print("pressed", repr(event.char))

    # Logs when mouse clicked, alternative to win.getMouse() and while loop
    # Might use later, I prefer waiting for callbacks
    def click(win):
        def callback(event):
            win.focus_set()
            print("clicked at", event.x, event.y)

    # Return a function that returns true is passed an object containing the
    # coordinates of the point
    def getClickFunction(point):
        def isClicked(button):
            p1 = button.getP1()
            p2 = button.getP2()
            return (p1.x <= point.x <= p2.x and p1.y <= point.y <= p2.y)
        return isClicked

    win = GraphWin("Tile Game", 600, 600)
    win.bind("<Button-1>", click(win))
    win.bind("<Key>", key)
    labels = {
        'score': Text(Point(60, 110), '0'),
        'state': Text(Point(60, 130), 'New Game')
    }
    difficulty = 0.5
    dimensions = {
        'x': 120,
        'y': 10,
        'width': 50,
        'height': 50,
        'across': 3,
        'down': 3
    }
    grid = Grid(dimensions).populate(0.5).draw(win)

    # Returns the directions of the best move
    # kinda subjective
    def best():
        return 'left'

    # Reset the gameboard including the grid, score, and state
    def reset():
        print('reset')
        labels['score'].setText('0')
        labels['state'].setText('New Game')
        grid.reset(win, difficulty, dimensions)
        return True

    # Create all the buttons, including their callbacks if clicked
    buttons = [
        Button('Best', 'yellow', {
            'x': [10, 110],
            'y': [10, 30]
        }, best),
        Button('Reset', 'green', {
            'x': [10, 110],
            'y': [40, 60]
        }, reset),
        Button('Quit', 'red', {
            'x': [10, 110],
            'y': [70, 90]
        }, quit)
    ]

    # Draw all the buttons and labels
    [button.draw(win) for button in buttons]
    labels['score'].draw(win)
    labels['state'].draw(win)

    while 1:
        isClicked = getClickFunction(win.getMouse())

        clickedTiles = [
            tile.direction
            for tile in grid.tiles
            if isClicked(tile.area)
        ]
        if (clickedTiles and clickedTiles[0]):
            move(order(clickedTiles[0], grid.lines), labels)
        [isClicked(b.area) and b.callback() for b in buttons]


# Alter the order of the lines so that the same move can be performed
# for instance, a down move is really just an up move when all the tiles are
# placed in reverse order in their respective lines and the line order is
# reversed
def order(direction, lines):
    print('Direction', direction)
    if direction == 'left' or direction == 'right':
        # Rotate the grid clockwise 90 degrees
        lines = [list(i) for i in zip(*lines.tiles[::-1])]
    if direction == 'down' or direction == 'left':
        # Reverse the grid

        lines = list(map(lambda line: line[::-1], lines[::-1]))
    return lines


# Shift the lines according to the rules of the gameboard
# a line is a list of tiles along a common axis
def move(lines, labels):

    score = labels['score']
    state = labels['state']

    def placeTwo(lines):
        lines[-1].tiles[-1].update(2)
        return lines

    if all(map(lambda line: line.canShift(), lines)):
        placeTwo(list(map(lambda line: line.shift(), lines)))
        score.setText(str(int(score.getText()) + 1))
        state.setText('Nice Move')
    else:
        score.setText(str(int(score.getText()) - 1))
        state.setText('Try Again')
    return lines


# Create a grid of squares according to the arguments
class Grid:

    def __init__(self, dimensions):
        across = dimensions['across']
        self.lines = [Line(dimensions, i) for i in range(across)]
        self.tiles = [j for i in self.lines for j in i.tiles]

    def draw(self, win):
        map(lambda line: line.draw(win), self.lines)
        return self

    def clear(self):
        map(lambda line: line.clear(), self.lines)
        return self

    # Fill the grid with a number of twos corresponding to the difficulty
    def populate(self, difficulty):

        def getPosition(i):
            return positions.pop(int(len(positions) * random()))

        tiles = self.tiles

        [tile.update(0) for tile in tiles]
        positions = list(range(len(tiles)))
        # Returns an array of the positions in tiles which should start as two
        numbers = list(range(++int(len(tiles) * difficulty)))
        twos = [getPosition(i) for i in numbers]
        [tiles[i].update(2) for i in twos]
        return self

    def reset(self, win, difficulty, dimensions):
        across = dimensions['across']
        self.clear()
        self.lines = [Line(dimensions, i) for i in range(across)]
        self.tiles = [j for i in self.lines for j in i.tiles]
        return self.populate(difficulty).draw(win)


class Line:

    def __init__(self, dimensions, i):
        down = dimensions['down']
        self.tiles = [Tile(dimensions, i, j) for j in range(down)]

    def draw(self, win):
        [tile.draw(win) for tile in self.tiles]
        return self

    def clear(self):
        [tile.clear() for tile in self.tiles]
        return self

    # Shift a line of tiles
    def shift(self):
        self.slide(self.combine(self.slide()))  # Because not recursive
        # A tile can only participate in one combination during any given move
        return self

    def slide(self):
        tiles = self.tiles

        for i in range(len(tiles) - 1):
            for j in range(i + 1, len(tiles)):
                first = tiles[i]
                second = tiles[j]
                if (not first.value and second.value):
                    first.update(second.value)
                    second.update(0)
        return self

    def combine(self):
        tiles = self.tiles
        for i in range(len(tiles) - 1):
            first = tiles[i]
            second = tiles[i+1]
            if (first.value == second.value and first.value > 0):
                first.double()
                second.update(0)
        return self

    def canShift(self):
        return self.hasEmptyBeforeNonEmpty() or self.hasPair()

    # Return true if the line has at least 1 empty square before a
    # non-empty square
    def hasEmptyBeforeNonEmpty(self):
        tiles = self.tiles
        for i in range(len(tiles) - 1):
            for j in range(i + 1, len(tiles)):
                if (not tiles[i].value and tiles[j].value):
                    return True
        return False

    # Return true if there is at least 1 pair of consecutive squares with
    # the same number
    def hasPair(self):
        tiles = self.tiles
        for i in range(len(tiles) - 1):
            if (tiles[i].value == tiles[i + 1].value and tiles[i].value):
                return True
        return False


class Tile:

    def __init__(self, dimensions, i, j):

        x = dimensions['x']
        y = dimensions['y']
        width = dimensions['width']
        height = dimensions['height']
        across = dimensions['across']
        down = dimensions['down']

        self.area = Rectangle(
            Point(x + width * i, y + height * j),
            Point(x + width * (i+1), y + height * (j+1)))
        self.text = Text(Point(x+width*(i+1/2), y+height*(j+1/2)), '')
        self.value = 0
        self.assign(i, j, across, down)

    def draw(self, win):
        self.area.draw(win)
        self.text.draw(win)
        return self

    def clear(self):
        self.area.undraw()
        self.text.undraw()
        return self

    def update(self, number):
        self.value = number
        if number > 0:
            self.text.setText(str(number))
        else:
            self.text.setText('')
        return self

    def double(self):
        self.update(2 * self.value)
        return self

    # Given the coordinates in the grid, assign direction for a move to perform
    # This could be simpler, TODO
    def assign(self, i, j, across, down):
        if (i == 0 and j != 0 and j != (down - 1)):
            self.direction = 'left'
        elif (i == (across - 1) and j != 0 and j != (down - 1)):
            self.direction = 'right'
        elif (j == 0 and i != 0 and i != (across - 1)):
            self.direction = 'up'
        elif (j == (down - 1) and i != 0 and i != (across - 1)):
            self.direction = 'down'
        else:
            self.direction = False


# Draw a button given the following arguments
class Button:

    def __init__(self, label, color, coordinates, callback):
        x = coordinates['x']
        y = coordinates['y']
        self.area = Rectangle(Point(x[0], y[0]), Point(x[1], y[1]))
        self.text = Text(Point((x[0] + x[1])/2, (y[0] + y[1])/2), label)
        self.fill(color)
        self.callback = callback

    def fill(self, color):
        self.area.setFill(color)
        return self

    def draw(self, win):
        self.area.draw(win)
        self.text.draw(win)
        return self

    def clear(self):
        self.area.undraw()
        self.text.undraw()
        return self

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
