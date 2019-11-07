import random
import os
import time
import pygame
import colorsLib as colors
#import spritesLib
import classes as cass
import AIS as AI #needed for dimension and player import
import math
#import multiprocessing
import threading


def get_img(string):
    os.chdir(os.getcwd() + "\\sprites")
    img = pygame.image.load(string)
    os.chdir("..")
    return img


with open("player.txt") as document:
    player = eval(document.read())
    assert isinstance(player, cass.Character), 'Not a character'


def load_dimension():
    global player
    with open("dimensions.txt") as document:
        dimensions_list = eval(document.read())
        length = len(dimensions_list)

    assert isinstance(player, cass.MainCharacter), "Not a character"
    with open(dimensions_list[player.dim]) as document:
        #print(player.dim)
        dimension = eval(document.read())
        assert isinstance(dimension, cass.Dimension), 'Not a Dimension'

    time.sleep(.5)

    # put the player in the dimension object
    found = False
    for obj in range(len(dimension.features)):
        # print(obj)
        if not isinstance(dimension.features[obj], cass.DimMarker):
            continue
        else:
            assert isinstance(dimension.features[obj], cass.DimMarker), "Not a DimMarker"

        if dimension.features[obj].thing == "Player" and not found:

            # this block ensures that the player spawns where the dimension says they should
            player.x_loc = dimension.features[obj].x - dimension.x / 2
            player.y_loc = dimension.features[obj].y  # not implimented yet
            player.z_loc = dimension.features[obj].z - dimension.z / 2

            # this adds the player to the dimension, from this point onward, there is no player dimmarker,
            # dimmarkers are for construction mostly
            # print(obj)
            # print(isinstance(dimension.features[obj], cass.DimMarker))
            dimension.features[obj].extra = player
            # print(isinstance(dimension.features[obj].extra, cass.MainCharacter))
            player = obj
            # print(dimension.features[obj].extra)
            found = True
        elif dimension.features[obj].thing == "Player" and found:
            del dimension.features[obj].thing

    if not found:
        print("Player Not found in world")

    # assign all the game wall art and choose random stones for those that require it
    for item in range(0, len(dimension.features)):
        if isinstance(dimension.features[item], cass.GameWall):
            if type(dimension.features[item].art) is list:
                continue
            elif type(dimension.features[item].art) is str:
                if dimension.features[item].art == "RandomAS":
                    dimension.features[item].art = pygame.transform.scale(get_img("amberstone" + str(random.randint(0, 7)) + ".PNG"),
                                                       (20, 20))
                else:
                    dimension.features[item].art = pygame.transform.scale(get_img(dimension.features[item].art), (20, 20))
                continue
            else:
                continue

        else:
            continue


    return player, dimension


def reset_player_weapons():
    play = dimension.features[player].extra
    assert isinstance(play, cass.MainCharacter), "need a player here"
    weapon1 = play.weapons[play.hand["Left"]]
    weapon2 = play.weapons[play.hand["Right"]]
    return weapon1, weapon2


player, dimension = load_dimension()
pygame.init()
display_w = dimension.x
display_h = dimension.z
fps = 30
# key map has three states, True, Hold, and False. hold means it will be processed on the next iteration
key_map = {"w": False, "a": False, "s": False, "d": False, "M1": False, "M2": False, "M3": False, "Shift": False, "Caps": False}
acc = .1
debug = False
Fun = False
Build = False
# an editor for building blocks
editor = cass.EditorPreset("Build")
editor.setall3(0)
#os.chdir(os.getcwd() + "\\fonts")
smallText = pygame.font.Font("SCR.otf", 10)  # creates the text format, size and font

smalltext = pygame.font.Font("SCR.otf", 10)  # creates the text format, size and font
#os.chdir("..")


