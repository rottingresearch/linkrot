# Following are the ANSI octal escape sequences for different formatting

HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"

# Text Style
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
REVERSE = "\033[7m"

# Nothing (Standard)
ENDC = "\033[0m"

def colorprint(color, s):
    '''Formates the string 's' with the ANSI octal escape sequence(s) 'color'
       and then makes sure that all the following print statements are of the of standard formatting.

    Args:
        color: ANSI octal escape sequence(s) to be used for formatting.
        s: The string to be formatted.

    Returns:
        None  

    '''
    print("%s%s%s" % (color, s, ENDC))
