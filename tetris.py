import pygame
from time import sleep
from random import choice

class Square:
    def __init__(self, x, y, height, width, canvas):
        #coords in sqList
        self.x = x
        self.y = y
        #coords on the GUI
        self.guiX = x * width
        self.guiY = y * height
        #sq sizes
        self.h = height
        self.w = width
        #main canvas
        self.canvas = canvas
        #square under the colorized one, a little bit bigger->outline
        outlineColor = (255, 255, 255)
        self.outlinePic = pygame.draw.rect(self.canvas, outlineColor, [self.guiX, self.guiY, self.w, self.h])
        #size difference between colorized and outline square-> outline width
        self.olw = 1
        #draw basic state
        self.inactivate()
        #container shape
        self.shape = None

    def setUnderMe(self, sqList): #find the square under this one
        if self.y == len(sqList) - 1:#on the bottom of the field
            self.underMe = 'iambottom'
        else:
            self.underMe = sqList[self.y + 1][self.x]

    def getUnderMe(self):#return lower neighbor
        return self.underMe

    def getCoords(self):#return coords in the list of squares
        return self.x, self.y

    def getState(self):#active or inactive
        return self.state

    def getShape(self):
        return self.shape

    def activate(self, color, shape):
        self.color = color
        self.draw(self.color)
        self.state = 'active'  #colorful ->  something is on it, not empty
        self.shape = shape

    def inactivate(self):
        self.color = (0, 0, 0)#black
        self.draw(self.color)
        self.state = 'inactive'  #black  ->  empty square
        self.shape = None

    def draw(self, color):
        self.pic = pygame.draw.rect(self.canvas, color, [self.guiX + self.olw, self.guiY + self.olw, self.w - 2 * self.olw, self.h - 2 * self.olw])

class Shape:
    def __init__(self, sqList, startX, startY):
        self.sqList = sqList
        self.startX, self.startY = startX, startY
        self.validSpawnBool = True
        self.chooseShape()
        self.chooseColor()
        self.drawMyBody()

    def validSpawn(self):
        return self.validSpawnBool


    def chooseShape(self): #choose random shape and set body first time
        #In this list every sublist is a shape. The coordinates in the tuples represents the loacation of the piece,
        #counted from the (0, 0) point->this is the middle of the shape.
        shapes = [
                  [(0, 0), (1, 0)],
                  [(0, 0), (1, 0), (0, 1)],
                  [(0, 0), (1, 0), (-1, 0), (-1, 1)],
                  [(0, 0), (1, 0), (-1, 0), (1, 1)],
                  [(0, 0), (1, 0), (-1, 0), (2, 0)],
                  [(0, 0), (1, 0), (0, 1), (1, 1)],
                  [(0, 0), (1, 0), (-1, 0), (0, 1)]
                  ]
        self.shape = choice(shapes)
        body = []
        for i in self.shape:
            body.append(self.sqList[self.startY + i[1]][self.startX + i[0]])
        for i in body:
            if i.getState() == 'active':
                self.validSpawnBool = False
        self.body = body
        self.middle = body[0]


    def chooseColor(self): #color of the shape, random, not changing over time.
        self.color = choice([(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 0)])

    def drawMyBody(self):
        for i in self.body:
            i.activate(self.color, self)
        pygame.display.update()

    def eraseMyBody(self):
        for i in self.body:
            i.inactivate()
        pygame.display.update()

    def moveDownPart(self, part): #move down 1 square from the shape by 1 unit
        x, y = part.getCoords()
        #inactivate previous position
        self.delPart(part)
        #activate current position
        self.body.append(self.sqList[y + 1][x])
        self.sqList[y + 1][x].activate(self.color, self)

    def delPart(self, part):
        self.body.remove(part)
        part.inactivate()

    def getBodySize(self):
        return len(self.body)

    def fall(self):  #go down by 1 square
        newBody = []  #list of squares in the shape after falling
        stopped = False
        for i in self.body:
            #look every element, if one can't fall more, then the whole object will stop
            if i.getUnderMe() == 'iambottom':
                stopped = True
            elif i.getUnderMe().getState() == 'active' and not(i.getUnderMe() in self.body):
                stopped = True
            else:
                newBody.append(i.getUnderMe())

        #reset GUI and main variables
        if not stopped:
            self.eraseMyBody()
            self.body = newBody
            if len(self.body) > 0:
                self.middle = newBody[0]
            self.drawMyBody()

        return stopped

    def rotate(self):
        mx, my = self.middle.getCoords()#coords of the middle of the shape
        newBody = []
        canRot = True#able to rotate the object
        for i in self.body:
            x, y = i.getCoords()#coords of current item
            rx, ry = x - mx, y - my#relative coords of middle and current item to each other. Changing this will rotate the object
            newRx, newRy = ry*-1, rx#location of the rotated piece(the middle point is the origo)
            newGlobalX, newGlobalY = newRx + mx, newRy + my
            #check new block's location
            #if on the edge(collision with field edge)
            if newGlobalX >= len(self.sqList[0]) or newGlobalX < 0 or newGlobalY >= len(self.sqList) or newGlobalY < 0:
                canRot = False
                break
            #collision with another object
            elif self.sqList[newGlobalY][newGlobalX].getState() == 'active' and not self.sqList[newGlobalY][newGlobalX] in self.body:
                canRot = False
                break
            else:
                newBody.append(self.sqList[newGlobalY][newGlobalX])
        if canRot:
            # reset main variables
            self.eraseMyBody()
            self.body = newBody
            if len(self.body) > 0:
                self.middle = newBody[0]
            self.drawMyBody()



    def goLeft(self):
        canGo = True
        for i in self.body:
            x, y = i.getCoords()
            #if on the very left side
            if x == 0:
                canGo = False
                break
            #if collides with another object
            elif self.sqList[y][x - 1].getState() == 'active' and not self.sqList[y][x - 1] in self.body:
                canGo = False
                break
        if canGo:
            #calculate new positions
            newBody = []
            for i in self.body:
                x, y = i.getCoords()
                newBody.append(self.sqList[y][x - 1])
            #reset main variables
            self.eraseMyBody()
            self.body = newBody
            if len(self.body) > 0:
                self.middle = newBody[0]
            self.drawMyBody()


    def goRight(self):
        canGo = True
        for i in self.body:
            x, y = i.getCoords()
            # if on the very right side
            if x == len(self.sqList[0]) - 1:
                canGo = False
                break
            # if collides with another object
            elif self.sqList[y][((x + 1) % len(self.sqList[0]))].getState() == 'active' and not self.sqList[y][x + 1] in self.body:
                canGo = False
                break
        if canGo:
            # calculate new positions
            newBody = []
            for i in self.body:
                x, y = i.getCoords()
                newBody.append(self.sqList[y][x + 1])
            # reset main variables
            self.eraseMyBody()
            self.body = newBody
            if len(self.body) > 0:
                self.middle = newBody[0]
            self.drawMyBody()

    def pullDown(self):
        stopped = False
        while not stopped:
            stopped = self.fall()