def save(new=None):
    spaces = "               " # spaces equal to the dimension features
    c = ",\n"
    if new:
        with open("dimensions.txt") as document:
            dimensions_list = eval(document.read())
            length = len(dimensions_list)
        temp = dimension.dimension_number
        dimension.dimension_number = length
        name = "dimension" + str(length) + ".txt"
    else:
        name = "dimension" + str(dimension.dimension_number) + ".txt"

    with open(name, "w+") as document: #open("dimension" + str(dimension.dimension_number + 1) + ".txt", "w+") as document:
        document.write("cass.Dimension(\n")
        document.write(spaces + ' "{}"'.format(dimension.name) + c)
        document.write(spaces + ' "{}"'.format(dimension.description) + c)
        document.write(spaces + " " + str(dimension.x) + c)
        document.write(spaces + " " + str(dimension.y) + c)
        document.write(spaces + " " + str(dimension.z) + c)
        document.write(spaces + " " + str(dimension.dimension_number) + c)
        document.write(spaces + " " + str(dimension.gravity) + c)
        document.write(spaces + " [" + "\n")

        for x in dimension.features:
            if isinstance(x, cass.DimMarker):
                thing = x
                if thing.thing == "EOL":
                    continue
                document.write(spaces + "  " + "cass.DimMarker(")
                if isinstance(thing.extra, cass.MainCharacter):
                    document.write('\"{}\"'.format(thing.thing) + ", " + str(round(thing.extra.x_loc + display_w/2)) + ", " +
                                   str(round(thing.extra.y_loc)) + ", " + str(round(thing.extra.z_loc + display_h/2)))
                else:
                    document.write('\"{}\"'.format(thing.thing) + ", " + str(thing.x) + ", " +
                                   str(thing.y) + ", " + str(thing.z) + ", " + str(thing.extra))
                document.write(")" + c)

            elif isinstance(x, cass.MainCharacter):
                # this will never get used, for now
                document.write(spaces + "  " + "cass.DimMarker(")
                document.write('\"Player\"' + ", " + str(player_x()) + ", " + str(player_y()) + ", " + str(player_z()))
                document.write(")" + c)

            elif isinstance(x, cass.GameWall):
                duplicate = False
                for y in dimension.features:
                    if not isinstance(y, cass.GameWall):
                        continue
                    assert isinstance(y, cass.GameWall), "Not a Gamewall, somehow"
                    if x.garbage:
                        continue
                    if x is y:
                        continue
                    if x.x_loc == y.x_loc:
                        if x.z_loc == y.z_loc:
                            y.garbage = True
                            duplicate = True

                if duplicate:
                    continue
                else:
                    thing = x
                    assert isinstance(thing, cass.GameWall), "ya done goofed"
                    document.write(spaces + "  " + "cass.GameWall(")

                    #document.write("'Player'" + ", " + str(player_x()) + ", " + str(player_y()) + ", " + str(player_z()))

                    document.write('{}, '.format(thing.x_loc))
                    document.write('{}, '.format(thing.y_loc))
                    document.write('{}, '.format(thing.z_loc))
                    document.write("{}, ".format(thing.dim))
                    document.write("{}, ".format(thing.height))
                    document.write("{}, ".format(thing.weight))
                    document.write("{}, ".format(thing.width))
                    document.write("{}, ".format(thing.length))
                    document.write("{}, ".format(thing.breakable))

                    if type(thing.art) is list:
                        document.write("{}, ".format(thing.art))
                    else:
                        document.write("'RandomAS', ")

                    document.write("{}".format(thing.collisions))

                    document.write(")" + c)

            elif isinstance(x, cass.Teleporter):
                thing = x
                assert isinstance(thing, cass.Teleporter)
                document.write(spaces + "  " + "cass.Teleporter(")
                #destination, tele_type, art, cooldown, x, y, z, dimension, height, weight, width, length, collides

                document.write('[{}, '.format(thing.dest[0]))
                document.write('{}, '.format(thing.dest[1]))
                document.write('{}, '.format(thing.dest[2]))
                if type(thing.dest[3]) is not int:
                    document.write('"{}"], '.format(thing.dest[3]))
                else:
                    document.write('{}], '.format(thing.dest[3]))
                document.write('"{}", '.format(thing.type))
                if type(thing.art) is list:
                    document.write('{}, '.format(thing.art))
                else:
                    document.write('{}, '.format(colors.white))
                document.write('{}, '.format(thing.cooldown))
                document.write('{}, '.format(thing.x_loc))
                document.write('{}, '.format(thing.y_loc))
                document.write('{}, '.format(thing.z_loc))
                document.write("{}, ".format(thing.dim))
                document.write("{}, ".format(thing.height))
                document.write("{}, ".format(thing.weight))
                document.write("{}, ".format(thing.width))
                document.write("{}, ".format(thing.length))
                document.write("{} ".format(True))
                document.write(")" + c)

            elif isinstance(x, cass.Enemy):
                thing = x
                assert isinstance(thing, cass.Enemy)
                document.write(spaces + "  " + "cass.Enemy(")
                # name, desc, x, y, z, dimension, height, weight, width, length, max_h, nat_reg, defense, armor,
                #                  strength, speed, title, meta, status, gives, weapons, hands, ai, art=None


                document.write('{}, '.format(thing.name))
                document.write('{}, '.format(thing.description))
                document.write('{}, '.format(thing.x_loc))
                document.write('{}, '.format(thing.y_loc))
                document.write('{}, '.format(thing.z_loc))
                document.write('{}, '.format(thing.dim))
                document.write("{}, ".format(thing.height))
                document.write("{}, ".format(thing.weight))
                document.write("{}, ".format(thing.width))
                document.write("{}, ".format(thing.length))
                document.write('{}, '.format(thing.max_h))
                document.write('{}, '.format(thing.h_regen))
                document.write('{}, '.format(thing.defense))
                document.write('{}, '.format(thing.armor))
                document.write('{}, '.format(thing.strength))
                document.write('{}, '.format(thing.speed))
                document.write('{}, '.format(thing.title))
                document.write('{}, '.format(thing.metabolism))
                document.write('{}, '.format(thing.status))
                document.write('{}, '.format(None))

                if thing.weapons in [None, [], ()]:
                    document.write('{}, '.format(None))
                else:
                    document.write('{}, '.format(None))
                    #TODO this section, the class is not properly saved
                document.write('{}, '.format(None))
                document.write('{}, '.format(None))
                document.write('{}, '.format(None))
                document.write(")" + c)


        document.write(spaces + "  " + "cass.DimMarker(")
        document.write('\"EOL\"' + ",0 ,0 ,0")
        document.write(")" + "\n")
        document.write(spaces + " ]" + "\n")
        document.write(spaces + ")" + "\n")

    if new:
        with open("dimensions.txt", "w+") as document:
            document.write("[")
            dimensions_list.append(name)
            for x in dimensions_list:
                document.write('"{}"'.format(x))
                if dimensions_list.index(x) < length:
                    document.write(", ")
            document.write("]")
        dimension.dimension_number = temp
    for x in dimension.features:
        if not isinstance(x, cass.GameWall):
            continue
        x.garbage = False


def loadingscreen():
    gameDisplay.fill(colors.light_grey)
    disp_text("Loading...")
    pygame.display.update()
    clock.tick(fps)


def rc(key=None):
    if key == "Fire":
        return colors.Flame.list[random.randint(0, 3)]

    if key == "Smoke":
        return colors.Smoke.list[random.randint(0, 4)]

    else:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0 ,255)
        return [r,g,b]


def player_x():
    return dimension.features[player].extra.x_loc


def player_y():
    return dimension.features[player].extra.y_loc


def player_z():
    return dimension.features[player].extra.z_loc


def player_x_z():
    return dimension.features[player].extra.x_z()


def muted(color):
    # return a muted version of the given color
    result = [0,0,0]
    result[0] = round(.75 * color[0])
    result[1] = round(.75 * color[1])
    result[2] = round(.75 * color[2])
    return result


gameDisplay = pygame.display.set_mode((display_w, display_h))
pygame.display.set_caption('Electron')
clock = pygame.time.Clock()
paused = False
# used to break and reload a new dimension
restart = False
os.chdir(os.getcwd() + "\\sprites")
# loads the player image in a vertical orientation
player_image_zeroed = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("fp.PNG"), (20, 20)), 90)
os.chdir("..")
center_zero = (display_w / 2, display_h / 2)
weapon1, weapon2 = reset_player_weapons()
assert isinstance(weapon1, cass.Weapon), "NOt proper weapon 1"
assert isinstance(weapon2, cass.Weapon), "NOt proper weapon 2"


