#!/usr/bin/env python3

class terminal_colors:
    '''Colors class:
    Reset all colors with colors.reset
    Two subclasses fg for foreground and bg for background.
    Use as colors.subclass.colorname.
    i.e. colors.fg.red or colors.bg.green
    Also, the generic bold, disable, underline, reverse, strikethrough,
    and invisible work with the main class
    i.e. colors.bold
    '''
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    class fg:
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        lightgrey='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'
    class bg:
        black='\033[40m'
        red='\033[41m'
        green='\033[42m'
        orange='\033[43m'
        blue='\033[44m'
        purple='\033[45m'
        cyan='\033[46m'
        lightgrey='\033[47m'


def calc_color_dist(r1, g1, b1, r2, g2, b2):
    # Euclidean distance between <r1, g1, b1> and <r2, g2, b2>.
    # Better color distance metrics exist!
    r_delta = r2 - r1
    g_delta = g2 - g1
    b_delta = b2 - b1
    return math.sqrt(r_delta*r_delta + g_delta*g_delta + b_delta*b_delta)

def find_nearest_term_color_code_from_rgb(r, g, b):
    # Linearly search for the nearest color code.
    # A faster algorithm could be implemented!
    min_color_dist = 0xFFFF_FFFF_FFFF # arbitrary large number
    nearest_color_code = -1
    for color_code, (r2, g2, b2) in enumerate(term_color_code_rgb_values):
        rgb_unknown = r2 == -1
        if rgb_unknown:
            continue
        color_dist = calc_color_dist(r, g, b, r2, g2, b2)
        if color_dist < min_color_dist:
            min_color_dist = color_dist
            nearest_color_code = color_code

    return nearest_color_code

def color_text(txt_msg: str, fc: list, bc: list):
    return f'\33[38;2;{fc[0]};{fc[1]};{fc[2]};48;2;{bc[0]};{bc[1]};{bc[2]}m{txt_msg}\33[0m'

def colors_between(color1, color2, percentage):
    """
    Interpolates between two RGB colors.
    
    Args:
        color1: Starting RGB color as list [r, g, b]
        color2: Ending RGB color as list [r, g, b]
        percentage: Float between 0.00 and 1.00 (0 = color1, 1 = color2)
    
    Returns:
        List of RGB values [r, g, b] interpolated between the two colors
    """
    # Clamp percentage between 0 and 1
    percentage = max(0.0, min(1.0, percentage))
    
    # Calculate interpolated RGB values
    r = color1[0] + (color2[0] - color1[0]) * percentage
    g = color1[1] + (color2[1] - color1[1]) * percentage
    b = color1[2] + (color2[2] - color1[2]) * percentage
    
    # Return as integers (rounded)
    return [int(round(r)), int(round(g)), int(round(b))]
