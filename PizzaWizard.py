import pygame, sys, time
from pygame.locals import *

class Wizard:
	def __init__(self, canvas):
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This section creates some variables that will be required for the functioning of this class
		self.canvas = canvas
		self.health = 10
		self.rect = pygame.Rect(150, 307, 150, 200)
		self.spells = []
		self.timer = time.time()
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This section creates lists of two picture animations of the wizard and other variables for the animation to work
		self.imagesFront = [pygame.image.load("WizardFront.png"), pygame.image.load("WizardFront.png")]
		#For simplicity, in the list above, We just used the same image twice, so that we don't need to complicate things
		self.imagesRight = [pygame.image.load("WizardRight1.png"), pygame.image.load("WizardRight2.png")]
		self.imagesLeft = [pygame.image.load("WizardLeft1.png"), pygame.image.load("WizardLeft2.png")]
		self.index = 0
		self.images = self.imagesLeft
		self.atboarder = False
		self.jumping = False
		self.jumpcount = 10
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This function jumps in a parabela
	def parabela(self):
		if self.jumpcount >= -10:
			neg = 1
			if self.jumpcount < 0:
				neg = -1
			self.rect.bottom -= int((self.jumpcount**2) * 0.5 * neg)
			self.jumpcount -= 1
		else:
			if self.rect.bottom > 1090 and self.rect.bottom < 1110:
				self.jumpcount = 0
			else:
				self.jumping = False
				self.jumpcount = 10
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This section displays the wizard, and changes the image every three tenth of a second
	def display(self):
		self.canvas.blit(self.images[self.index], self.rect)
		if self.rect.left > 0:
			if time.time() - self.timer >= 0.3:
				self.timer = time.time()
				if self.index:
					self.index = 0
				else:
					self.index = 1
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This function changes the animation images
	def turn(self, direction):
		if direction == 'right':
			self.images = self.imagesRight
		if direction == 'left':
			self.images = self.imagesLeft
		if direction == 'front':
			self.images = self.imagesFront
#-----------------------------------------------------------------------------------------------------------------------------------------------------
	def move(self):
		'''
		This section will move the wizard if he is supposed to jump
		or return the value he is supposed to move
		since he is acutally just in one position
		'''
		if self.jumping:
			self.parabela()
		if self.images == self.imagesFront:
			return
		if self.images == self.imagesRight:
			return 'right'
		if self.images == self.imagesLeft:
			return 'left'
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This funcion will parse a file and play the level
def fileparser(filename):
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This section initializes a bunch of lists and variables needed from beginning to end in this function
	spells = []
	monster2s = []
	monster1s = []
	canvas = pygame.display.set_mode((1200, 600))
	pygame.display.set_caption("Pizza Wizard")
	canvas.fill((255, 255, 255))
	bg = pygame.image.load("Level1BG.png")
	grass = pygame.image.load("Grass.png")
	bgx = 0
	maxdistance = 2
	distance = 1
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This section takes all of the information from the file with the 'with' statement
	try:
		with open(filename, 'rt') as fh:
			text = fh.read()
	except:
		print ('Coordinate file cannot be read. Terminating')
		sys.exit(1)
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This part parses the information we got from the previous section
	coordinates = text.split('\n')
	del coordinates[-1]
	separated_coordinates = []
	for coordinate in coordinates:
		separated_coordinates.append(coordinate.split(':'))
	coordinates = separated_coordinates[:]
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This section uses the parsed data into sprites and also creates the wizard
	for co in coordinates:
		if co[0] == 'level':
			if co[1] == '1':
				print ('1')
				continue
			if co[1] == '2':
				print ('2')
				bg = pygame.image.load("Level2BG.png")
			if co[1] == '3':
				print ('3')
				bg = pygame.image.load("Level3BG.png")
			if co[1] == '4':
				print ('4')
				bg = pygame.image.load("Level4BG.png")
	wizard = Wizard(canvas)
	dirchanged = False
	clock = pygame.time.Clock()
#-----------------------------------------------------------------------------------------------------------------------------------------------------
	'''This section contains the while statement for the mainloop
	ticks our little clock we defined three lines up
	(if you count the comment) and displays everything'''
	while True:
		clock.tick(50)
		canvas.fill((255, 255, 255))
		canvas.blit(bg, (bgx, 0))
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This function makes it an infinity background until it reaches the end or the beginning
		if bgx < 0:
			canvas.blit(bg, (bgx + 1200, 0))
		if bgx > 0:
			if distance != 1:
				canvas.blit(bg, (bgx - 1200, 0))
		if bgx in [1200, -1200]:
			if bgx == 1200:
				distance -= 1
			if bgx == -1200:
				distance += 1
			bgx = 0
		wizard.display()
		canvas.blit(grass, (0, 500))
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This section does all the keyboard event handling
		for event in pygame.event.get():
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This section quits if needed
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This section turns the wizard
			if event.type == KEYDOWN:
				if event.key == K_LEFT:
					wizard.turn('left')
					dirchanged = True
				if event.key == K_RIGHT:
					wizard.turn('right')
					dirchanged = True
				if event.key == K_SPACE:
					wizard.jumping = True
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This section stops turning the wizard if the a key has been lifted
			if event.type == KEYUP:
				if event.key in [K_LEFT, K_RIGHT]:
					dirchanged = False
#-----------------------------------------------------------------------------------------------------------------------------------------------------
		if not dirchanged:
			wizard.turn('front')
		if wizard.move() == 'left':
			if bgx != 0:
				bgx += 12
			elif distance != 1:
				bgx += 12
			else:
				if wizard.rect.left > 0:
					wizard.rect.right -= 12
				else:
					wizard.move()
		if wizard.move() == 'right':
			if bgx != 0:
				bgx -= 12
			elif distance != maxdistance:
				bgx -= 12
			else:
				if wizard.rect.left < 150:
					wizard.rect.right += 12
				else:
					if wizard.rect.right < 1200:
						wizard.rect.right += 12
		pygame.display.update()
		print (distance)
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This section parses and runs the fileparser function on every single level
fileparser("water")
#-----------------------------------------------------------------------------------------------------------------------------------------------------
