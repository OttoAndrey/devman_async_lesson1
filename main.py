import asyncio
import curses
import os
import random
import time
from itertools import cycle
from statistics import median

from curses_tools import draw_frame, read_controls, get_frame_size


async def animate_spaceship(canvas, start_row, start_column, frames):
    row, column = start_row, start_column
    max_rows, max_columns = canvas.getmaxyx()
    max_rows -= 1
    max_columns -= 1

    for frame in cycle(frames):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        frame_rows, frames_cols = get_frame_size(frame)
        row += rows_direction
        column += columns_direction

        row = median([1, row, max_rows-frame_rows])
        column = median([1, column, max_columns-frames_cols])

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
        for _ in range(0, 3):
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
    curses.curs_set(False)
    stars = '*:+.'
    max_rows, max_cols = canvas.getmaxyx()
    coroutines = []
    frames = []

    rocket_frames_path = 'frames/rocket_frames/'
    rocket_frames_names = os.listdir(rocket_frames_path)
    for rocket_frames_name in rocket_frames_names:
        with open(f'{rocket_frames_path}{rocket_frames_name}', 'r') as frame:
            frames.append(frame.read())

    spaceship_coroutine = animate_spaceship(canvas, max_rows/2, max_cols/2, frames)
    fire_coroutine = fire(canvas, max_rows-2, (max_cols-2)/2)

    coroutines.append(spaceship_coroutine)
    coroutines.append(fire_coroutine)

    for _ in range(0, 100):
        row = random.randint(1, max_rows-2)
        column = random.randint(1, max_cols-2)
        blink_coroutine = blink(canvas, row, column, random.choice(stars))
        coroutines.append(blink_coroutine)

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
