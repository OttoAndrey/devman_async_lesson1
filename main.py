import time
import curses
import asyncio
import random
from itertools import cycle
from curses_tools import draw_frame, read_controls


async def animate_spaceship(canvas, start_row, start_column, frames):
    row, column = start_row, start_column
    for frame in cycle(frames):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        row += rows_direction
        column += columns_direction
        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)
            

async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(0, 4):
            await asyncio.sleep(0)  

        canvas.addstr(row, column, symbol)
        for _ in range(0, 1):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(0, random.randint(0, 2)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(0, 1):
            await asyncio.sleep(0)


def draw(canvas):
    canvas.nodelay(True)
    with open("frames/rocket_frame_1.txt", "r") as my_file:
        rocket_frame_1 = my_file.read()

    with open("frames/rocket_frame_2.txt", "r") as my_file:
        rocket_frame_2 = my_file.read()

    frames = [rocket_frame_1, rocket_frame_2]

    curses.curs_set(False)
    stars = '*:+.'
    max_row, max_col = canvas.getmaxyx()

    coroutines = []
    coroutine_spaceship = animate_spaceship(canvas, max_row/2, max_col/2, frames)
    coroutine_fire = fire(canvas, max_row-2, (max_col-2)/2)

    coroutines.append(coroutine_spaceship)
    coroutines.append(coroutine_fire)

    for _ in range(0, 100):
        row = random.randint(1, max_row-2)
        column = random.randint(1, max_col-2)
        coroutine_blink = blink(canvas, row, column, random.choice(stars))
        coroutines.append(coroutine_blink)

    canvas.border()
    
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
