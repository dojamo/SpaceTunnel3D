"""
 3D Tunnel
 Developed by Dominic James-Moore

"""


# Increase the ship size
# decrease bubble size
# do a very tall thin
# make the shadow thicker but the collision area smaller;

# !!! CLEAN THIS UP 
import pygame, sys, math, asyncio
from pygame.locals import *
from pygame.time import *
from random import randrange

from pygame.rect import *

# GLOBALS

SCREENWIDTH = 1920  # hardcoded to surface 4
SCREENHEIGHT = 1080 # hardcoded to surface 4

# these are set based on a landscape screen, it just gives better gameplay regardless of orientation
DEFAULT_RECT_WIDTH = SCREENWIDTH * 0.6
DEFAULT_RECT_HEIGHT = SCREENHEIGHT * 0.6

# If it's mobile, change to portrait mode
if sys.platform == "emscripten":
    import platform
    platform.window.document.body.style.background = "black" # any gaps around the game are black, not grey
    if platform.window.innerHeight > platform.window.innerWidth: # portrait screen
        SCREENWIDTH = 1080
        # match the height to the browser's shape so there are no gaps at the sides
        SCREENHEIGHT = int(1080 * platform.window.innerHeight / platform.window.innerWidth)
    if platform.window.matchMedia("(pointer: coarse)").matches:
        ISMOBILE = True
    else:
        ISMOBILE = False  
else:
    ISMOBILE = False

ORIGINX = SCREENWIDTH / 2
ORIGINY = SCREENHEIGHT / 2
K_NUMERATOR = 768

##############################################################################
# DRAWING CLASSES - TO BE CLEANED UP                                         #
##############################################################################


class FloatingObject():
    def __init__(self, MinDepth):
        self.MinDepth = MinDepth
        self.CreateObject()
    # a list of other shape objects
    # a draw function
    # let them do the transforms (we need inheritance for the overall transform feature)

    def CreateObject(self):
        self.ShapeList = list()
        self.HexagonList = list()
        self.LineList = list()
        self.CircleList = list()
        
        NoOfHex = 90
        
        for i in range (1, NoOfHex): # DO WE NEED THE -1?
            xColour = (175 + i/1.5, 175 + i/1.5, 175 + i/1.5)
            xSize = 6+ i/12
            # LEFT, = -35
#            self.xHexagon = hexagon(-35, 50, self.MinDepth + NoOfHex-i, xSize,  xColour)

            TemplateObject = template_hexagon(-35, 50, self.MinDepth + NoOfHex-i, xSize)
            SimpleShape = simple_shape(-35, 50, self.MinDepth + NoOfHex-i, TemplateObject, xColour)
            self.ShapeList.append(SimpleShape)

            # RIGHT, = +35
#            self.xHexagon = hexagon(35, 50, self.MinDepth + NoOfHex-i, xSize,  xColour)
            TemplateObject = template_hexagon(+35, 50, self.MinDepth + NoOfHex-i, xSize)
            SimpleShape = simple_shape(+35, 50, self.MinDepth + NoOfHex-i, TemplateObject, xColour)
            self.ShapeList.append(SimpleShape)

#            self.HexagonList.append(self.xHexagon)        

        # Create a little hexagonal ball in the middle
        # manual point list
        BallSizes = (2,2,2,2,3,3,3,3,3,4,4,4,4,4,5,6,6,6,6,7,7,7,7,7,8,8,8,8,8,8,9,9,9,9,9,9,9,8,8,8,8,8,8,7,7,7,7,7,6,6,6,6,5,5,5,5)
        for i in range(1, len(BallSizes)):
            xColour = (85 + i, 145 + i, 190 + i)
            xSize = BallSizes[i]
            
            TemplateObject = template_hexagon(0, 50, self.MinDepth + 50 -i, xSize)
            SimpleShape = simple_shape(0, 50, self.MinDepth + 50 -i, TemplateObject, xColour)
            self.ShapeList.append(SimpleShape)
            
            
        # create the magic hexagon
        self.xMagicHexagon = self.ShapeList[200]
        self.xMagicHexagon.xColour=(200, 80, 40)
        
        

        # create the lines (self, StartX, StartY, StartZ, EndX, EndY, EndZ, Weight, Colour):
        xColour = (220, 220, 220)
        self.xLine = line(-30, 50, self.MinDepth , 30, 50, self.MinDepth + 40, 1, xColour)
        self.LineList.append(self.xLine)
        self.xLine = line(-30, 50, self.MinDepth +40, 30, 50, self.MinDepth, 1, xColour)
        self.LineList.append(self.xLine)
        
        # Burners  (CentreX, CentreY, CentreZ, Size, Colour, Fill
        # start with one circle each side, in deep red.
        for i in range (1, 11):
            xColour = (200, (70 +(i*10)), 30 +(i*5))
            self.xCircle = circle(-35, 50, self.MinDepth - 5-i*2, int(8-i/2), xColour, 0)
            self.CircleList.append(self.xCircle)
            self.xCircle = circle(35, 50, self.MinDepth - 5-i*2, int(8-i/2), xColour, 0)
            self.CircleList.append(self.xCircle)
         
    def MoveObject(self, ChangeX, ChangeY, ChangeZ):
    
        for ListLine in self.LineList :
            ListLine.MovePoints(ChangeX, ChangeY, ChangeZ)

        for ListShape in self.ShapeList :
            ListShape.MovePoints(ChangeX, ChangeY, ChangeZ)

        for ListCircle in self.CircleList :
            ListCircle.MovePoints(ChangeX, ChangeY, ChangeZ)


    def DrawObject(self, surface, Camera):

        for ListLine in self.LineList :
            ListLine.TransformPoints(Camera)
            ListLine.DrawPoints(surface)

        for ListShape in self.ShapeList :
            ListShape.TransformPoints(Camera)
            ListShape.DrawPoints(surface)
                   
        xColour = (180, 150, 60)

        for ListCircle in self.CircleList :
            ListCircle.TransformPoints(Camera)
            ListCircle.DrawCircle(surface)
           
