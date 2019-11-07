import classes as cass
import colorsLib as colors
# this is for AI's and presets of normal weapons

# preset bullets
average_bullet = cass.Bullet(2, "normal", None, True, "bullet.PNG", "bullet", None, 0,0,0,0,0,0,0,0,100)
trad_lazer = cass.Laser(colors.red, None, 200, 1, 6)


# preset firing patterns, insert into weapons
normal_gun = (cass.FirePattern(average_bullet, 10, 0), cass.FirePattern(average_bullet, 15, 0))
normal_lazer = (cass.FirePattern(trad_lazer, 0, 0), cass.FirePattern(trad_lazer, 0, 1))
normal_electron = (cass.WorldObject(colors.item_yellow, "lightning", None, 0, 0, 0, None, 5, 1, 1, 1, 3))

#for lightning objects the speed variable is used for any forward momentum,
#angle is the variance of its flow forward, IE how not straight the line will be
std_lightning = (cass.FirePattern(normal_electron, 0, 0))


first_lazer = cass.Weapon("First Lazer", "The name says it all", 20, 1, "Left", 2, 500, normal_lazer, False, False, False)
first_gun = cass.Weapon("GUN", "The name says it all", 20, 2, "Right", 10, 400, normal_gun, False, False, False)
minigun = cass.Weapon("MINIGUN", "The name says it all", 200, 2, "Right", 2, 400, normal_gun, False, False, False)
lightning_cannon = cass.Weapon("lighting cannon", "shoots lignting at enemies", 200, 4, "right", 20, 300, std_lightning,
                               False, False, False)




sturdy_brick = cass.GameWall(0, 0, -125, 1, 0, 0, 0, 0, False, [100, 100, 255], False)

dummy = cass.Enemy("target dummy", "read the name", 0, 0, 0, 0, 20, 20, 20, 20, 20, 2, 0, 0, 0, 0, "practicioner", 0,
                   "inanimate", None, None, None, None) #"dummytransparent.png")
