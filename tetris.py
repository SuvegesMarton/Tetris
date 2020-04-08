import pygame
from time import sleep
from random import randint, choice

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

    def activate(self, color):
        self.color = color
        self.draw(self.color)
        self.state = 'active'  #colorful ->  something is on it, not empty

    def inactivate(self):
        self.color = (0, 0, 0)#black
        self.draw(self.color)
        self.state = 'inactive'  #black  ->  empty square

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
                  [(0, 0), (-1, 0), (0, 1)],
                  [(0, 0), (1, 0), (2, 0), (0, 1)],
                  [(0, 0), (-1, 0), (-2, 0), (0, 1)],
                  [(0, 0), (1, 0), (-1, 0), (2, 0)],
                  [(0, 0), (1, 0), (0, 1), (1, 1)]
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
            i.activate(self.color)
        pygame.display.update()

    def eraseMyBody(self):
        for i in self.body:
            i.inactivate()
        pygame.display.update()

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
            self.middle = newBody[0]
            self.drawMyBody()

        return stopped

    def rotate(self):
        mx, my = self.middle.getCoords()#coords of the middle of the shape
        for i in self.body:
            x, y = i.getCoords()#coords of current item
            rx, ry = x - mx, y - my#relative coords of middle and current item to each other. Changing this will rotate the object
            nx, ny = ry, rx*-1#location of the rotated piece(the middle point is the origo)

class Coordinator:
    def __init__(self, height, width, sqInRow, sqInCol):#height, width of a square, number of squares in a row, col
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

    def delLine(self):
        pass

    def checkEvents(self):
        todo = None
        events = pygame.event.get()
        for event in events:  # check keyboard actions
            if event.type == pygame.QUIT:  # close the game
                print('Closed')
                return 'closed'
                break
            elif event.type == pygame.KEYDOWN: #move left-right, rotate, push down
                if event.key == pygame.K_LEFT:
                    self.movement = 'left'
                if event.key == pygame.K_RIGHT:
                    self.movement = 'true'
        return todo


    def main(self):
        #field setup
        self.createSqs()
        self.setUnders()
        # game loop
        running = True
        delay = 1#secundums between 2 'falls'
        accurate = 5#number of the checks on events per delay period
        while running:
            # shape creation
            s = Shape(self.sqs, 4, 0)
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
                        print('recieved')
                        running = False
                        break




                stopped = s.fall()

            self.delLine()


c = Coordinator(600, 600, 10, 10)
c.main()