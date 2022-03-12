# Eric Anderson (100704730)
"""2 songs have been added in the audio folder for testing, but any set of wave files should work.
   Also, closing the progress bar speeds up the visualization."""

import librosa
from tkinter import Tk, Canvas, Scrollbar, TclError
import os
import math
from progress_bar import Progress
import warnings
warnings.filterwarnings("ignore")


def remove_star(data):
    """Removes all astrix from a list and returns a list"""
    no_stars_list = []
    for s_sample in data:
        if s_sample != '*':
            no_stars_list.append(s_sample)
    return no_stars_list


def scale_list(data):
    """Scales a list based on the max value in the list and returns a list"""
    scaled_list = []
    max_val = max(remove_star(data))
    for s_sample in data:
        if s_sample != '*':
            scaled_list.append(s_sample / max_val)
        else:
            scaled_list.append(s_sample)
    return scaled_list


def remove_0x(hex_value):
    """Takes in a hex value. Removes the 0x from the hex value and returns a string"""
    str_hex = ''
    for index, e in enumerate(hex_value):
        if e != 'x' and index != 0:
            str_hex += e
    if len(str_hex) == 1:
        return '0' + str_hex
    return str_hex


def hsl_to_hex(hue, saturation, lightness):
    """Takes in a hsl value and returns a hex value"""
    C = (1 - abs((2 * lightness) - 1)) * saturation
    X = C * (1 - abs(((hue / 60) % 2) - 1))
    m = lightness - (C/2)
    temp_rgb = ()
    if 0 <= hue < 60:
        temp_rgb = (C, X, 0)
    elif 60 <= hue < 120:
        temp_rgb = (X, C, 0)
    elif 120 <= hue < 180:
        temp_rgb = (0, C, X)
    elif 180 <= hue < 240:
        temp_rgb = (0, X, C)
    elif 240 <= hue < 300:
        temp_rgb = (X, 0, C)
    elif 300 <= hue < 360:
        temp_rgb = (C, 0, X)
    r = int((temp_rgb[0] + m) * 255)
    g = int((temp_rgb[1] + m) * 255)
    b = int((temp_rgb[2] + m) * 255)
    colour_hex = f'#{remove_0x(hex(r)) + remove_0x(hex(g)) + remove_0x(hex(b))}'
    return colour_hex


def triangle(canvas_name, x, y, w, h, fill):
    """Creates the reference point of a canvas triangle, so it only uses one x, y coordinate"""
    x0 = x
    y0 = y
    x1 = x + (w / 2)
    y1 = y + h
    x2 = x + w
    y2 = y
    canvas_name.create_polygon(x0, y0, x1, y1, x2, y2, fill=fill)


def visualize(r, canvas_name, pb, data, sx, sy, w, h, xo, yo, axis_s):
    """Prints triangles on a canvas with different colours, based on the Hz that each data point represents"""
    movement_x = 0
    movement_y = 0
    y_size = axis_s - sy
    t_num = math.floor(y_size / (h + yo))
    t_count = 0
    back_up = False

    number_in_column = math.floor((axis_s - sy) / (h + yo))
    number_of_columns = int((int(round(len(data) / number_in_column, 0) * (w + xo)) + sx) / (xo + w))
    columns_in_view = 282
    percent_move = columns_in_view/number_of_columns
    current_movement = percent_move
    column_count = 0

    for count, s_sample in enumerate(data):
        try:
            pb.bar_update(count, len(data))
        except TclError:
            pass
        if s_sample == '*':
            # Prints a song endpoint triangle on the canvas
            triangle(canvas_name, (movement_x + sx), (movement_y + sy), w, h, hsl_to_hex(0, 0, 0))
        else:
            # Prints a triangle on the canvas
            triangle(canvas_name, (movement_x + sx), (movement_y + sy), w, h, hsl_to_hex(s_sample * 285, 1, 0.5))

        canvas_name.update()

        if back_up is False:
            movement_y += (h + yo)
            t_count += 1

        elif back_up is True:
            movement_y += (h - yo)
            t_count -= 1

        if t_count == t_num:
            movement_x += w + xo
            back_up = True
            h *= -1
            column_count += 1
        elif t_count == 0:
            movement_x += w + xo
            back_up = False
            h *= -1
            column_count += 1

        if column_count >= columns_in_view:  # Shifts the window if it is full of data
            r.update_idletasks()
            canvas_name.xview_moveto(f'{current_movement}')
            current_movement += percent_move
            column_count = 0


