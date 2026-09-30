import os

#import colors on Windows
if os.name == 'nt':
    os.system('color')


#added all the ANSI color 
ANSI_COLOR_SEQUENCES = {
    "black"  : '\033[30m',
    "red"    : '\033[31m',
    "green"  : '\033[32m',
    "yellow" : '\033[33m',
    "blue"   : '\033[34m',
    "magenta": '\033[35m',
    "cyan"   : '\033[36m',
    "white"  : '\033[37m',
    "reset"  : '\033[0m'
}

def change_termcolor(color : str):
    """
    Changes the color of the writing in the terminal to the given color (if known)
    """
    color = color.strip().lower()
    try:
        print(ANSI_COLOR_SEQUENCES[color], end="")
    except KeyError:
        return

def reset_termcolor():
    """
    Resets the terminal to its normal appearance
    """
    print('\033[0m', end="")

def print_termcolor(msg : str, color : str):
    """
    Changes the color of the writing in the terminal to the given color (if known) for a single message
    Resets to default color afterwards
    """
    change_termcolor(color)
    print(msg)
    reset_termcolor()