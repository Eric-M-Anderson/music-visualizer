# Eric Anderson (100704730)

import librosa
from tkinter import Tk, Canvas
import os


def scale_list(data):
    """Scales a list based on the max value in the list and returns a list"""
    scaled_list = []
    max_val = max(data)
    for i in data:
        scaled_list.append(i / max_val)
    return scaled_list


def remove_0x(hex_value):
    """Takes in a hex value. Removes the 0x from the hex value and returns a string"""
    str_hex = ''
    for i, e in enumerate(hex_value):
        if e != 'x' and i != 0:
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


def circle(canvas_name, x, y, radius, fill):
    x0 = x - radius
    y0 = y - radius
    x1 = x + radius
    y1 = y + radius
    return canvas_name.create_oval(x0, y0, x1, y1, fill=fill)


def visualize(canvas_name, data, radius, offset, axis_size):
    """Prints triangles on a canvas with different colours, based on the Hz that each data point represents"""
    size = axis_size - (axis_size % (radius * offset))
    movement_x = radius * offset
    movement_y = radius * offset
    direction_down = True
    just_switched = False
    for s_sample in data:
        circle(canvas_name, movement_x, movement_y, radius, hsl_to_hex(s_sample * 285, 1, 0.5))
        if movement_y <= size and direction_down is True and just_switched is False:
            movement_y += radius * offset
        elif movement_y <= size and direction_down is False and just_switched is False:
            movement_y -= radius * offset
        if movement_y == size and just_switched is False:
            direction_down = False
            just_switched = True
        elif movement_y == radius * offset and just_switched is False:
            direction_down = True
            just_switched = True
        elif just_switched is True:
            movement_x += radius * offset
            just_switched = False
    return movement_x, movement_y


if __name__ == '__main__':
    root = Tk()
    root.geometry("1920x900")
    canvas = Canvas(root, width='1920', height='900', bg='white')
    canvas.pack()

    path = input('Enter a path to a directory with only .wav files in it: ')
    dir_data = os.listdir(path)
    sc_scaled = []
    for i, file in enumerate(dir_data):
        audio_data = path + file
        hz, sr = librosa.load(audio_data)
        print(f'{file} Data Loaded')
        spectral_centroids = list(librosa.feature.spectral_centroid(y=hz, sr=sr, n_fft=1024, hop_length=512)[0])
        for sample in spectral_centroids:
            sc_scaled.append(sample)
    sc_scaled = scale_list(sc_scaled)
    print(f'Graphing Data')
    xy_data = visualize(canvas, sc_scaled, 2, 2, 900)
    root.mainloop()
