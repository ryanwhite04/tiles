# CITS1401 Assignment
# Ryan White 20528376 and Ziggy O'Reilly
# https://github.com/RyanWhite04/tiles

from graphics import GraphWin, Point, Rectangle, Text
from random import random


def main(title='Tile Game', padding=10, density=0.5, dimensions={
    'x': 120,      # Pixels left to grid
    'y': 10,       # Pixels down to grid
    'width': 45,   # Width of tile
    'height': 45,  # Height of tile
    'across': 5,   # Tiles across, min 3
    'down': 5      # Tiles down, min 3
}):

    x = dimensions['x']
    y = dimensions['y']
    width = padding + x + dimensions['across'] * dimensions['width']
    height = padding + y + dimensions['down'] * dimensions['height']
    win = GraphWin(title, width, height)
    grid = Grid(dimensions).populate(density)
    labels = {
        'score': Text(Point(x/2, 110), '0'),
        'state': Text(Point(x/2, 130), 'New Game')
    }

    # Returns the direction of the best move
    # kinda subjective
    def best():
        return 'left'

    # Reset the gameboard including the grid, score, and state
    def reset():
        print('reset')
        labels['score'].setText('0')
        labels['state'].setText('New Game')
        grid.reset(win, density, dimensions)
        return True

    win.bind("<Button-1>", click(win, grid, labels, [
        Button('Best', 'yellow', {
            'x': [padding, x - padding],
            'y': [10, 30]
        }, best),
        Button('Reset', 'green', {
            'x': [padding, x - padding],
            'y': [40, 60]
        }, reset),
        Button('Exit', 'red', {
            'x': [padding, x - padding],
            'y': [70, 90]
        }, exit)
    ]))
    win.mainloop()


# Logs when mouse clicked, alternative to win.getMouse() and while loop
def click(win, grid, labels, buttons):

    def move(direction):
        score = int(labels['score'].getText())
        if grid.move(direction):
            labels['score'].setText(str(score + 1))
            labels['state'].setText('Nice Move')
        else:
            labels['score'].setText(str(score - 1))
            labels['state'].setText('Try Again')

    # Logs when a key is pressed, for diretional controls
    def key(grid):
        def callback(event):
            keys = {
                '\uf700': 'up',
                '\uf701': 'down',
                '\uf702': 'left',
                '\uf703': 'right'
            }
            if event.char in keys:
                move(keys[event.char])
        return callback

    win.bind("<Key>", key(grid))

    # Draw everything
    grid.draw(win)
    labels['score'].draw(win)
    labels['state'].draw(win)
    [b.draw(win) for b in buttons]

    # Main event loop
    def callback(event):

        # Return a function that returns true is passed an object containing
        # coordinates of the point
        def getClickFunction(x, y):
            def isClicked(button):
                p1 = button.getP1()
                p2 = button.getP2()
                return (p1.x <= x <= p2.x and p1.y <= y <= p2.y)
            return isClicked

        isClicked = getClickFunction(event.x, event.y)
        clickedTiles = [
            tile.direction
            for tile in grid.tiles
            if isClicked(tile.area)
        ]
        if (clickedTiles and clickedTiles[0]):
            move(clickedTiles[0])
        [b.callback() for b in buttons if isClicked(b.area)]
        win.focus_set()
    return callback


class Grid:

    def __init__(self, dimensions):
        across = dimensions['across']
        self.lines = [Line(dimensions, i) for i in range(across)]
        self.tiles = [j for i in self.lines for j in i.tiles]

    def draw(self, win):
        [line.draw(win) for line in self.lines]
        return self

    def clear(self):
        [line.clear() for line in self.lines]
        return self

    # Fill the grid with a number of twos corresponding to the density
    def populate(self, density):

        def getPosition(i):
            return positions.pop(int(len(positions) * random()))

        tiles = self.tiles

        [tile.update(0) for tile in tiles]
        positions = list(range(len(tiles)))
        # Returns an array of the positions in tiles which should start as two
        numbers = list(range(++int(len(tiles) * density)))
        twos = [getPosition(i) for i in numbers]
        [tiles[i].update(2) for i in twos]
        return self

    def reset(self, win, density, dimensions):
        across = dimensions['across']
        self.clear()
        self.lines = [Line(dimensions, i) for i in range(across)]
        self.tiles = [j for i in self.lines for j in i.tiles]
        return self.populate(density).draw(win)

    # Shift the lines according to the rules of the gameboard
    # a line is a list of tiles along a common axis
    def move(self, direction):

        # Alter the order of the lines so that the same move can be performed
        # for instance, a down move is really just an up move when all the
        # tiles are placed in reverse order in their respective lines and the
        # line order is reversed
        def order(direction, unordered):
            lines = [line.tiles for line in unordered]
            if direction == 'left' or direction == 'right':
                # Rotate the grid clockwise 90 degrees
                lines = [list(i) for i in zip(*lines[::-1])]
            if direction == 'down' or direction == 'left':
                # Reverse the grid
                lines = [line[::-1] for line in lines[::-1]]

            return [Line().update(line) for line in lines]

        def placeTwo(lines):
            lines[-1].tiles[-1].update(2)
            return lines

        lines = order(direction, self.lines)
        if all([line.canShift() for line in lines]):
            placeTwo([line.shift() for line in lines])
            return True
        else:
            return False


class Line:

    def __init__(self, dimensions=None, i=None):
        if dimensions:
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
