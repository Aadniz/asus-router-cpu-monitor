#!/usr/bin/env python3

from colors import colors_between, color_text

bars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇"]
# color = [rgb start color, rgb end color]
bar_color1 = [[71, 180, 19], [255, 0, 0]]
bar_color2 = [[30, 167, 221], [255, 0, 0]]

def draw_data(data: dict):
    # draw_data only allowes to draw 2 values
    keys = list(data.keys())[:2]

    new_data = {}
    
    for key in keys:
        new_data[key] = {
            "percentage": data[key],
            "weight": 1.00
        }

    val1 = data[keys[0]]
        
    if len(keys) == 2:
        val1 = data[keys[0]]
        val2 = data[keys[1]]
        total = val1 + val2
        if total > 0:
            weight1 = val1 / total
            weight2 = val2 / total
        else:
            weight1 = weight2 = 0.5

        # Choose a bar based on percentage of the value
        bar = bars[min(int(weight1 * len(bars)), len(bars) - 1)]
        color1 = colors_between(bar_color1[0], bar_color1[1], data[keys[0]]/100)
        color2 = colors_between(bar_color2[0], bar_color2[1], data[keys[1]]/100)
        print(color_text(bar, color1, color2), end="", flush=True)
    else:
        weigh = 1.00


def print_data(data: dict):
    for key, value in data.items():
        percentage = '{0:.2f}'.format(value)
        print(f"{key}: {percentage}%", end=" ")
    print()
