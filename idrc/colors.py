def printc(text, color='blue'):
    """
    Print a colored text to the console.
    Parameters:
        text (str): The text to be printed.
        color (str, optional): The color of the text. Defaults to 'blue'.
    """
    c = Color()
    color_code = getattr(c, color.upper(), c.BLUE)
    print(f'{color_code}{text}{c.RESET}')

class Color:
    def __init__(self):
        self.RED = '\033[91m'
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.BLUE = '\033[94m'
        self.MAGENTA = '\033[95m'
        self.CYAN = '\033[96m'
        self.WHITE = '\033[97m'
        self.BLACK = '\033[30m'
        self.PURPLE = '\033[35m'
        self.ORANGE = '\033[33m'
        self.REBECCAPURPLE = '\033[45m'
        self.INDIGO = '\033[44m'
        self.TURQUOISE = '\033[36m'
        self.PINK = '\033[95m'
        self.HOTPINK = '\033[95m'
        self.RESET = '\033[0m'