def file_load(p):
    """Loads all the files in a folder and does data preprocessing"""
    dir_data = os.listdir(p)
    spectral_centroids_s = []
    for i, file in enumerate(dir_data):
        audio_data = p + file
        try:
            data, sr = librosa.load(audio_data)
            print(f'{file} \u001b[32mData Loaded\u001b[0m')
            spectral_centroids = list(librosa.feature.spectral_centroid(y=data, sr=sr)[0])
            for sample in spectral_centroids:
                spectral_centroids_s.append(sample)
            spectral_centroids_s.append('*')
        except EOFError:
            print(f'{file} \u001b[31m Failed to Load\u001b[0m')
    return scale_list(spectral_centroids_s), remove_star(spectral_centroids_s)


def initialize_window(r, sc_s, sx, sy, w, h, xo, yo, axis_s):
    """Creates the windows necessary to show the visualization"""
    r.config(background='black')
    r.geometry("1700x905")
    r.title('Music Visualized')

    c_legend = Canvas(r, width='1700', height='50', bg='white', highlightbackground="white")
    c_legend.pack(side='top')

    c = Canvas(r, width='1700', height='850', bg='black', highlightbackground="black")
    number_in_column = math.floor((axis_s - sy) / (h + yo))
    scrollbar_x = int(round(len(sc_s) / number_in_column, 0) * (w + xo)) + sx
    c.configure(scrollregion=(0, 0, scrollbar_x, 0))
    scrollbar = Scrollbar(r, orient='horizontal', command=c.xview)
    c.config(xscrollcommand=scrollbar.set)
    scrollbar.pack(side='top', fill='x')
    c.pack()
    return c, c_legend


def colour_bar(canvas_name, x_count, side_size, window_mid_point, low_hz, high_hz):
    """Makes and renders the Hz legend"""
    colour_samples = int((window_mid_point - x_count) * 2 / side_size)
    canvas_name.create_text(x_count - 80, 30, text=f'{round(low_hz, 1)} Hz', fill='black', justify='center', font=("Purisa", 20))
    for i in range(colour_samples):
        canvas_name.create_rectangle(x_count, 10, x_count + side_size, 50, fill=hsl_to_hex(i/colour_samples * 285, 1, 0.5))
        x_count += side_size
    canvas_name.create_text(x_count + 80, 30, text=f'{round(high_hz, 1)} Hz', fill='black', justify='center', font=("Purisa", 20))


if __name__ == '__main__':
    progress_b = Progress()
    root = Tk()

    path = input('Enter a path to a directory with only .wav files in it: ')
    try:
        sc = file_load(path)
    except FileNotFoundError:
        print(f"\u001b[33mError with '{path}' so trying ./audio/\u001b[0m")
        try:
            sc = file_load('./audio/')
        except ValueError:
            print('\u001b[33mThere are no audio files in ./audio/\u001b[0m')
            exit()

    start_x = 5
    start_y = 5
    width = 4        # Can be modified to show different results
    height = 5       # Can be modified to show different results
    x_offset = 2     # Can be modified to show different results
    y_offset = 2     # Can be modified to show different results
    axis_size = 830

    canvas = initialize_window(root, sc[0], start_x, start_y, width, height, x_offset, y_offset, axis_size)

    x_legend_start = 300
    sample_width = 10  # Can be modified to show different results
    win_mid_point = 850
    colour_bar(canvas[1], x_legend_start, sample_width, win_mid_point, min(sc[1]), max(sc[1]))

    print(f'\nThe Spectral Centroid Data is Being Graphed')
    visualize(root, canvas[0], progress_b, sc[0], start_x, start_y, width, height, x_offset, y_offset, axis_size)

    root.mainloop()