def angle(outer, inner, degrees=None):

    # this function is garbage but it works for now
    #dot = outer[0] * outer[1] + inner[0] * inner[1]  # dot product
    #det = outer[0] * inner[1] - inner[0] * outer[1]  # determinant
    #angl = math.atan2(det, dot)                     # atan2(y, x) or atan2(sin, cos)
    #angl = math.atan2(math.sin(outer[0] - inner[0]), math.cos(outer[1] - inner[1]))

    top = (outer[0] - inner[0])
    bottom = (outer[1] - inner[1])
    angl = math.atan2(outer[1] - inner[1], outer[0] - inner[0]) + math.radians(90)
    quadrent = None
    if inner[0] > outer[0] and outer[1] < inner[1]:
        quadrent = 1
        angl = angl * -1
    elif inner[0] < outer[0] and outer[1] < inner[1]:
        quadrent = 4
        angl = math.radians(360) - angl
    elif inner[0] > outer[0] and outer[1] > inner[1]:
        quadrent = 2
        angl = math.radians(360) - angl
    elif inner[0] < outer[0] and outer[1] > inner[1]:
        quadrent = 3
        angl = math.radians(360) - angl

    if not quadrent:
        if inner[0] > outer[0]:
            angl = 90
        if inner[0] < outer[0]:
            angl = 270
        if inner[1] > outer[1]:
            angl = 180
        if inner[1] > outer[1]:
            angl = 0

    if angl == 15470:
        angl = 270
    elif angl == 5157:
        angl = 90

    #print(quadrent)

    if degrees:
        return round(math.degrees(angl))
    else:
        return round(angl)


def mouse():
    #returns position and mvmt of mouse
    pos = pygame.mouse.get_pos()
    mvmt = pygame.mouse.get_rel()
    return pos, mvmt


def mouse_buttons():
    return pygame.mouse.get_pressed()


def quitgame():
    pygame.quit()
    quit()


def plane_distance(ob1x, ob1z, ob2x, ob2z):
    # distance across a 2D plane uses x and z because I expect to use those a lot
    dist = round((((ob2x - ob1x)**2) + ((ob2z - ob1z)**2))**.5, 2)
    return dist


def text_objects(text, font, color=None):
    if not color:
        color = colors.black
    textsurface = font.render(text, True, color)
    return textsurface, textsurface.get_rect()


def message_display(text):
    LargeText = pygame.font.Font('freesansbold.ttf', 115) # creates the text format, size and font
    TextSurf, TextRect = text_objects(text, LargeText)
    TextRect.center = ((display_w / 2), (display_h/2))
    gameDisplay.blit(TextSurf, TextRect)


def disp_text(text, location=None, color=None):
    TextSurf, TextRect = text_objects(text, smalltext, color)
    if not location:
        TextRect.center = ((display_w / 2), (display_h / 2))
    else:
        TextRect.center = (location[0], location[1])
    gameDisplay.blit(TextSurf, TextRect)


def button(msg, x, y, w, h, ic, ac=None, action=None, args=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        if not ac:
            ac = colors.muted(ic)
        pygame.draw.rect(gameDisplay, ac, (x, y, w, h))
        if click[0] == 1 and action != None:
            #print("yeah")
            action(args)
    else:
        pygame.draw.rect(gameDisplay, ic, (x, y, w, h))

    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    gameDisplay.blit(textSurf, textRect)


def text_box(msg, x, y, w, h, c=None):
    # this button returns true when clicked
    if type(msg) is int:
        msg = str(msg)
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if c:
        ic = c
    else:
        ic = [199, 188, 188]

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ic, (x, y, w, h))
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(gameDisplay, ic, (x, y, w, h))


    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    gameDisplay.blit(textSurf, textRect)
    
    
