from graphics import GraphWin, Point, Rectangle, Text


def main():

    def key(event):
        print("pressed", repr(event.char))

    def callback(event):
        win.focus_set()
        print("clicked at", event.x, event.y)

    win = GraphWin("My Circle", 600, 600)

    win.bind("<Button-1>", callback)
    win.bind("<Key>", key)

    # best = drawButton(win, 'Best', 'yellow')
    # reset = drawButton(win, 'Reset', 'green')
    # quit = drawButton(win, 'Quit', 'red')
    tiles = drawGrid(win, 0.5, [100, 100, 100, 100, 3, 3])

    while 1:
        isClicked = getClickFunction(win.getMouse())

        if any(map(isClicked, tiles)):
            # Tile was clicked
            move()
        elif isClicked(best):
            # Perform the best move
            best()
        elif isClicked(reset):
            # Start was clicked
            reset(win, tiles)
        elif isClicked(quit):
            # Quit was clicked
            win.close()
            break
        else:
            print('No Button was clicked')


def move(lines):

    def shift(line):
        # Shift a line of tiles
        # TODO Logic for shifting a line
        print('shift a line')

    return map(shift, lines)


def reset(win, tiles=[]):
    map(lambda tile: tile.clear(), tiles)
    return drawGrid(win, 0.5, [100, 100, 100, 100, 5, 5])
    print('Resetting the game')


def drawButton(win, label):
    button = Rectangle(Point(), Point())
    button.draw(win)

    text = Text(label)
    text.draw(win)
    return button


def drawGrid(win, difficulty, dimensions):
    [
        left,
        down,
        width,
        height,
        squaresAcross,
        squaresDown,
    ] = dimensions

    tiles = []
    for i in range(0, squaresAcross):
        for j in range(0, squaresDown):
            point1 = Point(left + width * i, down + height * j)
            point2 = Point(left + width * (i+1), down + height * (j+1))
            square = Rectangle(point1, point2)
            square.draw(win)

            point3 = Point(left + width * (i + 1/2), down + height * (j + 1/2))
            number = Text(point3, '2')
            number.draw(win)
            tiles.append({
                square: square,
                number: number,
            })
    return tiles


def getClickFunction(point):
    def isClicked(button):
        p1 = button.getP1()
        p2 = button.getP2()
        return (p1.x <= point.x <= p2.x and p1.y <= point.y <= p2.y)
    return isClicked

main()