class circle(): # this is greatly simplified.  I think for standard draw features it will need to be different.
    def __init__(self, CentreX, CentreY, CentreZ, Size, Colour, Fill): # this is not true 3d. hardcoded size
        self.xCentreX = CentreX
        self.xCentreY = CentreY
        self.xCentreZ = CentreZ
        self.xSize = Size
        self.xColour = Colour
        self.xFill = Fill
        # self.xPointList = list()
        # self.CreatePoints()
    
    #def CreatePoints(self):
        #self.xNewPoint = (self.xCentreX, self.xCentreY, self.xCentreZ)
        # self.xPointList.append(self.xNewPoint)
        
    def MovePoints(self, xMoveX, xMoveY, xMoveZ):
        self.xCentreX += xMoveX
        self.xCentreY += xMoveY
        self.xCentreZ += xMoveZ
        if self.xCentreZ <= 10 : self.xCentreZ = 10
        
    def TransformPoints(self, Camera):
        
        self.Camera = Camera
        # self.xPointDrawList = list()

        # Convert the 3D coordinates to 2D using perspective projection.

        # for ListPoint in self.xPointList:
        k = K_NUMERATOR / self.xCentreZ # depth modifier.  Hardcode value should be considered in relation to max depth.
        self.xDrawPoint = ( (int( (self.xCentreX - self.Camera.x) * k + ORIGINX)), int((self.xCentreY - self.Camera.y) * k + ORIGINY) )
        # self.xPointDrawList.append(self.xNewPoint)
               
    def DrawCircle(self, surface): #colour
        pygame.draw.circle(surface, self.xColour, self.xDrawPoint, self.xSize, self.xFill)
            
            
######## WHEN WE CALL SIMPLE SHAPE #####
# Do two calls: create a point list (e.g. make a hexagon, a pentagon, a line) then give it to shape to create the shape
# AT THE MOMENT EVERYTHING IS AALINES, NO CONNECTORS
# HEXAGON NEEDS A RADIUS, A CENTRE POINT AND A NUMBER OF POINTS (SIX).  CAN ALSO COVER SQUARE, PENTAGON, TRIANGLE ETC
# A LINE JUST HAS BEGGINNIG
            
# WE COULD HAVE ONE 'POINT LIST GENERATOR' / 'SHAPE GENERATOR' CLASS, so there's only one object, and we call it generate a bunch of point lists.
 



class complex_shape(): # a list of lists;
    pass

class simple_shape():
    # THIS IS JUST ONE SHAPE.  EG ONE HEXAGON, ONE LINE.
    # IT HAS A LIST OF POINTS, IT WILL DRAW A LINE BETWEEN THOSE POINTS, THE POINTS CAN BE MOVED AND THEN TURNED TO 2D
    # THAT'S IT.
    def __init__(self, CentreX, CentreY, CentreZ, TemplateObject, Colour):
        self.xCentreX = CentreX # keep these for now.
        self.xCentreY = CentreY
        self.xCentreZ = CentreZ
        self.TemplateObject = TemplateObject
        self.xPointList = list()
        self.xColour = Colour
        self.decant_points()
        
    def decant_points(self):  # take the points of the template object and then 
        for point in self.TemplateObject.xPointList :
            self.xPointList.append(point)
                                
    def MovePoints(self, xMoveX, xMoveY, xMoveZ):
        for ListPoint in self.xPointList:
            ListPoint [0] += xMoveX
            ListPoint [1] += xMoveY
            ListPoint [2] += xMoveZ
            if ListPoint [2] <= 10 : ListPoint [2] = 10

        self.xCentreX += xMoveX
        self.xCentreY += xMoveY
        self.xCentreZ += xMoveZ
        if self.xCentreZ <= 10 : self.xCentreZ = 10 # this is the only place this is used. 


    def TransformPoints(self, Camera):
        
        self.Camera = Camera
        self.xPointDrawList = list()

        # Convert the 3D coordinates to 2D using perspective projection.

        for ListPoint in self.xPointList:
            if ListPoint[2] > 0:
                k = K_NUMERATOR / ListPoint[2] # depth modifier.  Hardcode value should be considered in relation to max depth.

                self.xNewPoint = ( (int( (ListPoint[0] - self.Camera.x) * k + ORIGINX)), int((ListPoint[1] - self.Camera.y) * k + ORIGINY) )
                self.xPointDrawList.append(self.xNewPoint)
            
    def DrawPoints(self, surface):
        pygame.draw.aalines(surface, self.xColour, True, (self.xPointDrawList), 1)        


###### KIND OF UP TO HERE #########
    
