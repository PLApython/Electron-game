# base class for all objects, even if they are not effected by physics
import colorsLib as colors
import random
import math
import time


class Physics:
    def __init__(self, x, y, z, dimension, height, weight, width, length, collides):
        # position (m) from (0,0,0)
        self.x_loc = x
        self.y_loc = y
        self.z_loc = z

        # velocity (m/s)
        self.x_vel = 0
        self.y_vel = 0
        self.z_vel = 0

        # acceleration (m/s^2)
        self.x_acc = 0
        self.y_acc = 0
        self.z_acc = 0

        # is it influenced by gravity?
        self.gravity = True

        # world dimension ie: overworld, hell, etc...
        self.dim = dimension

        # facing what direction?
        # direction angle on the horizion line
        self.horiz = 0  # (radians)
        # direction angle perpendicular to the horizion
        self.vert = 0  # (radians)
        # facing angles are in radians measured where the x,z plane is the horizion and angle (0,0) is facing towards +x

        # dimension in the +y direction (meters)
        self.height = height

        # weight in kilograms (kilograms)
        self.weight = weight

        # dimension in the z axis (meters)
        self.width = width

        # direction in the +x dimension (meters)
        self.length = length

        # by default
        self.shape = "square"

        # if false, no collisions are computed for this object
        self.collisions = collides

        # electric charge - this is exclusive for this version of physics, used for some weapons
        self.charge = 0

        self.previous = [x, y, z]
        # this is changed such that it should be deleted
        self.garbage = False

    # updates all physical motion variables according to newtonian physics
    #use this unless you have a specific need for a different behaviour
    def update_location_generic(self):
        self.x_vel += self.x_acc
        self.x_loc += self.x_vel

        self.y_vel += self.y_acc
        self.y_loc += self.y_vel

        self.z_vel += self.z_acc
        self.z_loc += self.z_vel

    #used for collisions
    def return_to_prev_pos(self):
        self.x_loc = self.previous[0]
        self.y_loc = self.previous[1]
        self.z_loc = self.previous[2]

    #used for collisions
    def swap_position(self):
        self.previous[0] = self.x_loc
        self.previous[1] = self.y_loc
        self.previous[2] = self.z_loc

    #used for collisions
    def remove_velocity(self):
        self.x_vel = 0
        self.y_vel = 0
        self.z_vel = 0

    #initialize velocity
    def initv(self,x,y,z):
        self.x_vel = x
        self.z_vel = z
        self.y_loc = y

    def x_z(self, offset=None):
        if not offset:
            offset = [0,0]
        return [self.x_loc - offset[0], self.z_loc - offset[1]]

    def short(self, x,z):
        self.x_loc = x
        self.z_loc = z


class FirePattern:
    def __init__(self, bullet, speed, angle):
        # the actual bullet object to be created (can also be beam, or ai object)
        self.bullet = bullet

        # the speed of the exiting object, (useless for beams)
        self.speed = speed

        # the angle of exiting the weapon
        self.angle = angle


