# CITS1401 Assignment
# Ryan White 20528376 and Ziggy O'Reilly
# https://github.com/RyanWhite04/tiles

from graphics import GraphWin, Point, Rectangle, Text, Entry
from random import random


# Density is the ratio of tiles which start with a two
# Padding is the spacing around ui components
# Most is the largest size of the grid, max was taken

# Rather than having the computer play, I just
# made a function called best move with performs the computers move
# so the user doesn't have to wait and watch, and even works mid human game
# It's a better approach, but not in line with the instructions
def main(title='Tiles', padding=10, density=0.5, size=5, most=10, dimensions={
    'x': 120,      # Pixels left to grid
    'y': 10,       # Pixels down to grid
    'width': 45,   # Width of tile
    'height': 45,  # Height of tile
}):

    # These are used to construct the board
    x = dimensions['x']
    y = dimensions['y']

    #
    width = padding + x + most * dimensions['width']
    height = padding + y + most * dimensions['height']

    # The window is made just big enough to fit all components at max size
    win = GraphWin(title, width, height)

    # The squares for the game
    grid = Grid(dimensions, size).fill(density)

    # Labels which show the score and state of the game
    labels = {
        'score': Text(Point(x/2, 140), '0'),
        'state': Text(Point(x/2, 160), 'Hey There')
    }

    inputs = {
        'density': Input('Density', 0.5, Point(0.7*x, 180), 4, 0, 1),

        # Minimum is 3, because less and the game is stupid
        'size': Input('Size', 5, Point(0.7*x, 200), 4, 3, most)
    }

    # The best, reset and exit buttons
    buttons = [
        Button('Best', 'yellow', {
            'x': [padding, x - padding],
            'y': [10, 30]
        }, best(grid, labels)),
        Button('Reset', 'green', {
            'x': [padding, x - padding],
            'y': [40, 60]
        }, reset(win, grid, labels, inputs, dimensions)),
        Button('Exit', 'red', {
            'x': [padding, x - padding],
            'y': [70, 90]
        }, exit)
    ]

    # Bind mouse event handler to window
    win.bind("<Button-1>", click(win, grid, labels, buttons))

    # Bind keyboard press event handler to window
    # This is so the player can move using the directional keys
    win.bind("<Key>", key(move(grid, labels)))

    # Don't quit on me!
    draw(win, grid, labels, inputs, buttons).mainloop()


# Draw all the components
def draw(win, grid, labels, inputs, buttons):
    grid.draw(win)
    inputs['size'].draw(win)
    inputs['density'].draw(win)
    labels['score'].draw(win)
    labels['state'].draw(win)
    [b.draw(win) for b in buttons]

    if grid.over():
        labels['state'].setText('Game Over')
    return win


# Reset the gameboard including the grid, score, and state
def reset(win, grid, labels, inputs, dimensions):
    def partial():
        labels['score'].setText('0')
        labels['state'].setText('New Game')
        density = inputs['density'].getValue()
        size = inputs['size'].getValue()
        grid.reset(win, density, size, dimensions)
        if grid.over():
            labels['state'].setText('Game Over')
    return partial


# Logs when mouse clicked, alternative to win.getMouse() and while loop
def click(win, grid, labels, buttons):
    def partial(event):
        isClicked = getClickFunction(event.x, event.y)
        clickedTiles = [
            tile.direction
            for tile in grid.tiles
            if isClicked(tile.area)
        ]
        win.focus_set()
        if (clickedTiles and clickedTiles[0]):
            move(grid, labels)(clickedTiles[0])
        return [b.callback() for b in buttons if isClicked(b.area)]
    return partial


# Perform the best move
def best(grid, labels):
    def partial():
        score = int(labels['score'].getText())
        if grid.best():
            labels['score'].setText(str(score + 1))
            labels['state'].setText('Nice Move')
        else:
            labels['score'].setText(str(score - 1))
            labels['state'].setText('Try Again')
        if grid.over():
            labels['state'].setText('Game Over')
    return partial


def move(grid, labels):
    def partial(direction):
        score = int(labels['score'].getText())
        view = grid.views[['up', 'down', 'left', 'right'].index(direction)]
        if grid.move(view):
            labels['score'].setText(str(score + 1))
            labels['state'].setText('Nice Move')
        else:
            labels['score'].setText(str(score - 1))
            labels['state'].setText('Try Again')
        if grid.over():
            labels['state'].setText('Game Over')
    return partial


# Logs when a key is pressed, for diretional controls
def key(move):
    def partial(event):
        keys = {
            '\uf700': 'up',
            '\uf701': 'down',
            '\uf702': 'left',
            '\uf703': 'right'
        }
        if event.char in keys:
            move(keys[event.char])
    return partial


