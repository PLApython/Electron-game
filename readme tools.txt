damage types - one attack can have multiple types
    ranged
    melee
    physical
        piercing - relies on pointyness is speed based and often disjointed
        slashing - sharp but also has a larger area of effect than piercing (counts as .3 blunt, .7 pierce)
        blunt -  momentum based- brute force and strength based often enviromental
    elemental
        water
        earth
        fire
        air
        aether
        magical
    mental
        psionic
        dampening

armor
    effects tags
        Thorns
        Hot

HasBrain
    status'


the y axis is always the height and gravity always pulls towards -y
the xz plane is the horizion
for non rotating objects, the z axis is always width, and the x axis is always length
all rotation vectors of the xz plane are measured from +x with the first quadrent being between (x+,z+)
all rotation vectors of the xy-y plane are measured as 0 being on the plane, and a positive rotation being towards +y
all rotations are in radians


cass.Dimension(
                "The Shadow plains",
                "The test world",
                1000,
                20,
                750,
                1,
                9.8,
                [
                 cass.DimMarker("Background", 0,0,0, [100,100,100]),
                 cass.DimMarker("Player", 0,0,0),
                 cass.GameWall(50,0,50,1,10,10,10,10,False,[255,255,255], False),
                 cass.GameWall(50,0,100,1,10,10,10,10,False, "RandomAS", False),
                 cass.DimMarker("Player", 0,0,0)
                ]
               )