class template_hexagon():
    def __init__(self, CentreX, CentreY, CentreZ, Radius):
        self.xCentreX = CentreX
        self.xCentreY = CentreY
        self.xCentreZ = CentreZ
        self.xRadius = Radius
        self.xPointList = list()
        self.CreatePoints()
        
    def CreateOnePoint(self, xRadians):

        self.xNewPoint = [(self.xCentreX + self.xRadius * math.cos(xRadians)), (self.xCentreY + self.xRadius * math.sin(xRadians)), self.xCentreZ]
        self.xPointList.append(self.xNewPoint)

    def CreatePoints(self):
        # first move 1/12 radians to find the first point, then
        xRadians = (2 * math.pi) / 12
        self.CreateOnePoint(xRadians)    

        # now go through the next 6
        for i in range (1, 6) :
            xRadians = ((2 * math.pi) / 12) * (1 + (i *2))
            self.CreateOnePoint(xRadians)
    
class template_line():
    def __init__(self, StartX, StartY, StartZ, EndX, EndY, EndZ, Weight, Colour):
        self.xStartX = StartX
        self.xStartY = StartY
        self.xStartZ = StartZ
        self.xEndX = EndX
        self.xEndY = EndY
        self.xEndZ = EndZ
        self.xWeight = Weight
        self.xColour = Colour
        self.xPointList = list()
        self.CreatePoints()
        
    def CreatePoints(self):
        self.xNewPoint = [self.xStartX, self.xStartY, self.xStartZ]
        self.xPointList.append(self.xNewPoint)
        self.xNewPoint = [self.xEndX, self.xEndY, self.xEndZ]
        self.xPointList.append(self.xNewPoint)


########
    
class line():
    def __init__(self, StartX, StartY, StartZ, EndX, EndY, EndZ, Weight, Colour):
        self.xStartX = StartX
        self.xStartY = StartY
        self.xStartZ = StartZ
        self.xEndX = EndX
        self.xEndY = EndY
        self.xEndZ = EndZ
        self.xWeight = Weight
        self.xColour = Colour
        self.xPointList = list()
        self.CreatePoints()
    
    def CreatePoints(self):
        self.xNewPoint = [self.xStartX, self.xStartY, self.xStartZ]
        self.xPointList.append(self.xNewPoint)
        self.xNewPoint = [self.xEndX, self.xEndY, self.xEndZ]
        self.xPointList.append(self.xNewPoint)
    
    def MovePoints(self, xMoveX, xMoveY, xMoveZ):
        for ListPoint in self.xPointList:
            ListPoint [0] += xMoveX
            ListPoint [1] += xMoveY
            ListPoint [2] += xMoveZ
            
            if ListPoint [2] <= 10 : ListPoint [2] = 10

    def TransformPoints(self, Camera):
        
        self.Camera = Camera
        self.xPointDrawList = list()

        # Convert the 3D coordinates to 2D using perspective projection.

        for ListPoint in self.xPointList:
            k = K_NUMERATOR / ListPoint[2] # depth modifier.  Hardcode value should be considered in relation to max depth.
            self.xNewPoint = ( (int( (ListPoint[0] - self.Camera.x) * k + ORIGINX)), int((ListPoint[1] - self.Camera.y) * k + ORIGINY) )
            self.xPointDrawList.append(self.xNewPoint)
               
    def DrawPoints(self, surface):
        pygame.draw.aalines(surface, self.xColour, True, (self.xPointDrawList), 1)
            

    
    
    #######
    
class hexagon():
    def __init__(self, CentreX, CentreY, CentreZ, Radius, Colour):
        self.xCentreX = CentreX
        self.xCentreY = CentreY
        self.xCentreZ = CentreZ
        self.xRadius = Radius
        self.xColour = Colour
        self.xPointList = list()
        self.CreatePoints()
        
    def CreateOnePoint(self, xRadians):

        self.xNewPoint = [(self.xCentreX + self.xRadius * math.cos(xRadians)), (self.xCentreY + self.xRadius * math.sin(xRadians)), self.xCentreZ]
        self.xPointList.append(self.xNewPoint)

    def CreatePoints(self):
        # first move 1/12 radians to find the first point, then
        xRadians = (2 * math.pi) / 12
        self.CreateOnePoint(xRadians)    

        # now go through the next 6
        for i in range (1, 6) :
            xRadians = ((2 * math.pi) / 12) * (1 + (i *2))
            self.CreateOnePoint(xRadians)

    def MovePoints(self, xMoveX, xMoveY, xMoveZ):
        for ListPoint in self.xPointList:
            ListPoint [0] += xMoveX
            ListPoint [1] += xMoveY
            ListPoint [2] += xMoveZ
            if ListPoint [2] <= 10 : ListPoint [2] = 10

        self.xCentreX += xMoveX
        self.xCentreY += xMoveY
        self.xCentreZ += xMoveZ
        if self.xCentreZ <= 10 : self.xCentreZ = 10


    def TransformPoints(self, Camera):
        
        self.Camera = Camera
        self.xPointDrawList = list()

        # Convert the 3D coordinates to 2D using perspective projection.

        for ListPoint in self.xPointList:
            if ListPoint[2] > 0:
                k = K_NUMERATOR / ListPoint[2] # depth modifier.  Hardcode value should be considered in relation to max depth.

                self.xNewPoint = ( (int( (ListPoint[0] - self.Camera.x) * k + ORIGINX)), int((ListPoint[1] - self.Camera.y) * k + ORIGINY) )
                self.xPointDrawList.append(self.xNewPoint)
            
    def DrawPoints(self, surface):
        pygame.draw.aalines(surface, self.xColour, True, (self.xPointDrawList), 1)        