class Weapon:
    def __init__(self, name, desc, val, at_type, hand, speed, at_range, pattern, warmup, heat, speed_up, status=None):

        # name of item
        self.name = name

        # object description
        self.description = desc

        # price if any
        self.value = val

        # this is used to display weapon information to the player
        if status:
            self.status = status
        else:
            self.status = "Nominal"
        # what kind of attack this weapon produces
        # 1 is a beam, 2 is a cannon type, 3 is a spawner (supports AI), 4 is lightning
        # beams are instant
        # cannons fire a bullet
        # spawners add an entity to the dimension (with a lifetime to limit the number of active entities) lightning goes here
        self.attack_type = at_type

        # a list of the entities to be created
        self.pattern = pattern

        """
        eg:
         FirePattern(info)
        bullet2 = bullet(info)
        bullet2 = bullet(info)
        self.patten = [bullet1, bullet2, bullet3] 
        """

        # left, right or any, specifies which side the weapon can be carried on
        self.hand = hand

        # how quickly the weapon can be used
        self.attack_speed = speed

        # counts the ticks since the last firing of the weapon, when this equals the speed it fires
        self.time_since_last_fire = 0

        # if true, takes a few ticks to begin firing, then fires continuously
        self.warmup = warmup
        self.warmed = False
        # if true weapon gets hotter with every shot
        self.heatup = heat

        # if true, weapon fires more quickly with each shot
        self.speed_up = speed_up

        # range where it is most effective, be it melee or at extreme range in meters
        self.range = at_range
        self.firing = False

    def fire_weapon(self):
        # run this command as long as the proper button is pressed, this will return true if the weapon is to be fired
        if self.heatup >= 400:
            self.status = "Overheat"
            return False
        else:
            self.status = "Nominal"
        self.time_since_last_fire += 1

        if self.speed_up:
            if self.heatup > 1:
                self.time_since_last_fire += self.heatup
            else:
                self.time_since_last_fire += 1

        if self.warmup:
            if self.time_since_last_fire >= (20 + self.attack_speed):
                if self.heatup:
                    if self.heatup == True:
                        self.heatup = 1

                    else:
                        self.heatup += 2
                # create the bullet
                self.time_since_last_fire = 0
                return True
                
        elif self.time_since_last_fire >= self.attack_speed:
            if self.heatup:
                if self.heatup == True:
                    self.heatup = 1

                else:
                    self.heatup += 2
                # create bullet
            self.time_since_last_fire = 0
            return True
            
        # dont create bullet
        return False


    def weapon_fired(self, origin, angle, window):
        created = []
        origin[0] += window[1]/2
        origin[1] += window[0]/2
        if self.attack_type == 4:
            num = round(self.range * 1, 0)
            skip = 0
            for x in range(0,int(num)):
                if x%2==0:
                    skip +=1
                    continue
                sine = math.sin(math.radians(-1 * angle - 90))
                cosine = math.cos(math.radians(-1 * angle - 90))
                created.append(WorldObject(colors.item_yellow, "lightning", None, 0, 0, 0, None, 5, 1, 1, 1, 3))
                created[x - skip].short(x*cosine + origin[0] + -.1*random.randint(-1 * x, x), x*sine + origin[1] + .1*random.randint(-1* x, x))

            for x in created:
                assert isinstance(x, WorldObject), "not a proper object"
                x.x_vel = random.randint(-2, 2)
                x.y_acc = random.randint(-5, 5) / 10

        elif self.attack_type in [2, 3]: #boolet
            for x in range(0, len(self.pattern)):
                created.append(WorldObject(colors.green, "bullet", None, origin[0], 0, origin[1], None, 1, 1, 1, 1, 100))
                created[x].x_vel = math.cos(-1 * math.radians(angle + self.pattern[x].angle + 90)) * self.pattern[x].speed
                created[x].z_vel = math.sin(-1 * math.radians(angle + self.pattern[x].angle + 90)) * self.pattern[x].speed

        elif self.attack_type == 1:
            for x in range(0, len(self.pattern)):
                created.append(self.pattern[x].bullet)
                created[x].create(origin, angle)


        return created


    def cooldown(self):
        # run this every round to cooldown
        if self.heatup > 0:
            self.heatup -= 1
        if self.heatup <= 0:
            self.heatup = True

    def status_ind(self):
        # returns all the required arguments to display the weapon status
        if self.status == "Nominal":
            if self.firing and not self.warmed:
                return "Warming", colors.item_yellow
            else:
                return self.status, colors.orange
        elif self.status == "Jammed":

            return self.status, colors.dark_red
        elif self.status == "Overheat":

            return self.status, colors.red
        else:
            return "Error", colors.light_brown

    def ready_to_fire(self):
        # returns the percentage of completion to the next shot
        if self.status is "Nominal":
            frac = abs(self.time_since_last_fire - self.attack_speed)
            return frac, (255 - 255*frac, 0 + 255*frac, 0)
        if self.status is "Jammed":
            return 0, (0,0,0)
        if self.status is "Overheat":
            return self.attack_speed, (255,0,0)

