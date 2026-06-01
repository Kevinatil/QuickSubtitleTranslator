color_dict = {
    'reset': '\033[0m',
    'red': '\033[31m',
    'green': '\033[32m',
    'blue': '\033[34m',
    'yellow': '\033[93m'
}
color_set = set(color_dict.keys())

def printc(content, color=None):
    if color is None:
        print(content)
    elif color in color_set:
        print(color_dict[color] + content + color_dict['reset'])
    else:
        print(content)