# # # # # # # # #            
            
            
##############################################################################
# END OF DRAWING CLASSES - TO BE CLEANED UP                                  #
##############################################################################

class xRectBluePrint():
    # Create a virtual rectangle by specifying Center point, height, width and depth
    # Create and draw a rect object in 3D space
    # Move back and forwards on the Z plane

    def __init__(self, RectCenterPointX, RectCenterPointY, RectWidth, RectHeight, RectDepth, xColour):
        # our virtual rectangle should just have : Center point x, Center point y, top left x, top left y, bottom right h, bottom right w), z value

        self.xCenterPointX = RectCenterPointX
        self.xCenterPointY = RectCenterPointY
        self.xRectWidth = RectWidth
        self.xRectHeight = RectHeight
        self.xDepthZ = RectDepth
        self.xBurnDown = [True, 1, 1, 1]
        self.xShadow = False
        self.xShape = "rect"
 
        self.CalcDescriptors()
        self.xColour = xColour  # over ride on init    

    def CalcDescriptors(self):
        # CALC CORNERS
        self.xTopLeftX = self.xCenterPointX - self.xRectWidth/2
        self.xTopLeftY = self.xCenterPointY - self.xRectHeight/2
        self.xBottomRightX = self.xCenterPointX + self.xRectWidth/2
        self.xBottomRightY = self.xCenterPointY + self.xRectHeight/2
        # CREATE THE LOGICAL RECTANGLE
        self.xLogicalRect =pygame.Rect(self.xTopLeftX, self.xTopLeftY, self.xRectWidth, self.xRectHeight)
        # SET / RESET THE COLOUR
            # Set a random colour.  We can look at cycling them later.  These would need to be set outside of the class
            # to use some colour logic that spans across the rectangles. 
        self.xColour = (randrange(100,200), randrange(150,250), randrange(50,250))
        self.xBirthColour = self.xColour

    def TransformRect(self, Camera):

        self.Camera = Camera
        # Transform the four co-ordinates to 3D.
    
        # Convert the 3D coordinates to 2D using perspective projection.
        # this should be a single function, or should transform a 3d point, I think
        k = K_NUMERATOR / self.xDepthZ # Depth modifier.  256 is in relation to total depth.

        x1 = int((self.xTopLeftX - self.Camera.x) * k + ORIGINX)
        y1 = int((self.xTopLeftY - self.Camera.y) * k + ORIGINY)

        x2 = int((self.xBottomRightX - self.Camera.x) * k + ORIGINX)
        y2 = int((self.xBottomRightY - self.Camera.y) * k + ORIGINY)

        xwidth = x2 - x1
        xheight = y2 - y1

        # Then create the rect object
        self.xRect = pygame.Rect(x1, y1, xwidth, xheight)
      
    def DrawRect(self, xsurface):        
        if self.xBurnDown[0] is True :
            self.xColour = (int(self.xColour[0] * self.xBurnDown[1]),
                            int(self.xColour[1] * self.xBurnDown[2]),
                            int(self.xColour[2] * self.xBurnDown[3]))
        elif self.xShadow is True :
            self.xColour = (255, 255, 255)
        else: self.xColour = self.xBirthColour


        if self.xShape == "rect" :
            pygame.draw.rect(xsurface, self.xColour, self.xRect, 1)
        elif self.xShape == "ellipse" :
            # check for overflow 2^16 in draw ellipse
            if self.xRect.width >= 65536 or self.xRect.height >= 65536:
                self.xDepthZ = 0 # this will cause the rectangle to be recycled next time around
            else:
                xScreenRect = xsurface.get_rect()
                xClippedRect = self.xRect.clip(xScreenRect)
        
                if xClippedRect.width > 0 and xClippedRect.height > 0:
                    # Create a subsurface for drawing the clipped part of the ellipse
                    xSubSurface = xsurface.subsurface(xClippedRect)
        
                    # Offset the ellipse so it aligns correctly within the clipped rect
                    xOffsetEllipseRect = self.xRect.move(-xClippedRect.left, -xClippedRect.top)

                    pygame.draw.ellipse(xSubSurface, self.xColour, xOffsetEllipseRect, 1)
                        
    
    def ChangeZ(self, xMoveZ):
        # Method to change the depth (Z value) by the amount specified in xMove Z
        self.xDepthZ += xMoveZ
    
    def ResetRect(self, RectCenterPointX, RectCenterPointY, ResetDepth, ResetWidth, ResetHeight, ResetShape):
        self.xDepthZ = ResetDepth # this happens regardless
        self.xCenterPointX = RectCenterPointX
        self.xCenterPointY = RectCenterPointY
        self.xRectWidth = ResetWidth
        self.xRectHeight = ResetHeight
        self.xShape = ResetShape
        self.xBurnDown[0] = False
        self.CalcDescriptors()
    
    def Crash(self):
        self.xBurnDown = [True, .99, .95, .93]
        self.xColour = (255, 255, 255)
        

class vector():
    def __init__(self, vx , vy, vz):
        self.vx = vx
        self.vy = vy
        self.vz = vz