def typing():
    # returns a cronilogical list of characters pressed
    pressed = ["_", "_"]
    del pressed[1]
    shift = False
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: 
                shift = True
                
            if shift:
                if event.key == pygame.K_a:
                    pressed.append("a")
                elif event.key == pygame.K_b:
                    pressed.append("b")
                elif event.key == pygame.K_c:
                    pressed.append("c")
                elif event.key == pygame.K_d:
                    pressed.append("d")
                elif event.key == pygame.K_e:
                    pressed.append("e")
                elif event.key == pygame.K_f:
                    pressed.append("f")
                elif event.key == pygame.K_g:
                    pressed.append("g")
                elif event.key == pygame.K_h:
                    pressed.append("h")
                elif event.key == pygame.K_i:
                    pressed.append("i")
                elif event.key == pygame.K_j:
                    pressed.append("j")
                elif event.key == pygame.K_k:
                    pressed.append("k")
                elif event.key == pygame.K_l:
                    pressed.append("l")
                elif event.key == pygame.K_m:
                    pressed.append("n")
                elif event.key == pygame.K_n:
                    pressed.append("n")
                elif event.key == pygame.K_o:
                    pressed.append("o")
                elif event.key == pygame.K_p:
                    pressed.append("p")
                elif event.key == pygame.K_q:
                    pressed.append("q")
                elif event.key == pygame.K_r:
                    pressed.append("r")
                elif event.key == pygame.K_s:
                    pressed.append("s")
                elif event.key == pygame.K_t:
                    pressed.append("t")
                elif event.key == pygame.K_u:
                    pressed.append("u")
                elif event.key == pygame.K_v:
                    pressed.append("v")
                elif event.key == pygame.K_w:
                    pressed.append("w")
                elif event.key == pygame.K_x:
                    pressed.append("x")
                elif event.key == pygame.K_y:
                    pressed.append("y")
                elif event.key == pygame.K_z:
                    pressed.append("z")

            else:
                if event.key == pygame.K_a:
                    pressed.append("A")
                elif event.key == pygame.K_b:
                    pressed.append("B")
                elif event.key == pygame.K_c:
                    pressed.append("C")
                elif event.key == pygame.K_d:
                    pressed.append("D")
                elif event.key == pygame.K_e:
                    pressed.append("E")
                elif event.key == pygame.K_f:
                    pressed.append("F")
                elif event.key == pygame.K_g:
                    pressed.append("G")
                elif event.key == pygame.K_h:
                    pressed.append("H")
                elif event.key == pygame.K_i:
                    pressed.append("I")
                elif event.key == pygame.K_j:
                    pressed.append("J")
                elif event.key == pygame.K_k:
                    pressed.append("K")
                elif event.key == pygame.K_l:
                    pressed.append("L")
                elif event.key == pygame.K_m:
                    pressed.append("M")
                elif event.key == pygame.K_n:
                    pressed.append("N")
                elif event.key == pygame.K_o:
                    pressed.append("O")
                elif event.key == pygame.K_p:
                    pressed.append("P")
                elif event.key == pygame.K_q:
                    pressed.append("Q")
                elif event.key == pygame.K_r:
                    pressed.append("R")
                elif event.key == pygame.K_s:
                    pressed.append("S")
                elif event.key == pygame.K_t:
                    pressed.append("T")
                elif event.key == pygame.K_u:
                    pressed.append("U")
                elif event.key == pygame.K_v:
                    pressed.append("V")
                elif event.key == pygame.K_w:
                    pressed.append("W")
                elif event.key == pygame.K_x:
                    pressed.append("X")
                elif event.key == pygame.K_y:
                    pressed.append("Y")
                elif event.key == pygame.K_z:
                    pressed.append("Z")

            if event.key == pygame.K_SPACE:
                pressed.append(" ")
            elif event.key == pygame.K_1:
                pressed.append("1")
            elif event.key == pygame.K_2:
                pressed.append("2")
            elif event.key == pygame.K_3:
                pressed.append("3")
            elif event.key == pygame.K_4:
                pressed.append("4")
            elif event.key == pygame.K_5:
                pressed.append("5")
            elif event.key == pygame.K_6:
                pressed.append("6")
            elif event.key == pygame.K_7:
                pressed.append("7")
            elif event.key == pygame.K_8:
                pressed.append("8")
            elif event.key == pygame.K_9:
                pressed.append("9")
            elif event.key == pygame.K_0:
                pressed.append("0")
            elif event.key == pygame.K_RETURN:
                pressed.append("#")
            elif event.key == pygame.K_DELETE:
                pressed.append("|")

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                shift = False

    pressed.append("_")
    if pressed[0] == "_" and pressed[1] == "_":
        return False
    else:
        return(pressed[1])


def ret_button(msg, x, y, w, h, ic, ac=None):
    # this button returns true when clicked
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        if not ac:
            ac = colors.muted(ic)
        pygame.draw.rect(gameDisplay, ac, (x, y, w, h))
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(gameDisplay, ic, (x, y, w, h))

    #os.chdir(os.getcwd() + "\\fonts")
    smallText = pygame.font.Font("SCR.otf", 20)  # creates the text format, size and font
    #os.chdir("..")
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    gameDisplay.blit(textSurf, textRect)


def pallet_particle(pos, amount=None, color=None, life=None):
    # pos = position
    if not color:
        color = "Fire"
    if not amount:
        amount = 1
    if not life:
        life = 150
    if life < 30:
        life = 35
    for x in range(0, amount):
        particle = cass.WorldObject(rc(color), "Particle", None, pos[0] + player_x(), 0,
                                    pos[1] + player_z(), 0, 0, 0, 0, 0,
                                    random.randint(30, life))
        particle.x_vel = random.randint(-4, 4)
        particle.z_vel = random.randint(-4, 4)
        dimension.features.append(particle)