# Return a function that returns true is passed an object containing
# coordinates of the point
def getClickFunction(x, y):
    def partial(button):
        p1 = button.getP1()
        p2 = button.getP2()
        return (p1.x <= x <= p2.x and p1.y <= y <= p2.y)
    return partial


class Grid:

    def __init__(self, dimensions, size):

        size = int(size)
        self.lines = [Line(dimensions, size, i) for i in range(size)]
        self.tiles = [j for i in self.lines for j in i.tiles]
        self.views = [
            self.order(direction)
            for direction
            in ['up', 'down', 'left', 'right']
        ]

    # Alter the order of the lines so that the same move can be performed
    # for instance, a down move is really just an up move when all the
    # tiles are placed in reverse order in their respective lines and the
    # line order is reversed
    def order(self, direction):
        lines = [line.tiles for line in self.lines]
        if direction == 'left' or direction == 'right':
            # Rotate the grid clockwise 90 degrees
            lines = [list(i) for i in zip(*lines[::-1])]
        if direction == 'down' or direction == 'left':
            # Reverse the grid
            lines = [line[::-1] for line in lines[::-1]]

        return [Line().update(line) for line in lines]

    def draw(self, win):
        [line.draw(win) for line in self.lines]
        return self

    def clear(self):
        [line.clear() for line in self.lines]
        return self

    # Fill the grid with a number of twos corresponding to the density
    def fill(self, density):

        def getPosition(i):
            return positions.pop(int(len(positions) * random()))

        tiles = self.tiles
        density = float(density)
        [tile.update(0) for tile in tiles]
        positions = list(range(len(tiles)))
        # Returns an array of the positions in tiles which should start as two
        numbers = list(range(++int(len(tiles) * density)))
        twos = [getPosition(i) for i in numbers]
        [tiles[i].update(2) for i in twos]
        return self

    # TODO Shouldn't need this, but can't figure out how to return grid from
    # events to start using a new grid
    def reset(self, win, density, size, dimensions):

        size = int(size)
        density = float(density)
        self.clear()
        self.lines = [Line(dimensions, size, i) for i in range(size)]
        self.tiles = [j for i in self.lines for j in i.tiles]
        self.views = [
            self.order(direction)
            for direction
            in ['up', 'down', 'left', 'right']
        ]
        return self.fill(density).draw(win)

    # Shift the lines according to the rules of the gameboard
    # a line is a list of tiles along a common axis
    def move(self, view):

        def placeTwo(lines):
            lines[-1].tiles[-1].update(2)
            return lines

        return self.able(view) and placeTwo([line.shift() for line in view])

    # Returns the direction of the best move
    # kinda subjective
    def best(self):
        move = self.move
        able = self.able
        return next((move(view) for view in self.views if able(view)), False)

    # Return true if the game is over
    def over(self):
        views = self.views
        able = self.able
        return not any([able(view) for view in views])

    # Check if all the lines in a view can be shifted
    def able(self, view):
        return all([line.canShift() for line in view])


# A group of tiles which can be shifted and arranged according to their order
class Line:

    def __init__(self, dimensions=None, size=None, i=None):
        if dimensions:
            self.tiles = [Tile(dimensions, size, i, j) for j in range(size)]

    def draw(self, win):
        [tile.draw(win) for tile in self.tiles]
        return self

    def clear(self):
        [tile.clear() for tile in self.tiles]
        return self

    # Shift a line of tiles
    def shift(self):
        self.slide().combine().slide()  # Because not recursive
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

    def update(self, tiles):
        self.tiles = tiles
        return self


# A square and a number with an associated value
class Tile:

    # TODO make it just accept x, y coords and callback
    def __init__(self, dimensions, size, i, j):

        x = dimensions['x']
        y = dimensions['y']
        width = dimensions['width']
        height = dimensions['height']

        # In future might make across able to be different to down
        across = down = size
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


class Input:

    def __init__(self, label, default, point, width, least, most):

        # Because it's monospace font
        face = 'courier'
        self.default = default
        self.min = least
        self.max = most
        self.entry = Entry(point, width)
        self.entry.setFace(face)
        self.entry.setText(default)

        # This only works because the font face is courier (monospace)
        # It more than double the label length, so that when it's center
        # matches that of the input, the text aligns perfectly on the left.
        self.label = Text(point, label + ': ' + (' ' * (6 + len(label))))
        self.label.setFace('courier')

    def draw(self, win):
        self.entry.draw(win)
        self.label.draw(win)
        return self

    def validate(self):
        entry = self.entry
        value = entry.getText()
        try:
            float(value)  # Check to see if it's even a number
        except ValueError:
            value = self.default
            entry.setText(value)
        if float(value) < self.min or float(value) > self.max:
            entry.setText(self.default)
        return self

    def getValue(self):
        return self.validate().entry.getText()


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
