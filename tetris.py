import pygame
from time import sleep
from random import randint

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



class Coordinator:
    def __init__(self, height, width, sqInRow, sqInCol):#height, width of a square, number of squares in a row, col
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

    def setUnders(self):
        for i in self.sqs:
            for j in i:
                j.setUnderMe(self.sqs)

    def checkEvents(self):
        running = True
        events = pygame.event.get()
        for event in events:  # check keyboard actions
            if event.type == pygame.QUIT:  # close the game
                running = False
                print('Closed')
                break
            elif event.type == pygame.KEYDOWN:
                pass
        return running


    def main(self):
        running = True
        while running:
            running = self.checkEvents()


c = Coordinator(600, 600, 10, 10)
c.createSqs()
c.setUnders()
c.main()

#1