# anything that moves or is intractable, anything more complex than a wall
class Character(Physics):

    def __init__(self, name, desc, x, y, z, dimension, height, weight, width, length, max_h, nat_reg, defense, armor,
                 strength, speed, title, meta, status):

        # activate the class[physics] initializer
        Physics.__init__(self, x, y, z, dimension, height, weight, width, length, True)

        self.current = "Normal"

        # used to refer to object in story situations
        self.name = name
        # a given title that is used to address or decorate a character
        self.title = title

        # a descritption
        self.description = desc

        # current health
        self.health = max_h
        # max health
        self.max_h = max_h
        # natural_regeneration (applied upon call, not automatic)
        self.h_regen = nat_reg

        # damage taken = weakness * (incoming damage * defense - resistance)
        self.defense = defense  # a float less than 1 but greater than 0
        self.armor = armor  # the total power ranking of all worn armor

        # a number representing (strength * 5 kilos) comfortable lift weight
        # (may scale with size, but you have to handle  manually)
        self.strength = strength

        # a number to representing (speed * 1 m/s) comfortable move speed laterally
        self.speed = speed
        self.max_speed = speed
        # max_speed does not get modified by enviromental hazards


        # effects how often the character can activate regeneration effects\
        # effects how much the character can eat and store
        # smaller numbers eat more, but regen more
        self.metabolism = meta

        # a description of the player status
        self.status = status

    def full_name(self):
        return self.name + ": " + self.title

    def regen(self):
        # sending a round argument checks if the creature gets a chance to regen this round of battle
        self.health += self.h_regen
        if self.health > self.max_h:
            self.health = self.max_h
            self.status = "well rested"

    # damage is the RAW in
    def take_damage(self, damage):
        self.health -= self.armor * damage
        self.health = round(self.health, 3)
        return self.check_health()

    def check_health(self):
        if self.health <= 0:
            print("you died")
            return False
        else:
            return True


class EditorPreset:
    # this is a preset for the editor to make blocks
    def __init__(self, name):
        # the name of the preset
        self.name = name

        # the color to be created
        self.color = [0, 0, 0, 0]

        # is the block made with color or image?
        self.preference = "Sprite"

        # block length
        self.length = 20

        # block width
        self.width = 20

        # load the image here
        self.image = None

        self.collisions = True
        self.breakable = False

    def intcolor(self):
        self.color[0] = round(self.color[0])
        self.color[1] = round(self.color[1])
        self.color[2] = round(self.color[2])


    def setall3(self, num):
        self.color[0] = num
        self.color[1] = num
        self.color[2] = num


    def color_na(self):
        return self.color[0], self.color[1], self.color[2]


    def ret_visual(self):
        if self.preference == "Color":
            return self.color_na()
        if self.preference == "Sprite":
            return self.image


class DrawAction:
    def __init__(self, function, arg):
        __function = function
        args = arg
    def execute(self):
        self.__function(self.args)


# X+X+X+X+X+X+X+X+X+X+X+X+X+X+X+X+X
# final Products
# X+X+X+X+X+X+X+X+X+X+X+X+X+X+X+X+X