class player():
    def __init__(self, x, y, z, VelocityFactor, Friction, CircleSize, HasObject, Object):
        self.HasObject = HasObject
        self.Object = Object
        self.x = x
        self.y = y
        self.z = z
        self.VelocityFactor = VelocityFactor
        self.CircleSize = CircleSize
        self.vector = vector(0, 0, 0)  # not moving
        self.friction = Friction
        
    def draw(self, xgamescreen):
        pygame.draw.circle(xgamescreen, (200,150,200), (int(round(self.x,0)),int(round(self.y,0))), self.CircleSize, 5)
        
    def ChangeX(self, amount):
        self.x += amount
        
    def ChangeY(self, amount):
        self.y += amount

    def ChangeZ(self, amount):
        self.z += amount
        
    def MoveByVector(self): # THIS USES ABSOLUTE FRICTION, NOT PERCENTAGE.
        # X:  calculate direction, apply friction to the vector        
        if abs(self.vector.vx) <= self.friction / 10 : # inefficient, will always fire for zeroes.
             self.vector.vx = 0
        else:
            self.vector.vx = self.vector.vx * ((1 - self.friction)) # * FrictionDirection)

        self.ChangeX(self.vector.vx)              # apply vector to position

        # Y:  calculate direction, apply friction to the vector        
        if abs(self.vector.vy) <= self.friction : # inefficient, will always fire for zeroes.
            self.vector.vy = 0
        else:
            self.vector.vy = self.vector.vy * ((1 - self.friction) ) #* FrictionDirection)
            
        self.ChangeY(self.vector.vy)              # apply vector to position
        #self.vector.vy *= boundary
        
        if self.HasObject == True:
            # Then process the object accordingly
            # MoveObject(self, ChangeX, ChangeY, ChangeZ)
            self.Object.MoveObject(self.vector.vx, self.vector.vy, 0)

class dummyobject():
    pass

class Tunnel3D():  # THIS SHOULD BE MORE GENERIC, MORE OF A 'GAMEPLAY' CLASS, MAYBE.
    def __init__(self, xGamescreen, xFrameRate, xZoomBar): # xQuitButton, 
        self.xGamescreen = xGamescreen
        self.init_tunnel() # initiate the tunnels