def pause():
    paused = True
    saved = False
    zeroed = False
    while paused:

        gameDisplay.fill(colors.light_grey)
        if ret_button("'P' to un-Pause", display_h/2, display_w/2, 200, 50, colors.red):
            paused = False
            break
        if ret_button("exit game", display_h/2, display_w/4, 200, 50, colors.dark_red):
            quitgame()

        if ret_button("Save", display_h/2, display_w/6, 200, 50, colors.light_blue) and not saved:
            saved = True
            print("saving")
            save()

        if ret_button("Save as new", display_h/2 + 200, display_w/6, 200, 50, colors.dark_red) and not saved:
            saved = True
            print("saving")
            save(True)

        if ret_button("Zero", display_h/2, display_w/3, 200, 50, colors.orange) and not zeroed:
            zeroed = True
            dimension.features[player].extra.x_loc = 0 - display_w/2
            dimension.features[player].extra.z_loc = 0 - display_h/2
            pallet_particle((display_w/2 , display_h/2), 30, "Smoke", 60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            if not event.type == pygame.KEYDOWN:
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    break
                if event.key == pygame.K_q:
                    quitgame()
                if event.key == pygame.K_p:
                    paused = False
                    break
            if not paused:
                break
        if not paused:
            break
        pygame.display.update()  # shows all the things you have previously drawn ^^^^^
        clock.tick(fps)


def open_inventory():
    self = dimension.features[player].extra
    assert isinstance(self, cass.MainCharacter), "no inventory to manage"
    leave = False

    while True:

        # general bacground colors and stuff
        gameDisplay.fill(colors.brown)
        gameDisplay.fill(colors.grey, [-10, 90, display_w + 10, display_h-160])
        pygame.draw.line(gameDisplay, colors.light_brown,
                         [-10, 90], [display_w + 10, 90], 4)
        pygame.draw.line(gameDisplay, colors.light_brown,
                         [-10, display_h - 70], [display_w + 10, display_h - 70], 4)

        if ret_button("Exit Inventory", 7, display_h - 57, 200, 50, colors.red):
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            if not event.type == pygame.KEYDOWN:
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    break
                if event.key == pygame.K_e:
                    leave = True
        if leave:
            break

        pygame.display.update()  # shows all the things you have previously drawn ^^^^^
        clock.tick(fps)


def RGBcolor(color):
    if is_number(color):
        color = int(color)
        if 0 <= color <= 255:
            return color
    else:
        return 255


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def block_editor():
    global editor
    paused = True
    assert isinstance(editor, cass.EditorPreset), "Not an editor"
    text = "_"
    prev_box = 1
    box = 3
    while paused:
        #def ret_button(msg, x, y, w, h, ic, ac=None)

        gameDisplay.fill(colors.light_grey)
        if ret_button("Exit Editor", 0, 0, 200, 50, colors.red):
            paused = False
            break

        if ret_button(editor.preference, display_w/2, display_h/2 - 200, 200, 50, colors.orange):
            if editor.preference == "Color":
                editor.preference = "Sprite"
            elif editor.preference == "Sprite":
                editor.preference = "Color"
                
        if ret_button("Collides : {}".format(editor.collisions), display_w/2, display_h/2 - 250, 200, 50, colors.violet):
            if editor.collisions is True:
                editor.collisions = False
            elif editor.collisions is False:
                editor.collisions = True

        if ret_button("Set", display_w/2 - 150, display_h/2, 200, 50, colors.orange):
            prev_box = box
            editor.color[prev_box] = RGBcolor(text)
            box = 3

        if box == 0:
            if text_box(RGBcolor(text), 100, display_h/2, 50, 50, colors.light_grey):
                box = 0
        else:
            if text_box(editor.color[0], 100, display_h/2, 50, 50):
                prev_box = box
                editor.color[prev_box] = RGBcolor(text)
                text = "_"
                box = 0

        if box == 1:
            if text_box(RGBcolor(text), 200, display_h/2, 50, 50, colors.light_grey):
                box = 1
        else:
            if text_box(editor.color[1], 200, display_h/2, 50, 50):
                prev_box = box
                editor.color[prev_box] = RGBcolor(text)
                text = "_"
                box = 1

        if box == 2:
            if text_box(RGBcolor(text), 300, display_h/2, 50, 50, colors.light_grey):
                box = 2
        else:
            if text_box(editor.color[2], 300, display_h/2, 50, 50):
                prev_box = box
                editor.color[prev_box] = RGBcolor(text)
                text = "_"
                box = 2

        typin = typing()
        if typin is not False:
            if text[0] is "_":
                text = typin
            else:
                text += typin


#
        # make sure that everything is an integer
        editor.intcolor()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    break
        if not paused:
            break
        if not paused:
            for color in editor.color:
                if not (0 <= color <= 255):
                    editor.color = colors.red
            break

        gameDisplay.fill(editor.color_na(), [100, display_h - 200, 100, 100])

        pygame.display.update()  # shows all the things you have previously drawn ^^^^^
        clock.tick(fps)


def tele_editor(teleporter):
    global editor
    paused = True
    assert isinstance(teleporter, cass.Teleporter), "Not a Teleporter"
    text = "_"
    prev_box = 1
    box = 3
    color = [0,0,0,0]
    while paused:
        # def ret_button(msg, x, y, w, h, ic, ac=None)

        gameDisplay.fill(colors.light_grey)
        if ret_button("Exit Editor", 0, 0, 200, 50, colors.red):
            paused = False
            break

        if ret_button(teleporter.type, display_w / 2, display_h / 2 - 200, 200, 50, colors.orange):
            if teleporter.type == "exact":
                teleporter.type = "same"
            elif teleporter.type == "same":
                teleporter.type = "exact"

        if ret_button("Saves: {}".format(teleporter.collisions), display_w / 2, display_h / 2 - 250, 200, 50,
                      colors.violet):
            if teleporter.collisions:
                teleporter.collisions = False
            elif not teleporter.collisions:
                teleporter.collisions = True
            
        if ret_button("Set", display_w / 2 - 150, display_h / 2, 200, 50, colors.orange):
            prev_box = box
            editor.color[prev_box] = RGBcolor(text)
            box = 3

        if box == 0:
            if text_box(RGBcolor(text), 100, display_h / 2, 50, 50, colors.light_grey):
                box = 0
        else:
            if text_box(editor.color[0], 100, display_h / 2, 50, 50):
                prev_box = box
                color[prev_box] = RGBcolor(text)
                text = "_"
                box = 0

        if box == 1:
            if text_box(RGBcolor(text), 200, display_h / 2, 50, 50, colors.light_grey):
                box = 1
        else:
            if text_box(editor.color[1], 200, display_h / 2, 50, 50):
                prev_box = box
                color[prev_box] = RGBcolor(text)
                text = "_"
                box = 1

        if box == 2:
            if text_box(RGBcolor(text), 300, display_h / 2, 50, 50, colors.light_grey):
                box = 2
        else:
            if text_box(editor.color[2], 300, display_h / 2, 50, 50):
                prev_box = box
                color[prev_box] = RGBcolor(text)
                text = "_"
                box = 2

        typin = typing()
        if typin is not False:
            if text[0] is "_":
                text = typin
            else:
                text += typin

        # make sure that everything is an integer
        editor.intcolor()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    break
        if not paused:
            break
        if not paused:
            for color in editor.color:
                if not (0 <= color <= 255):
                    editor.color = colors.red
            break

        gameDisplay.fill(editor.color_na(), [100, display_h - 200, 100, 100])

        pygame.display.update()  # shows all the things you have previously drawn ^^^^^
        clock.tick(fps)

    return teleporter


def lectern(text):
    # need some logic for line wraps and stuff
    gameDisplay.fill(colors.light_grey)
    disp_text("Loading...")
    pygame.display.update()
    clock.tick(fps)


def GameLoop():
    main_menu()
    global restart
    global player
    global dimension
    # used to reload a new dimension
    while True:
        if restart is True:
            loadingscreen()
            player, dimension = load_dimension()
        restart = False
        # used to perform game tick
        while True:

            # get input
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:
                    buttons = mouse_buttons()
                    if buttons[0]:
                        key_map["M1"] = True

                    if buttons[1]:
                        key_map["M2"] = True

                    if buttons[2]:
                        key_map["M3"] = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    buttons = mouse_buttons()
                    if not buttons[0]:
                        key_map["M1"] = False

                    if not buttons[1]:
                        key_map["M2"] = False

                    if not buttons[2]:
                        key_map["M3"] = False

                elif event.type == pygame.QUIT:
                    quitgame()

                elif event.type == pygame.KEYUP:

                    if event.key == pygame.K_w:
                        key_map["w"] = False
                    elif event.key == pygame.K_a:
                        key_map["a"] = False
                    elif event.key == pygame.K_s:
                        key_map["s"] = False
                    elif event.key == pygame.K_d:
                        key_map["d"] = False
                    elif event.key == pygame.K_LSHIFT:
                        key_map["Shift"] = False

                    elif event.key == pygame.K_CAPSLOCK:
                        if key_map["Caps"] is False:
                            key_map["Caps"] = True
                        elif key_map["Caps"] is True:
                            key_map["Caps"] = False

                elif event.type == pygame.KEYDOWN:
                    global Build
                    if event.key == pygame.K_w:
                        key_map["w"] = True
                    elif event.key == pygame.K_a:
                        key_map["a"] = True
                    elif event.key == pygame.K_s:
                        key_map["s"] = True
                    elif event.key == pygame.K_d:
                        key_map["d"] = True
                    elif event.key == pygame.K_LSHIFT:
                        key_map["Shift"] = True

                    elif event.key == pygame.K_CAPSLOCK:
                        if key_map["Caps"] is False:
                            key_map["Caps"] = True
                        elif key_map["Caps"] is True:
                            key_map["Caps"] = False

                    elif event.key == pygame.K_p:
                        pause()
                    elif event.key == pygame.K_DELETE:
                        quitgame()
                    elif event.key == pygame.K_ESCAPE:
                        pause()
                    elif event.key == pygame.K_F3:
                        global debug
                        if debug:
                            debug = False
                        else:
                            debug = True

                    elif event.key == pygame.K_F9:
                        global Fun
                        if Fun:
                            Fun = False
                        else:
                            Fun = True

                    elif event.key == pygame.K_b:
                        if Build:
                            Build = False
                        else:
                            Build = True
                    #elif event.key == pygame.K_k:
                        #stop here forces a breakpoint in debug mode
                        #print("debug")


                    elif event.key == pygame.K_e:

                        if Build:
                            block_editor()
                        else:
                            open_inventory()

                #global Fun
                if Fun:
                    if key_map["M1"]:
                        pos = mouse()
                        pos = pos[0]
                        for x in range(0, 60):
                            pallet_particle(pos, None, "Smoke")

                # used for build mode
                if Build:
                    global editor
                    pos = mouse()
                    pos = pos[0]
                    if key_map["M3"] and (key_map["Shift"] is False):
                            visual = editor.ret_visual()
                            if visual == None:
                                visual = get_img("amberstone0.PNG")
                                visual = pygame.transform.scale(visual, (20, 20))
                            if debug:
                                wall = cass.GameWall(player_x() + pos[0], 0, player_z() + pos[1], dimension.dimension_number,
                                                     0, 0, 0, 0, False, visual, editor.collisions)

                                wall.x_loc = 25 * round(wall.x_loc / 25)
                                wall.z_loc = 25 * round(wall.z_loc / 25)

                            else:
                                wall = cass.GameWall(player_x() + pos[0], 0, player_z() + pos[1], dimension.dimension_number,
                                                     0, 0, 0, 0, False, visual, editor.collisions)
                            wall.collisions = editor.collisions
                            dimension.features.append(wall)

                    elif key_map["M3"] and key_map["Shift"] is not False:
                        for x in range(0, len(dimension.features)):
                            if isinstance(dimension.features[x], cass.DimMarker):
                                continue
                            elif isinstance(dimension.features[x], cass.WorldObject):
                                continue
                            elif isinstance(dimension.features[x], cass.GameWall):
                                #print("Yes")
                                if plane_distance(dimension.features[x].x_loc, dimension.features[x].z_loc, player_x() + pos[0], player_z() + pos[1]) < 20:
                                    #for x in range(0, 20):
                                    #    pallet_particle(pos)
                                    assert isinstance(dimension.features[x], cass.GameWall), help(dimension.features[x])
                                    del dimension.features[x]
                                    break
                                else:
                                    continue
                            elif isinstance(dimension.features[x], cass.Teleporter):
                                if plane_distance(dimension.features[x].x_loc, dimension.features[x].z_loc,
                                                  player_x() + pos[0], player_z() + pos[1]) < 15:
                                    pallet_particle(pos, 10)
                                    dimension.features[x] = tele_editor(dimension.features[x])

            # Draw
            house = mouse()
            for item in dimension.features:
                if isinstance(item, cass.DimMarker):
                    assert isinstance(item, cass.DimMarker), "IDK"
                    if item.thing == "Background":
                        gameDisplay.fill(item.extra)

                    if item.thing == "Player":
                        assert isinstance(item.extra, cass.MainCharacter), "Not a character"
                        angl = angle(house[0], center_zero, True)
                        player_image = pygame.transform.rotate(player_image_zeroed, angl)
                        gameDisplay.blit(player_image, (display_w / 2 - 10, display_h / 2 - 10))
                        #gameDisplay.fill(colors.green, [dimension.x/2, dimension.z/2, 20, 20])

                elif isinstance(item, cass.GameWall):
                    if type(item.art) is tuple:
                        item.art = list(item.art)
                    if type(item.art) is list:
                        gameDisplay.fill(item.art, [item.x_loc - player_x(), item.z_loc - player_z(), 20, 20])
                    else:
                        gameDisplay.blit(item.art, (item.x_loc - player_x(), item.z_loc - player_z()))

                elif isinstance(item, cass.Teleporter):
                    if type(item.art) is tuple:
                        item.art = list(item.art)
                    if type(item.art) is list:
                        gameDisplay.fill(item.art, [item.x_loc - player_x(), item.z_loc - player_z(), 20, 20])
                    else:
                        gameDisplay.blit(item.art, (item.x_loc - player_x(), item.z_loc - player_z()))

                elif isinstance(item, cass.WorldObject):
                    #if item.type == "Particle":
                    gameDisplay.fill(item.art, [item.x_loc - player_x(), item.z_loc - player_z(), 4, 4])
                    #if item.type == "bullet":
                    if item.life():
                        del dimension.features[dimension.features.index(item)]
                    if item.type is "lightning":
                        for item2 in dimension.features:
                            if not isinstance(item2, cass.WorldObject):
                                continue
                            else:
                                if item2.type != "lightning":
                                    continue
                                else:
                                    if len(item.connected) > 3:
                                        break
                                    else:
                                        if item.id in item2.connected:
                                            continue
                                        item.connected.append(item2.id)
                                        item2.connected.append(item.id)
                                        pygame.draw.line(gameDisplay, item.art, (item.x_z(player_x_z())), item2.x_z(player_x_z()),
                                                         item.width)


                    for item in dimension.features:
                        if not isinstance(item, cass.WorldObject):
                            continue
                        if not item.type == "lightning":
                            continue
                        item.connected = []

                elif isinstance(item, cass.Laser):
                    item.cycles_drawn += 1
                    item.start_pos[0] -= player_x()
                    item.end_pos[0] -= player_x()
                    item.start_pos[1] -= player_z()
                    item.end_pos[1] -= player_z()
                    pygame.draw.line(gameDisplay, item.color(), item.start_pos, item.end_pos, item.width)
                    #print(item.start_pos)
                    if item.cycles_drawn > 3:
                        item.garbage = True
                        continue


                elif isinstance(item, cass.Enemy):
                    gameDisplay.fill(item.art, [item.x_loc - player_x(), item.z_loc - player_z(), 20, 20])


            if debug:
                # debug info
                disp_text("Position - x: {} z: {}".format(round(player_x() + dimension.x/2),
                          round(player_z() + dimension.z/2)), [75, 10])
                disp_text("Velocity - x: {} z: {}".format(round(dimension.features[player].extra.x_vel,1),
                          round(dimension.features[player].extra.z_vel,1)), [75, 20])

                angl = angle(house[0], center_zero, True)
                # print(angle(house[0], (dimension.x/2, dimension.z/2), True))
                disp_text("mouse - x: {} z: {}".format(round(house[0][0] * -1), round(house[0][1] * -1)), [75, 30])
                disp_text("angle - degrees: {}".format(angl), [75, 40])
                gameDisplay.fill(colors.black, ((dimension.x/2 - 3, dimension.z/2 - 100), (5, 100)))
                pygame.draw.line(gameDisplay, colors.black, center_zero, (house[0]), 5)
                disp_text("entities - #: {}".format(len(dimension.features) - 3), [75, 50])
                disp_text("Build Mode - : {}".format(Build), [75, 60])
                disp_text("Shift - : {}".format(key_map["Shift"]), [75, 70])
                disp_text("Weapons - : {}".format(key_map["Caps"]), [75, 80])
                disp_text("Dimension - : {}".format(dimension.dimension_number), [75, display_h-15])


            if key_map["Caps"]:
                weap = dimension.features[player].extra
                assert isinstance(weap, cass.MainCharacter), "not the player"
                disp_text("ARMED", (display_w - 100, 15), colors.dark_red)

                disp_text("Weapon 1", (display_w - 100, 30))
                status, color = weap.weapon_status("Left")
                disp_text(status, (display_w - 100, 45), color)

                disp_text("Weapon 2", (display_w - 100, 55))
                status, color = weap.weapon_status("Right")
                disp_text(status, (display_w - 100, 65), color)
                #gameDisplay.fill(colors.light_blue, [display_w-300, 0, 150, 200])

                weapon1.cooldown()
                weapon2.cooldown()
                angl = angle(house[0], center_zero, True)

                if key_map["M1"]and weapon1.fire_weapon():
                    result = weapon1.weapon_fired([player_x(), player_z()], angl, (display_h, display_w))
                    for x in result:
                        dimension.features.append(x)

                if key_map["M3"] and weapon2.fire_weapon():
                    result = weapon2.weapon_fired([player_x(), player_z()],angl, (display_h, display_w))
                    for x in result:
                        dimension.features.append(x)

            elif not key_map["Caps"]:
                disp_text("SAFETY", (display_w - 100, 15))
                weapon1.cooldown()
                weapon2.cooldown()
                weapon1.cooldown()
                weapon2.cooldown()


            # handle player input
            for key in key_map:

                if not isinstance(dimension.features[player].extra, cass.Character):
                    print(help(dimension.features[player].extra))
                assert isinstance(dimension.features[player].extra, cass.Character), "Not Character, index = {}".format(player)

                if key_map[key] is True:
                    if key == "w":
                        if not dimension.features[player].extra.z_vel >= 2:
                            dimension.features[player].extra.z_vel = 2
                        key_map["s"] = "hold"

                    elif key == "a":
                        if not dimension.features[player].extra.x_vel >= 2:
                            dimension.features[player].extra.x_vel = 2
                        key_map["d"] = "hold"

                    elif key == "s":
                        if not dimension.features[player].extra.z_vel <= -2:
                            dimension.features[player].extra.z_vel = -2
                        key_map["w"] = "hold"

                    elif key == "d":
                        if not dimension.features[player].extra.x_vel <= -2:
                            dimension.features[player].extra.x_vel = -2
                        key_map["a"] = "hold"
                    continue

                if key_map[key] is False:
                    if key is "w":
                        dimension.features[player].extra.z_vel = 0
                    elif key is "a":
                        dimension.features[player].extra.x_vel = 0
                    elif key is "s":
                        dimension.features[player].extra.z_vel = 0
                    elif key is "d":
                        dimension.features[player].extra.x_vel = 0
                    continue


            # Update Location
            for item in dimension.features:
                if isinstance(item, cass.GameWall):
                    continue
                elif isinstance(item, cass.Teleporter):
                    continue
                elif isinstance(item, cass.DimMarker):
                    if item.thing == "Background":
                        continue
                    if item.thing == "Player":
                        if not key_map["Shift"]:
                            item.extra.swap_position()
                            #print("x: {} z: {}".format(item.extra.x_vel, item.extra.z_vel))
                            item.extra.z_loc = item.extra.z_loc - item.extra.z_vel
                            item.extra.x_loc = item.extra.x_loc - item.extra.x_vel

                            if item.extra.z_vel < 0 and abs(item.extra.z_vel) < 5.1:
                                item.extra.z_vel = item.extra.z_vel - acc
                            if item.extra.z_vel > 0 and abs(item.extra.z_vel) < 5.1:
                                item.extra.z_vel = item.extra.z_vel + acc

                            if item.extra.x_vel < 0 and abs(item.extra.x_vel) < 5.1:
                                item.extra.x_vel = item.extra.x_vel - acc
                            if item.extra.x_vel > 0 and abs(item.extra.x_vel) < 5.1:
                                item.extra.x_vel = item.extra.x_vel + acc

                        elif key_map["Shift"]:
                            item.extra.swap_position()
                            # print("x: {} z: {}".format(item.extra.x_vel, item.extra.z_vel))
                            item.extra.z_loc = item.extra.z_loc - item.extra.z_vel
                            item.extra.x_loc = item.extra.x_loc - item.extra.x_vel

                            if item.extra.z_vel < 0 and abs(item.extra.z_vel) < 4.1:
                                item.extra.z_vel = -.25
                            if item.extra.z_vel > 0 and abs(item.extra.z_vel) < 4.1:
                                item.extra.z_vel = .25

                            if item.extra.x_vel < 0 and abs(item.extra.x_vel) < 4.1:
                                item.extra.x_vel = -.25
                            if item.extra.x_vel > 0 and abs(item.extra.x_vel) < 4.1:
                                item.extra.x_vel = .25

                elif isinstance(item, cass.WorldObject):
                    if item.type == "Particle":
                        item.update_location_generic()
                        if item.lifetime%5 == 0:
                            item.x_vel = random.randint(-4, 4)
                            item.z_vel = random.randint(-4, 4)
                        if item.lifetime%12 == 0:
                            item.art = muted(item.art)
                    if item.type == "bullet":
                        item.update_location_generic()


            # handle proximity
            for item1 in dimension.features:
                if not isinstance(item1, cass.Teleporter):
                    continue
                else:
                    if (plane_distance(player_x() + display_w/2, player_z() + display_h/2, item1.x_loc, item1.z_loc)) > 20:
                        continue
                    assert isinstance(dimension.features[player].extra, cass.MainCharacter), "Not a player"

                    if item1.type is "same":
                        dimension.features[player].extra.x_loc = item1.dest[0] - display_w/2
                        dimension.features[player].extra.y_loc = item1.dest[1]
                        dimension.features[player].extra.z_loc = item1.dest[2] - display_h/2

                    elif item1.type is "exact":
                        
                        if item1.dest[3] is "U":
                            item1.dest[3] = dimension.dimension_number + 1

                        elif item1.dest[3] is "D":
                            item1.dest[3] = dimension.dimension_number - 1
                        elif item1.dest[3] is "R":
                            print("12hoiyu")
                            #item1.dest[3] = random.randint(0, length - 1)
                            
                        if item1.collisions:
                            dimension.features[player].extra.x_loc = 0 - display_w/2
                            dimension.features[player].extra.z_loc = 0 - display_h/2
                            save()
                        player = dimension.features[player].extra
                        restart = True
                        player.x_loc = item1.dest[0]
                        player.y_loc = item1.dest[1]
                        player.z_loc = item1.dest[2]
                        player.dim = item1.dest[3]
                        break


                if not isinstance(item1, cass.GameWall):
                    continue

                assert isinstance(item1, cass.GameWall), "Idk how but this isnt a gamewall"
                if item1.collisions is False:
                    continue
                if not (plane_distance(player_x() + display_w/2, player_z() + display_h/2, item1.x_loc, item1.z_loc)) < 20:
                    continue
                else:
                    assert isinstance(dimension.features[player].extra, cass.MainCharacter), "not a player"
                    dimension.features[player].extra.remove_velocity()
                    dimension.features[player].extra.return_to_prev_pos()

            #Damage
            #for item1 in dimension.features:
            if False:
                #TODO finish this section
                if isinstance(item1, cass.DimMarker):
                    continue
                if isinstance(item1, cass.GameWall):
                    continue
                if isinstance(item1, cass.Teleporter):
                    continue
                if isinstance(item1, cass.Character):
                    continue
                if isinstance(item1, cass.WorldObject):
                    if item1.type == "Particle":
                        continue
                for item2 in dimension.features:
                    if item1 is item2:
                        continue
                    if isinstance(item1, cass.Laser):
                        pass
                        if isinstance(item2, cass.WorldObject):
                            continue
                        if isinstance(item2, cass.GameWall):
                            continue
                        if isinstance(item2, cass.DimMarker):
                            continue
                        if isinstance(item2, cass.Teleporter):
                            continue
                        if isinstance(item2, cass.Character):
                            tolerance = 5 # degrees
                            horse = angle(item2.x_z(), (player_x(), player_z()))
                            if (item1.angle - 5) <= horse and horse <= (item1.angle + 5):
                                if item2:
                                    item2.take_damage(item1.damage)

                    if isinstance(item1, cass.WorldObject):
                        pass


            if restart is True:
                # if we need to reload and start a new dimension
                break


            # (we only really need to remove them all eventually, not all at once)
            # garbage collection
            for x in range(0, len(dimension.features)):
                if isinstance(dimension.features[x], cass.WorldObject):
                    continue
                elif isinstance(dimension.features[x], cass.DimMarker):
                    continue
                elif isinstance(dimension.features[x], cass.Physics):
                    if dimension.features[x].garbage:
                        pos = mouse()
                        pos = pos[0]
                        for x in range(0, 4):
                            pallet_particle(pos)
                        del dimension.features[x]
                        break
                elif isinstance(dimension.features[x], cass.Laser):
                    if dimension.features[x].garbage is True:
                        del dimension.features[x]
                        break

                        
            pygame.display.update()
            clock.tick(fps)


def main_menu():
    paused = True
    while paused:

        gameDisplay.fill(colors.light_brown)
        if ret_button("Enter Game", display_h / 2, display_w / 2, 200, 50, colors.red):
            paused = False
            break
        if ret_button("exit game", display_h / 2, display_w / 4, 200, 50, colors.dark_red):
            quitgame()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quitgame()
            if not event.type == pygame.KEYDOWN:
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quitgame()
                if event.key == pygame.K_RETURN:
                    paused = False
                    break
            if not paused:
                break
        if not paused:
            break

        pygame.display.update()  # shows all the things you have previously drawn ^^^^^
        clock.tick(fps)


GameLoop()