# a game object
class GameWall(Physics):
    def __init__(self, x, y, z, dimension, height, weight, width, length, breakable, art, collides):

        # activate the class[physics] initializer
        Physics.__init__(self, x, y, z, dimension, height, weight, width, length, collides)

        # the image used for rendering purposes
        self.art = art

        # if false, is unbreakable, if true, is the breaking difficulty, a float greater than zero
        self.breakable = breakable

        #if not collides:
        #    self.collides = True
        #else:
        #    self.collides = collides

    # secondary init method
    #short as in shorthand
    def short(self, x, z, breakable, art, collides):
        self.x_loc = x
        self.z_loc = z
        self.breakable = breakable
        self.art = art
        self.collisions = collides

        self.y = 0
        self.dimension = 0
        self.height = 2
        self.width = 2
        self.length = 2
        self.weight = 0

    def get_art(self):
        if self.art is list:
            return "color", self.art
        return "image", self.art


class Dimension:
    def __init__(self, name, desc, x_size, y_size, z_size, dim_num, gravity, features):
        self.name = name
        self.description = desc
        self.x = x_size
        self.y = y_size
        self.z = z_size
        self.dimension_number = dim_num

        # False if no gravity, a strength in m/s if true, gravity is applied on the x -  z plane pulling towards -y
        self.gravity = gravity

        # a list of every object on the plane
        self.features = features


class DimMarker:
    def __init__(self, thing, x, y, z, extra=None):
        # a dim marker is different from a WorldObject, a dimmarker is for things that are used for initialization
        # a dim marker is usually for constants in a dimension, like the player starting position, or the background
        # a marker for what this instance represents in the dimension bracket
        self.thing = thing
        self.x = x
        self.y = y
        self.z = z
        # any extra information, useful for randomly generated things
        self.extra = extra


class WorldObject(Physics):
    def __init__(self, art, item_type, ai, x, y, z, dimension, height, weight, width, length, lifetime):

        # activate the class[physics] initializer
        Physics.__init__(self, x, y, z, dimension, height, weight, width, length, True)

        # a string denoting the item (bullet, money, particle, lightning)
        self.type = item_type
        self.id = 0
        if self.type == "lightning":
            self.id = time.time()

        self.connected = []

        # used to remove objects once they are irrelevant and declutter dimensions
        # if false, then is not removed
        self.lifetime = lifetime

        # an image with a clear alpha channel preferrably
        # or an RGB color
        self.art = art

        # an ai program that will take in its current surroundings
        self.ai = ai


    def life(self):
        # returns true if the object should be deleted
        if not self.lifetime:
            return False
        # subtracts one from the lifetime
        # returns true if the object should be deleted
        self.lifetime -= 1
        if self.lifetime <= 0:
            return True
        else:
            return False


class Bullet(WorldObject):
    def __init__(self, damage, damage_type, effect, friendly, art, item_type, ai, x, y, z, dimension, height, weight,
                 width, length, lifetime):

        WorldObject.__init__(self, art, item_type, ai, x, y, z, dimension, height, weight, width, length, lifetime)

        # damage on a hit
        self.damage_amt = damage

        # the type of damage
        # normal
        # explosive
        #(all should be normal for now)
        self.damage_type = damage_type

        # effects include: charge, magnetize, heat
        # you only get one per bullet
        self.effect = effect

        # true if on the side of the player, false if not
        self.allignment = friendly

    def ai_commands(self, radius, view, mouse_loc, player_loc, important_objects):
        if self.ai_exists:
            self.x_vel, self.z_vel, self.y_vel= self.ai(radius, view, mouse_loc, player_loc, self.allignment, important_objects)
        elif self.ai == "Particle":
            self.update_location_generic()
        # this is a simple ai for very small things, this should be very minor things happening