#        self.xQuitButton  = xQuitButton
        self.xZoomBar  = xZoomBar

        # translucent up/down arrows for the zoom bar (mobile only)
        self.xZoomArrows = pygame.Surface((xZoomBar.width, SCREENHEIGHT), pygame.SRCALPHA)  # see-through layer
        xArrowColour = (80, 80, 80, 140)      # grey, last number = opacity (0 invisible - 255 solid)
        xMid = xZoomBar.width // 2            # centre of the bar
        xHalf = xZoomBar.width // 6           # half the arrow size
        xUpY = SCREENHEIGHT // 5              # 20% of the way down
        xDownY = SCREENHEIGHT * 4 // 5        # 80% of the way down
        pygame.draw.polygon(self.xZoomArrows, xArrowColour,
                            [(xMid, xUpY - xHalf), (xMid - xHalf, xUpY + xHalf), (xMid + xHalf, xUpY + xHalf)])
        pygame.draw.polygon(self.xZoomArrows, xArrowColour,
                            [(xMid, xDownY + xHalf), (xMid - xHalf, xDownY - xHalf), (xMid + xHalf, xDownY - xHalf)])
        
        # Player: x, y, z, VelocityFactor, Friction, CircleSize):
        self.dummyobject = dummyobject() # 974
        self.Camera1 = player(0, 0, 0, 1, .974, 50, False, self.dummyobject) # camera is slower, greater velocity factor reduction
        self.xCraft = FloatingObject(850)
        self.Player1 = player(0, 0, 0, 1, .015, 10, True, self.xCraft) # create the player; create the Velocity Factor
        self.ModelVector = vector(0, 0, 0)
        self.xScore = 0
        self.xScoreFalling = False
        self.xFontScore = pygame.font.Font("PressStart2P-Regular.ttf",24)
        self.xFontFrameRate = pygame.font.Font("PressStart2P-Regular.ttf", 18)
        if ISMOBILE:
            self.xFontInstructions = pygame.font.Font("VT323-Regular.ttf", 45)
        else:
            self.xFontInstructions = pygame.font.Font("VT323-Regular.ttf", 30)
        self.xFrameRate = xFrameRate

        # self.xScoreSurface = pygame.Surface(80,20)
 
    def init_tunnel(self): # initiate the tunnel sections

        DefaultRectCenterPointX = 0
        DefaultRectCenterPointY = 0
        self.RectWidth = DEFAULT_RECT_WIDTH
        self.RectHeight = DEFAULT_RECT_HEIGHT
        self.RectDepth = 8192  # This will be the max depth
        self.RectCount = 256 # this is how many rectangles
        self.xShape = "rect"
        self.r= 0.5
        
        RectSpacing = self.RectDepth/self.RectCount # this is the gap between rectangles
        
        # Tunnel path variables, x/y/z vectors
        self.xCurrentVector = (0, 0, 24)
        self.xTargetVector = (0, 0, 10)
        self.xGravity = (0, 0, 10)
        self.xLastX = 0 # to apply the vector to
        self.xLastY = 0 # to apply the vector to

        self.TunnelObjectList = list()
        for i in range(self.RectCount): # start count at 0 
            # Calculate the depth, starting at the max depth and then working backwards
            DepthToSet = self.RectDepth + i * RectSpacing # First instance should modify by zero
        
            Colour = (int(self.r), int(30 + self.r), int(30+ self.r))
            self.xNewBluePrint = xRectBluePrint(DefaultRectCenterPointX, DefaultRectCenterPointY, self.RectWidth, self.RectHeight, DepthToSet, Colour)
            self.TunnelObjectList.append(self.xNewBluePrint)
            self.r += 0.5
            
    # Dampens the scale of movement to maximum / minimum values
    def Damper(self, Damper, Move):
        if Move > Damper: Move = Damper
        elif Move > Damper *0.2: pass
        elif Move > 0: Move = Damper *.1
        elif Move > -Damper *-0.1: Move = Damper *-.1
        elif Move > Damper *-0.8: pass
        else: Move = -Damper
        return Move

    def Calculate_Path(self):

        # Recycle.  First, work out if we are changing direction
        ChangeDirection = randrange(1,151) # do we change direction at all
        if ChangeDirection >= 100: # yes
            ChangeDirection2 = randrange(1,6) # 33% chance we'll go flat
            if ChangeDirection2 == 5:
                self.xTargetVector = (0, 0, 10) # flat but forward
            else:
                self.xTargetVector = (randrange(SCREENWIDTH * -4,  SCREENWIDTH * 4),
                                      randrange(SCREENHEIGHT  * -4, int(SCREENHEIGHT * 3.9)), 10) # this is the target direction of travel
        # so now we have our direction; could be unchanged, could be new.
  
        # Create the gravitational pull
        gravityX = (self.xTargetVector[0] - self.xCurrentVector[0])
        gravityY = (self.xTargetVector[1] - self.xCurrentVector[1])

        # Damping within thresholds
        xDamper = 0.6
        gravityX = self.Damper(xDamper,gravityX)
        gravityY = self.Damper(xDamper,gravityY)
        

        # Then apply the gravity to the current vector
        self.xCurrentVector = ((self.xCurrentVector[0] + gravityX), (self.xCurrentVector[1] + gravityY), 
                               (self.xCurrentVector[2]))

    def ShowScore(self):

        font = self.xFontScore
        if self.xScoreFalling:
            tmpColour = (150, 0, 0)
        else:
            tmpColour = (100, 200, 100)
        text = font.render(str(int(self.xScore)), True, tmpColour)
        self.xGamescreen.blit(text,(SCREENWIDTH - 150, 10))

    def ShowInstructions(self):
        font = self.xFontInstructions
        tmpColour = (255,255,255)
        if ISMOBILE:
            xInstructions = "SPACE TUNNEL 3D\r\n\r\nstay in the tunnel 'til nirvana at 10,000\r\n\r\ndrag anywhere to move\r\ndrag up/down in the bar on the right:\r\n  up - forward\r\n  down - backward\r\nreload the page to restart\r\n\r\ntips:\r\nlook for white rectangle for current depth of craft\r\nmove forward to give yourself more time to react\r\n\r\ngo for a fly outside the tunnel\r\nfor a different perspective.\r\nwill deplete your score\r\nzoom forwards and watch the tunnel burn"
        else:
            xInstructions = "SPACE TUNNEL 3D\r\n\r\nstay in the tunnel 'til nirvana at 10,000\r\n\r\nmaximize browser window\r\nIf FPS much less than 50,\r\ntry using private browsing modes\r\n\r\nmouse, trackpad or arrow keys to move\r\nA-forward\r\nZ-backward\r\nR-restart\r\nESC-resume mouse control\r\n\r\ntips:\r\nlook for white rectangle for current depth of craft\r\nuse A to move forward to give yourself more time to react\r\n\r\ngo for a fly outside the tunnel\r\nfor a different perspective.\r\nwill deplete your score\r\nzoom forwards and watch the tunnel burn"
        for i, xLine in enumerate(xInstructions.splitlines()):
            text = font.render(xLine, True, tmpColour)
            self.xGamescreen.blit(text, (25, 100 + i * font.get_linesize()))

#    def ShowFrameRate(self):
#        font = self.xFontFrameRate
#        tmpColour = (140,140,140)
#        text = font.render("speed (+/- to change): " + str(self.xFrameRate), True, tmpColour)
#        self.xGamescreen.blit(text, (920, 10))


    def Move_Tunnel(self):
        """ Move and draw all rectangles """
        
        # HANDLE MODEL MOVEMENT
        
        # Move the player
        if self.ModelVector.vx != 0 :
            self.Player1.vector.vx = (self.ModelVector.vx * self.Player1.VelocityFactor) - self.Player1.vector.vx # adjust player vector by diff between mod and plyr
            self.ModelVector.vx *= .985                             #  reset to 0.  Only gets applied once.
        
        if self.ModelVector.vy != 0 :
            self.Player1.vector.vy = (self.ModelVector.vy * self.Player1.VelocityFactor) - self.Player1.vector.vy # adjust player vector by diff between mod and plyr
            self.ModelVector.vy *= .975                                        # reset to 0.  Only gets applied once.           

       # then ask the player to move by it's current vector amount (call it's move method), and draw it.
        self.Player1.MoveByVector() # !!! this should move the object !!!!
     
        # Move the camera
        # work out if there's a difference, x then y.
        
        self.Camera1.vector.vx = self.Player1.x - self.Camera1.x # this is all done on absolutes.
        self.Camera1.vector.vy = self.Player1.y - self.Camera1.y # this is all done on absolutes.

        self.Camera1.MoveByVector()
        
    # FULL SCREEN CONTROLS
        
        if ISMOBILE:
            pygame.draw.rect(self.xGamescreen, (20, 20, 20), self.xZoomBar, 0)
            self.xGamescreen.blit(self.xZoomArrows, (self.xZoomBar.left, 0))
