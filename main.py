import asyncio
import curses
import os
import random
import time
from itertools import cycle
from statistics import median

from curses_tools import draw_frame, read_controls, get_frame_size


async def animate_spaceship(canvas, start_row, start_column, frames):
    border = 1

    row, column = start_row, start_column

    # canvas.getmaxyx() возвращает длину/ширину окна отрисовки.
    # Поэтому далее определяются переменные-границы для координат.
    height, width = canvas.getmaxyx()

    for frame in cycle(frames):
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        row += rows_direction
        column += columns_direction

        frame_rows, frame_cols = get_frame_size(frame)
        bottom_frame_edge = height - frame_rows - border
        right_frame_edge = width - frame_cols - border
        top_frame_edge = border
        left_frame_edge = border

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
    tic_timeout = 0.1
    stars_number = 100
    border = 1
    frames_number = 2

    canvas.nodelay(True)
    curses.curs_set(False)
    stars = '*:+.'

    # canvas.getmaxyx() возвращает длину/ширину окна отрисовки.
    # Поэтому далее определяются переменные-границы для координат.
    height, width = canvas.getmaxyx()
    bottom_frame_edge = height - border - 1
    right_frame_edge = width - border - 1
    top_frame_edge = border
    left_frame_edge = border
    frame_center = (height - 1) // 2, (width - 1) // 2

    coroutines = []
    frames = []

    rocket_frames_path = 'frames/rocket_frames/'
    rocket_frames_names = os.listdir(rocket_frames_path)
    for rocket_frames_name in rocket_frames_names:
        with open(f'{rocket_frames_path}{rocket_frames_name}', 'r') as file:
            frame = file.read()
        frames.extend([frame for _ in range(frames_number)])

    spaceship_coroutine = animate_spaceship(canvas, *frame_center, frames)
    fire_coroutine = fire(canvas, *frame_center)

    coroutines.append(spaceship_coroutine)
    coroutines.append(fire_coroutine)

    for _ in range(stars_number):
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
        time.sleep(tic_timeout)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