class Laser:
    def __init__(self, color, effect, max_range, damage, width=None):

        # a simple RGB or "Random"
        self.__color = color

        # effects include: charging, magnetizing, and heating
        self.effect = effect

        self.max_range = max_range * -1

        # damage dealt on a direct hit, (for laser this will be really low) includes: "random"
        self.__damage = damage

        # when this reaches 3 it will be deleted
        self.cycles_drawn = 0

        self.angle = 0

        if not width:
            width = 6

        # beam width, does influence hitbox
        self.width = width

        self.garbage = False

        self.start_pos = [0, 0]
        self.end_pos = [0, 0]

    def create(self, start_pos, angle):

        self.angle = angle

        self.start_pos = start_pos#[start_pos[0]/2,start_pos[1]/2]

        self.end_pos = [((math.sin(math.radians(angle)) * self.max_range) + start_pos[0]),
                        (math.cos(math.radians(angle)) * self.max_range) + start_pos[1]]


    def damage(self):
        if self.__damage == "random":
            return random.randint(0,5)
        else:
            return self.__damage


    def color(self):
        if self.__color == "random":
            return [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        else:
            return self.__color


class MainCharacter(Character):
    def __init__(self, name, desc, x, y, z, dimension, height, weight, width, length, max_h, nat_reg, defense, armor,
                 strength, speed, meta, title, gold, weapons, status, hands, presets=None):

        Character.__init__(self, name, desc, x, y, z, dimension, height, weight, width, length, max_h, nat_reg, defense, armor,
                           strength, speed, title, meta, status)

        # a list of weapon options
        self.weapons = weapons

        # available currency
        self.gold = gold

        # a dictionary of numbers specifying which weapon from self.weapons is used fow which hand(s)
        # self.hands = ["Left": 1, "Right": 4]
        # weapons cannot be shared between arms
        self.hand = hands

        # a list of hands objects specifying presets of weapon parings
        self.presets = presets

    def add_weapon(self, item):
        assert isinstance(item, Weapon), "not valid weapon"
        self.weapons.append(item)
        # returns the index of the weapon
        # return self.weapons.index(item)

    def item_stats(self, index):
        pass

    def equip_weapon(self, hand, index):
        if index == hand["Left"] or hand["Right"]:
            # if the weapon is already equipped then it cant be equipped anywhere else
            return False
        self.hand[hand] = index
        return True
        # returning true from this function says that it was sucessful


    def weapon_status(self, hand):
        return self.weapons[self.hand[hand]].status_ind()


class Enemy(Character):
    def __init__(self, name, desc, x, y, z, dimension, height, weight, width, length, max_h, nat_reg, defense, armor,
                 strength, speed, title, meta, status, gives, weapons, hands, ai, art=None):

        Character.__init__(self, name, desc, x, y, z, dimension, height, weight, width, length, max_h, nat_reg, defense,
                           armor, strength, speed, title, meta, status)

        # list of what the player gets on enemy death
        # use dies() to give it to the player
        self.__gives = gives

        # a list of weapons, they are all useable
        self.weapons = weapons

        # enemies can have many hands for lots of weapons
        # works the same as hands for MainCharacter
        self.hands = hands

        # the name of an ai function from AIS
        self.ai = ai

        if art:
            self.art = art
        else:
            self.art = colors.dark_red

    #use this with a preset from AIS.py this is for initializing them to a position
    def short(self,x,z, name=None,des=None, title=None, gives=None):
        self.x_loc = x
        self.x_loc = z

        if name:
            self.name= name
        if des:
            self.description = des
        if title:
            self.title = title
        if gives:
            self.gives = gives

    def preset(self,number, x, y):
        pass


    def dies(self):
        pass


class Teleporter(Physics):
    def __init__(self, destination, tele_type, art, cooldown, x, y, z, dimension, height, weight, width, length, collides):
        # collisions is currently being used to determine if the leaving dimension should be saved or not
        Physics.__init__(self, x, y, z, dimension, height, weight, width, length, collides)
        # relative, exact, swap, same
        # relative moves the subject to the same coords in the other dimension
        # exact will specify a new location using exact coords
        # swap (same dimension) requires two things to switch place
        # same moves within the same dimension
        self.type = tele_type
        # the destination dimension
        self.dest = destination
        # the art or color to be used
        self.art = art
        # the time between possible teleports
        self.cooldown = cooldown
        # used for the actual countdown
        self.current = 0


class Sign:

    pass  # TODO make this