#        pygame.draw.rect(self.xGamescreen, (50, 20, 20), self.xQuitButton, 0)

        # HANDLE OBJECT MOVEMENT

        for ListRect in reversed(self.TunnelObjectList):
            
        # This is where we move the rectangle back and change direction.
            if ListRect.xDepthZ <= self.xCurrentVector[2]: 
                # RECYCLE THE RECTANGLE                

                self.Calculate_Path()                                    # First calculate any changes to the vector
                                                                         # Then recycle the rectangle with new x, y and z : 
                ListRect.ResetRect(self.xLastX + self.xCurrentVector[0],   # apply x vector to last position
                                   self.xLastY + self.xCurrentVector[1],   # apply y vector to last position
                                   self.RectDepth - ListRect.xDepthZ,      # ensures a precise Z in case parameters misaligned
                                   self.RectWidth,
                                   self.RectHeight,
                                   self.xShape)
                self.xLastX = ListRect.xCenterPointX                     # then capture the current values for the next round
                self.xLastY = ListRect.xCenterPointY
                self.xLastShape = ListRect.xShape

            else: # MOVE THE RECTANGLE
                xModifier = 0 #(10 / ListRect.xDepthZ) * 1 # so starts as a very small number, and ends up at 1.  Times 2.
                ListRect.ChangeZ(self.xCurrentVector[2] *-1 + xModifier)
                
                # 
                # Check shadow zone 
                if (ListRect.xDepthZ <= self.xCraft.xMagicHexagon.xCentreZ +50 and
                             ListRect.xDepthZ >= self.xCraft.xMagicHexagon.xCentreZ - 50) :
                    ListRect.xShadow = True
                    
                    # check crash zone
                    if (ListRect.xDepthZ <= self.xCraft.xMagicHexagon.xCentreZ +12 and
                             ListRect.xDepthZ >= self.xCraft.xMagicHexagon.xCentreZ - 12) :
                        # check if crashed    
                        if not ListRect.xLogicalRect.collidepoint(self.xCraft.xMagicHexagon.xCentreX, self.xCraft.xMagicHexagon.xCentreY):
                            ListRect.Crash()
                            ListRect.xShadow = False
                            self.xScore -=1.2
                            self.xScoreFalling = True
                            if self.xScore < 0 : self.xScore = 0
                        else : 
                            self.xScore += 1.5  #.4
                            self.xScoreFalling = False
                else : ListRect.xShadow = False

            ListRect.TransformRect(self.Camera1) 
            ListRect.DrawRect(self.xGamescreen)

        self.xCraft.DrawObject(self.xGamescreen, self.Camera1)

    # Draw text
        self.ShowScore()
#        self.ShowFrameRate()        
        if self.xScore < 500:
            self.ShowInstructions()

        if self.xScore <= 1000 :
            pass
        elif self.xScore <= 2000 :
            self.RectHeight = DEFAULT_RECT_HEIGHT * 0.8
        elif self.xScore <= 3000 :
            self.RectWidth = DEFAULT_RECT_WIDTH * 0.5
            self.RectHeight = DEFAULT_RECT_HEIGHT
        elif self.xScore <= 3500 :
            self.RectHeight = DEFAULT_RECT_HEIGHT * 0.5
        elif self.xScore <= 4500 :
            self.RectWidth = DEFAULT_RECT_HEIGHT
            self.RectHeight = DEFAULT_RECT_HEIGHT
            self.xShape = "ellipse"
        elif self.xScore <= 5000 :
            self.RectHeight = DEFAULT_RECT_HEIGHT * 0.8
        elif self.xScore <= 6000 :
            self.RectHeight = DEFAULT_RECT_HEIGHT * 0.6
        elif self.xScore <= 6800 :
            self.RectHeight = DEFAULT_RECT_HEIGHT * 0.4
        elif self.xScore <= 7600 :
            self.RectWidth = DEFAULT_RECT_HEIGHT * 0.8
        elif self.xScore <= 8300 :
            self.RectWidth = DEFAULT_RECT_HEIGHT * 0.6
        elif self.xScore <= 9100 :
            self.RectWidth = DEFAULT_RECT_HEIGHT * 0.4
        elif self.xScore <= 9999 :
            self.RectWidth = DEFAULT_RECT_HEIGHT * 0.3
            self.RectHeight = DEFAULT_RECT_HEIGHT * 0.9

        else :
            if randrange(1,201) >= 197 :
                xmod1 = randrange(20,41) / 100
                xmod2 = randrange(20,41) / 100
            else :
                xmod1 = 1
                xmod2 = 1
            self.RectWidth = DEFAULT_RECT_HEIGHT *6 * xmod1
            self.RectHeight = DEFAULT_RECT_HEIGHT *6 * xmod2
        

# class ScoreBox() :
    

class engine():
    # init
    def __init__(self):  
 
        pygame.init()
