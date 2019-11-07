light_grey = (200, 200, 200)
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
dark_red= (200, 0, 0)
green = (0, 255, 0)
dark_green = (0, 200, 0)
blue = (0, 0, 255)
item_yellow = (236, 255, 145)
brown = (119, 77, 0)
light_brown = (173, 112, 0)
grey = (96, 96, 96)
orange = (255, 87, 8)
light_blue = (147, 255, 238)
dark_grey = (150,150,150)
violet = (116, 19, 196)

def muted(color):
    result = [0,0,0]
    result[0] = round(.75 * color[0])
    result[1] = round(.75 * color[1])
    result[2] = round(.75 * color[2])
    return result


class Pallet:
    def __init__(self, list, flagship):
        # a list of colors that go with this pallet
        self.list = list

        # a dictionary of colors that are often features of this pallet, this might also be interpreted as a color scheme
        self.flagship = flagship
        # eg = {"red":(255,0,20), etc...}

Flame = Pallet([[240,127,19],[128,9,9],[242,125,12],[253,207,88]], red)
Smoke = Pallet([[127,72,95],[209,224,247],[208,208,206],[169,186,212],[65,63,68]], dark_grey)