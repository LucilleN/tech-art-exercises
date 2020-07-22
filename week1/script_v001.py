import maya.cmds
import random

# moving constraints
minX = minY = minZ = -10
maxX = maxY = maxZ = 10

###########
# Helpers #
###########
    
def getRandomShapeName():
    # primitive shape options!
    shapes = ["polyCube", "polySphere", "polyCylinder", "polyCone", "polyTorus"]
    return random.choice(shapes)
    
def createShape(shapeName):
    shapeConstructor = getattr(maya.cmds, shapeName)
    return shapeConstructor()[0]
    
def moveShape(shape, dx, dy, dz):
    maya.cmds.setAttr(shape + ".translateX", dx)
    maya.cmds.setAttr(shape + ".translateY", dy)
    maya.cmds.setAttr(shape + ".translateZ", dz)
   
def getRandomStartingPosition():
    x = random.randint(minX, maxX)
    y = random.randint(minY, maxY)
    z = random.randint(minZ, maxZ)
    return (x, y, z)
    
##########
# Script #
##########

# clear the current selection
maya.cmds.select(cl = True)

# get starting and ending time of the time slider
startTime = maya.cmds.playbackOptions(query=True, min=True)
# endTime = maya.cmds.playbackOptions(query=True, max=True)
endTime = 1200

# set the current time to the beginning of the time slider
# maya.cmds.currentTime(startTime)

iterations = 10
currentStartTime = startTime
currentEndTime = endTime / iterations

for iteration in range(iterations):
    
    (x0, y0, z0) = getRandomStartingPosition()
    
    for i in range(10):
        # create a shape
        shape = createShape(getRandomShapeName())
        
        # reset current time back to beginning
        maya.cmds.currentTime(currentStartTime)
        
        # set a keyframe at the current starting position
        moveShape(shape, x0, y0, z0)
        maya.cmds.setKeyframe(shape)
        
        # randomly pick a future time
        randomTime = random.randint(currentStartTime + 1, currentEndTime)
        # change the current time to be the new random time
        maya.cmds.currentTime(randomTime)
        # move the cube a random x, y, and z value
        moveShape(
            shape, 
            random.randint(minX, maxX), 
            random.randint(minY, maxY), 
            random.randint(minZ, maxZ), 
        )
        # set the second keyframe
        maya.cmds.setKeyframe()   
    
    currentStartTime = currentEndTime
    currentEndTime += endTime / iterations