#        flags = pygame.FULLSCREEN | pygame.SCALED
#        self.vDesktops = pygame.display.get_desktop_sizes()
#        self.screenWidth = self.vDesktops[0][0]    
#        self.screenHeight = self.vDesktops[0][1]    
#        self.xGamescreen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, pygame.SCALED)
#        self.xGamescreen = pygame.display.set_mode((0, 0))
        self.xGamescreen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.SCALED)
    
        # Enable for trackpad
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        pygame.display.set_caption("Space Tunnel")
        self.xClock = pygame.time.Clock()
        
        # create a zoom bar on the left, only used on mobile.
        self.xZoomBar = pygame.Rect(SCREENWIDTH - 140, 0, 140, SCREENHEIGHT - 0)

#        self.xQuitButton = pygame.Rect(0, 0, 70, 70)
        
        # Create the tunnel
        self.xMoveAmount = .4 # distance to move per key press.
        self.xFrameRate = 60 # Max frame rate. User control currently commented out.
        self.xMoveAmount2 = 10
        self.xAccelerate = 0
        self.xMouseScaler = .2
#        self.xTunnel = Tunnel3D(self.xGamescreen, self.xQuitButton, self.xZoomBar, self.xFrameRate)
        self.xTunnel = Tunnel3D(self.xGamescreen, self.xFrameRate, self.xZoomBar)

    # restart
    def restart(self):
#        self.xTunnel = Tunnel3D(self.xGamescreen, self.xQuitButton, self.xZoomBar, self.xFrameRate)
        self.xTunnel = Tunnel3D(self.xGamescreen, self.xFrameRate, self.xZoomBar)

    # event loop
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.restart()
                return
            elif event.type == KEYDOWN:
                if event.key ==  K_r:
                    self.restart()
                    
#                if event.key in (K_EQUALS, K_KP_PLUS):
#                    if self.xFrameRate < 180 :
#                        self.xFrameRate += 20
#                        self.xTunnel.xFrameRate = self.xFrameRate
#                if event.key in (K_MINUS, K_KP_MINUS):                    
#                    if self.xFrameRate > 60 :
#                        self.xFrameRate -= 20
#                        self.xTunnel.xFrameRate = self.xFrameRate
                        
                if event.key == K_ESCAPE:
                    pygame.event.set_grab(False)
                    pygame.mouse.set_visible(True)
                        
            if event.type == pygame.MOUSEMOTION:
                xMouseMovementX, xMouseMovementY = pygame.mouse.get_rel()
                xMouseX, xMouseY = pygame.mouse.get_pos()

                if ISMOBILE and self.xZoomBar.collidepoint(xMouseX, xMouseY):                    
                    xRequestedZoom  = xMouseMovementY*-4
                    if xRequestedZoom > 0 or self.xTunnel.xCraft.xMagicHexagon.xCentreZ + xRequestedZoom > 60:
                        self.xTunnel.xCraft.MoveObject(0, 0, xRequestedZoom)
                else:
                    self.xTunnel.ModelVector.vx += xMouseMovementX * self.xMouseScaler
                    self.xTunnel.ModelVector.vy += xMouseMovementY * self.xMouseScaler

# Any mouse click will return the mouse                            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.event.set_grab(False)
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)

# Touchscreen only
#            if ISMOBILE:
#               if self.xZoomBar.collidepoint(xMouseX, xMouseY):                    
#                   self.xTunnel.xCraft.MoveObject(0, 0, xMouseMovementY*-4)
#                else:
#            if event.type == pygame.MOUSEBUTTONDOWN:
#                if self.xQuitButton.collidepoint(event.pos):
#                    self.restart()



        keys=pygame.key.get_pressed()
        if keys[K_q]: self.xAccelerate += .05
        else: self.xAccelerate = 1

        if keys[K_LEFT]: self.xTunnel.ModelVector.vx -= self.xMoveAmount * self.xAccelerate
        if keys[K_RIGHT]: self.xTunnel.ModelVector.vx += self.xMoveAmount * self.xAccelerate
        if keys[K_DOWN]: self.xTunnel.ModelVector.vy += self.xMoveAmount * self.xAccelerate
        if keys[K_UP]: self.xTunnel.ModelVector.vy -= self.xMoveAmount * self.xAccelerate

        # THIS IS A CHEAT
        if keys[K_a]: self.xTunnel.xCraft.MoveObject(0, 0, self.xMoveAmount2)
        if keys[K_z]: 
            if self.xTunnel.xCraft.xMagicHexagon.xCentreZ > 60 : 
                self.xTunnel.xCraft.MoveObject(0, 0, -self.xMoveAmount2)



    # run game
    async def main_loop(self):
        
        while 1:
            self.xClock.tick(self.xFrameRate)
            self.event_loop()
            # clear the screen
            self.xGamescreen.fill((0,0,0))

            # move all of the rectangles.  Will need to be a loop.
            self.xTunnel.Move_Tunnel()

            # show the actual frame rate (diagnostic)
            xFps = self.xTunnel.xFontFrameRate.render(str(int(self.xClock.get_fps())) + " fps", True, (140,140,140))
            self.xGamescreen.blit(xFps, ((SCREENWIDTH // 2) - 10, 10))

            # Update the display the screen
            pygame.display.flip()
            await(asyncio.sleep(0))
#            wait (3)

def startup():
    # prepare environment, create screen, start the program, quit
    # move some stuff down here later, maybe.
    asyncio.run(engine().main_loop())
    # pygame.quit()
    

if __name__ == "__main__":
    startup()
