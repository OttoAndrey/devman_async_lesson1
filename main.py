import asyncio
import curses
import os
import random
import time
from itertools import cycle
from statistics import median

from curses_tools import draw_frame, read_controls, get_frame_size


async def animate_spaceship(canvas, start_row, start_column, frames):
    BORDER = 1

    row, column = start_row, start_column

    # canvas.getmaxyx() возвращает длину/ширину окна отрисовки.
    # Поэтому далее определяются переменные-границы для координат.
    height, width = canvas.getmaxyx()

    for frame in cycle(frames):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        row += rows_direction
        column += columns_direction

        frame_rows, frame_cols = get_frame_size(frame)
        bottom_frame_edge = height - frame_rows - BORDER
        right_frame_edge = width - frame_cols - BORDER
        top_frame_edge = BORDER
        left_frame_edge = BORDER

        row = median([top_frame_edge, row, bottom_frame_edge])
        column = median([left_frame_edge, column, right_frame_edge])

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
        for _ in range(3):
            await asyncio.sleep(0)  

        canvas.addstr(row, column, symbol)
        for _ in range(1):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(random.randint(0, 2)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(1):
            await asyncio.sleep(0)


def draw(canvas):
    TIC_TIMEOUT = 0.1
    STARS_NUMBER = 100
    BORDER = 1
    FRAME_CENTER = 2
    FRAMES_NUMBER = 2

    canvas.nodelay(True)
    curses.curs_set(False)
    stars = '*:+.'

    # canvas.getmaxyx() возвращает длину/ширину окна отрисовки.
    # Поэтому далее определяются переменные-границы для координат.
    height, width = canvas.getmaxyx()
    bottom_frame_edge = height - BORDER - 1
    right_frame_edge = width - BORDER - 1
    top_frame_edge = BORDER
    left_frame_edge = BORDER

    coroutines = []
    frames = []

    rocket_frames_path = 'frames/rocket_frames/'
    rocket_frames_names = os.listdir(rocket_frames_path)
    for rocket_frames_name in rocket_frames_names:
        with open(f'{rocket_frames_path}{rocket_frames_name}', 'r') as file:
            frame = file.read()
        frames.extend([frame for _ in range(FRAMES_NUMBER)])

    spaceship_coroutine = animate_spaceship(canvas, height/FRAME_CENTER, width/FRAME_CENTER, frames)
    fire_coroutine = fire(canvas, bottom_frame_edge, right_frame_edge/FRAME_CENTER)

    coroutines.append(spaceship_coroutine)
    coroutines.append(fire_coroutine)

    for _ in range(STARS_NUMBER):
        row = random.randint(top_frame_edge, bottom_frame_edge)
        column = random.randint(left_frame_edge, right_frame_edge)
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
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
