# Eric Anderson (100704730)

import librosa
from tkinter import Tk, Canvas, Scrollbar
import os
import math
from progress_bar import Progress


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
    return canvas_name.create_polygon(x0, y0, x1, y1, x2, y2, fill=fill)


def visualize(canvas_name, pb, data, sx, sy, w, h, xo, yo, axis_s):
    """Prints triangles on a canvas with different colours, based on the Hz that each data point represents"""
    movement_x = 0
    movement_y = 0
    y_size = axis_s - sy
    t_num = math.floor(y_size / (h + yo))
    t_count = 0
    back_up = False
    for count, s_sample in enumerate(data):
        pb.bar_update(count, len(data))
        if s_sample == '*':
            triangle(canvas_name, (movement_x + sx), (movement_y + sy), w, h, hsl_to_hex(0, 0, 0))
        else:
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
        elif t_count == 0:
            movement_x += w + xo
            back_up = False
            h *= -1


def file_load(p):
    """Loads all the files in a folder and does data preprocessing"""
    dir_data = os.listdir(path)
    spectral_centroids_s = []
    for i, file in enumerate(dir_data):
        audio_data = p + file
        hz, sr = librosa.load(audio_data)
        print(f'{file} Data Loaded')
        spectral_centroids = list(librosa.feature.spectral_centroid(y=hz, sr=sr)[0])
        for sample in spectral_centroids:
            spectral_centroids_s.append(sample)
        spectral_centroids_s.append('*')
    return scale_list(spectral_centroids_s)


def initialize_window(r, sc_s, sx, sy, w, h, xo, yo, axis_s):
    """Creates the windows necessary to show the visualization"""
    r.config(background='black')
    r.geometry("1700x905")
    r.title('Music Visualized')
    c = Canvas(r, width='1700', height='900', bg='black', highlightbackground="black")
    number_in_column = math.floor((axis_s - sy) / (h + yo))
    scrollbar_x = int(round(len(sc_s) / number_in_column, 0) * (w + xo)) + sx
    c.configure(scrollregion=(0, 0, scrollbar_x, 0))
    scrollbar = Scrollbar(r, orient='horizontal', command=c.xview)
    c.config(xscrollcommand=scrollbar.set)
    scrollbar.pack(side='top', fill='x')
    c.pack()
    return c


if __name__ == '__main__':
    progress_b = Progress()
    root = Tk()

    path = input('Enter a path to a directory with only .wav files in it: ')

    sc_scaled = file_load(path)

    start_x = 5
    start_y = 5
    width = 4        # Can be modified to show different results
    height = 5       # Can be modified to show different results
    x_offset = 2     # Can be modified to show different results
    y_offset = 2     # Can be modified to show different results
    axis_size = 880

    canvas = initialize_window(root, sc_scaled, start_x, start_y, width, height, x_offset, y_offset, axis_size)

    print(f'Graphing Data')
    visualize(canvas, progress_b, sc_scaled, start_x, start_y, width, height, x_offset, y_offset, axis_size)

    root.mainloop()