class Coordinator:
    def __init__(self, width, height, sqInRow, sqInCol):#height, width of a square, number of squares in a row, col
        #field size
        self.h = height
        self.w = width
        self.inr = sqInRow
        self.inc = sqInCol

        #set canvas
        self.canvas = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Tetris')
        self.canvas.fill((0, 0, 0))

    def createSqs(self):
        sqs = []
        for i in range(self.inc):
            sqrow = []
            for j in range(self.inr):
                sqrow.append(Square(j, i, self.h / self.inc, self.w / self.inr, self.canvas))
            sqs.append(sqrow)
        self.sqs = sqs
        pygame.display.update()

    def setUnders(self):#set the lower neighbors for all squares. Important because of the 'Coordinator.fall' function
        for i in self.sqs:
            for j in i:
                j.setUnderMe(self.sqs)

    def delOneLine(self, lineNumber):
        #deactivate line
        for i in self.sqs[lineNumber]:
            shape = i.getShape()
            shape.delPart(i)
        #pull down every line above the deleted one by 1 block
        for i in range(lineNumber - 1, -1, -1):  #if for example lineNumber = 5, i = 4, 3, 2, 1, 0.
            for j in self.sqs[i]:
                shape = j.getShape()
                if shape != None:
                    shape.moveDownPart(j)

    def findLineToDel(self):
        lineNumber = 0
        for i in self.sqs:
            deletable = True
            for j in i:
                if j.getState() == 'inactive':
                    deletable = False
            if deletable:
                return lineNumber#number of the deletable line
            else:
                lineNumber += 1
        return False#no deletable lines

    def delLine(self):
        while True:
            deletable = self.findLineToDel()
            if deletable == False:
                break
            else:
                self.delOneLine(deletable)
        pygame.display.update()

    def checkEvents(self):
        todo = None
        events = pygame.event.get()
        for event in events:  # check keyboard actions
            if event.type == pygame.QUIT:  # close the game
                return 'closed'
                break
            elif event.type == pygame.KEYDOWN: #move left-right, rotate, push down
                if event.key == pygame.K_LEFT:
                    todo = 'left'
                if event.key == pygame.K_RIGHT:
                    todo = 'right'
                if event.key == pygame.K_UP:
                    todo = 'rotate'
                if event.key == pygame.K_DOWN:
                    todo = 'pullDown'
        return todo


    def main(self):
        #field setup
        self.createSqs()
        self.setUnders()
        # game loop
        running = True
        delay = 1#secundums between 2 'falls'
        accurate = 10#number of the checks on events per delay period
        self.existingShapes = []
        while running:
            # shape creation
            s = Shape(self.sqs, int(self.inr / 2), 0)
            self.existingShapes.append(s)
            #check if new shape spawned on the top of another, if yes, game over
            if s.validSpawn() == False:
                running = False
                print('Field is filled with shapes. Game over')
                break
            #fall while it's possible, recieve and execute user commands
            stopped = False
            while not stopped and running:
                for i in range(accurate):
                    # slowdown
                    sleep(delay / accurate)
                    # pulls the command from user
                    todo = self.checkEvents()
                    #execute user commands
                    if todo == 'closed':
                        print('Game is closed')
                        running = False
                        break
                    elif todo == 'left':
                        s.goLeft()
                    elif todo == 'right':
                        s.goRight()
                    elif todo == 'rotate':
                        s.rotate()
                    elif todo == 'pullDown':
                        s.pullDown()
                        stopped = True




                stopped = s.fall()

            self.delLine()


c = Coordinator(300, 600, 5, 10)
c.main()