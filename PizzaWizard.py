import pygame, sys, time
from pygame.locals import *

#This class will be a parsing exception
class ParseError:
	def __init__(self):
		print ('cannot parse file')

winWidth = 1200
winHeight = 600
canvas = pygame.display.set_mode((1200, 600))
clock = pygame.time.Clock()
#class for the bullets that the monsters launch
class Bullet:
	#Initializer function needs some mathematical variables to be able to point to the wizard
	def __init__(self, imgs, x, y, width, height, target_x, target_y, speed, strength):
		self.rect = pygame.Rect(x, y, width, height)
		self.strength = strength
		orig_1 = 7 #Just some number for testing
		orig_2 = speed + orig_1
		try:
			slope = (abs(self.rect.top - target_y) / abs(self.rect.left - target_x))
		except ZeroDivisionError:
			slope = None
		if slope is not None:
			y1 = slope * orig_1 + self.rect.top
			y2 = slope * orig_2 + self.rect.top
		self.dif_y = y1 - y2
		self.dif_x = speed if self.rect.right < target_x else -speed
		self.img = pygame.image.load(imgs[1] if self.dif_x < 0 else imgs[0])
		self.hasBeenInMain = False
	def update(self):
		if self.rect.right > 0 and self.rect.left < winWidth:
			self.hasBeenInMain = True
	def move(self):
		self.rect.right += self.dif_x
		self.rect.top += self.dif_y
	def display(self, canvas):
		canvas.blit(self.img, self.rect)

#class for all the monsters
class Monster:
	def __init__(self, bullet_height, bullet_imgs, imgsRight, imgsLeft, x, y, width, height, direction, speed, bullet_strength):
		self.index = 0
		self.bullet_height = bullet_height
		self.bullet_imgs = bullet_imgs
		self.shoot = time.time()
		self.rect = pygame.Rect(x, y, width, height)
		self.imgsRight = imgsRight
		self.imgsLeft = imgsLeft
		self.imgs = self.imgsRight if direction == 'right' else self.imgsLeft
		self.SeenWizard = False
		self.direction = direction
		self.timer = time.time()
		self.speed = speed
		self.bullet_strength = bullet_strength

	def display(self, wizard):
		if self.rect.left < winWidth and self.rect.right > 0:
			self.SeenWizard = True
			canvas.blit(self.imgs[self.index], self.rect)

		if self.rect.left > 0 and self.rect.right < winWidth:
			if time.time() - self.timer >= 0.3:
				self.timer = time.time()
				if self.index:
					self.index = 0
				else:
					self.index = 1
		if time.time() - self.shoot > 3 and self.SeenWizard:
			self.shoot = time.time()
			if not wizard.Dead:
				self.shoot_bullet(wizard)
	def move(self, wizard):
		if self.SeenWizard:
			if self.rect.right <= wizard.rect.left:
				self.direction = 'right'
				self.rect.right += self.speed
				self.imgs = self.imgsRight
			if self.rect.left >= wizard.rect.right:
				self.direction = 'left'
				self.rect.right -= self.speed
				self.imgs = self.imgsLeft
	def jump(self):pass

	def fly(self):pass

	def shoot_bullet(self, wizard):
		if self.direction == 'left':
			point1 = (self.rect.left, self.rect.top)
		else:
			point1 = (self.rect.right, self.rect.top)
		point2 = (wizard.rect.centerx, wizard.rect.top)
		bullets.append(Bullet(self.bullet_imgs, point1[0], point1[1], 80, self.bullet_height, point2[0], point2[1], 15, self.bullet_strength))
class Wizard:
	def __init__(self):
		self.health = 10
		self.healthImg = pygame.image.load("Bar{}.png".format(self.health))
		self.rect = pygame.Rect(150, 307, 138, 193)
		self.spells = []
		self.timer = time.time()
		self.speed = 12
		self.Dead = False

#creates lists of two picture animations of the wizard and other variables for the animation to work
		self.imagesFront = [pygame.image.load("WizardFront.png"), pygame.image.load("WizardFront.png")]
		self.imagesRight = [pygame.image.load("WizardRight1.png"), pygame.image.load("WizardRight2.png")]
		self.imagesLeft = [pygame.image.load("WizardLeft1.png"), pygame.image.load("WizardLeft2.png")]
		self.imagesDead = [pygame.image.load("WizardDead.png"), pygame.image.load("WizardDead.png")]
		self.index = 0
		self.images = self.imagesFront
		self.atboarder = False
		self.jumping = False
		self.jumpcount = 10

#This function jumps in a parabola
	def lose_health(self):
		self.health -= 1
		if self.health > 0:
			self.healthImg = pygame.image.load("Bar{}.png".format(self.health))
			return
		self.healthImg = pygame.image.load("HealthBar.png")
		self.images = self.imagesDead
		self.Dead = True
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

#displays the wizard, and changes the image every three tenth of a second
	def display(self):
		canvas.blit(self.images[self.index], self.rect)
		if self.rect.left-25 >= 0:
			if self.rect.left+163 <= winWidth:
				canvas.blit(self.healthImg, (self.rect.left-25, self.rect.top - 60))
			else:
				canvas.blit(self.healthImg, (1009, self.rect.top - 60))
		else:
			canvas.blit(self.healthImg, (0, self.rect.top - 60))
		if self.rect.left > 0 and self.rect.right < winWidth and not self.jumping:
			if time.time() - self.timer >= 0.3:
				self.timer = time.time()
				if self.index:
					self.index = 0
				else:
					self.index = 1

#This function changes the animation images
	def turn(self, direction):
		if not self.Dead:
			if direction == 'right':
				self.images = self.imagesRight
			if direction == 'left':
				self.images = self.imagesLeft
			if direction == 'front':
				self.images = self.imagesFront

	def move(self):
		'''
		This section will move the wizard if he is supposed to jump
		or return the value he is supposed to move
		since he is acutally just in one position
		'''
		if self.jumping:
			self.parabela()
		if self.Dead:
			return
		if self.images == self.imagesFront:
			return
		if self.images == self.imagesRight:
			return 'right'
		if self.images == self.imagesLeft:
			return 'left'

#this funcion will parse a file and play the level
def fileparser(filename):

#initializes a bunch of lists and variables needed from beginning to end in this function
	global bullets
	monsters = []
	bullets = []
	pygame.display.set_caption("Pizza Wizard")
	canvas.fill((255, 255, 255))
	bg = pygame.image.load("Level1BG.png")
	grass = pygame.image.load("Grass.png")
	ogreRight = pygame.image.load("Monster3Right.png")
	ogreLeft = pygame.image.load("Monster3Left.png")
	rottingRight = pygame.image.load("Monster2Right.png")
	rottingLeft = pygame.image.load("Monster2Left.png")
	skatingRight = pygame.image.load("Monster1Right.png")
	skatingLeft = pygame.image.load("Monster1Left.png")
	bgx = 0
	maxdistance = 2
	distance = 1

#takes all of the information from the file with the 'with' statement
	try:
		with open(filename, 'rt') as fh:
			text = fh.read()
	except:
		print ('Coordinate file cannot be read. Terminating')
		sys.exit(1)

#parses the information we got from the previous section
	coordinates = text.split('\n')
	del coordinates[-1]
	newco = []
	for coordinate in coordinates[:]:
		newco.append(coordinate.rstrip())
	coordinates = newco[:]
	separated_coordinates = []
	for coordinate in coordinates:
		separated_coordinates.append(coordinate.split(':'))
	coordinates = separated_coordinates[:]
	newco = []
	for coordinate in coordinates[:]:
		newco += [[]]
		for co in coordinate:
			newco[-1].append(co.split(',') if len(co.split(',')) > 1 else co)
	coordinates = newco[:]

#uses the parsed data into sprites and also creates the wizard
	for co in coordinates:
		if co[0] == 'level':
			if co[1] == '1':
				continue
			if co[1] == '2':
				bg = pygame.image.load("Level2BG.png")
			if co[1] == '3':
				bg = pygame.image.load("Level3BG.png")
			if co[1] == '4':
				bg = pygame.image.load("Level4BG.png")
		if co[0] == 'length':
			maxdistance = int(co[1])
		if co[0] == 'ogre':
			monsters += [Monster(30, ['Bullet2Right.png', 'Bullet2Left.png'], [ogreRight, ogreRight], [ogreLeft, ogreLeft], int(co[1][0]), int(co[1][1]), 115, 145, co[2], 4, 1)]
		if co[0] == 'rotting':
			monsters += [Monster(30, ['Bullet2Right.png', 'Bullet2Left.png'], [rottingRight, rottingRight], [rottingLeft, rottingLeft], int(co[1][0]), int(co[1][1]), 133, 144, co[2], 6, 1)]
		if co[0] == 'skating':
			monsters += [Monster(40, ['Bullet1Right.png', 'Bullet1Left.png'], [skatingRight, skatingRight], [skatingLeft, skatingLeft], int(co[1][0]), int(co[1][1]), 147, 145, co[2], 8, 2)]
#imgsRight, imgsLeft, x, y, width, height, direction, speed

	wizard = Wizard()
	dirchanged = False #direction changed

	'''
	This section contains the while statement for the mainloop
	and ticks our little baby clock we defined at the top
	 and displays everything
	'''
	Dying = False
	started_dying = time.time()

	while True:
		clock.tick(50)
		canvas.fill((255, 255, 255))
		canvas.blit(bg, (bgx, 0))
#This function makes it an infinity background until it reaches the end or the beginning
		if bgx < 0:
			canvas.blit(bg, (bgx + winWidth, 0))
		if bgx > 0:
			if distance != 1:
				canvas.blit(bg, (bgx - winWidth, 0))
		if bgx in [winWidth, -winWidth]:
			if bgx == winWidth:
				distance -= 1
			if bgx == -winWidth:
				distance += 1
			bgx = 0
		wizard.display()
		for monster in monsters:
			monster.move(wizard)
			monster.display(wizard)
		canvas.blit(grass, (0, 500))
		for bullet in bullets[:]:
			bullet.update()
			if (bullet.rect.right <= 0 or bullet.rect.left >= winWidth) and bullet.hasBeenInMain:
				del bullets[bullets.index(bullet)]
				continue
			bullet.move()
			bullet.display(canvas)
#keyboard event handling
		for event in pygame.event.get():

#quits if needed
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

#turns the wizard if its not dead
			if not wizard.Dead:
				if event.type == KEYDOWN:
					if event.key == K_LEFT:
						wizard.turn('left')
						dirchanged = True

					if event.key == K_RIGHT:
						wizard.turn('right')
						dirchanged = True

					if event.key == K_SPACE:
						wizard.jumping = True

					if event.key == K_RCTRL or event.key == K_LCTRL:
						pass

#stops turning the wizard if the a key has been lifted
				if event.type == KEYUP:
					if event.key in [K_LEFT, K_RIGHT]:
						dirchanged = False
		if not dirchanged:
			wizard.turn('front')
#Moves the background or the wizard, whichever is needed
		if wizard.move() == 'left' and not wizard.Dead:
			if bgx != 0 and wizard.rect.left == 150:
				bgx += wizard.speed
				for monster in monsters:
					monster.rect.right += wizard.speed
				for bullet in bullets:
					bullet.rect.right += wizard.speed
			elif distance != 1 and wizard.rect.left == 150:
				bgx += wizard.speed
				for monster in monsters:
					monster.rect.right += wizard.speed
				for bullet in bullets:
					bullet.rect.right += wizard.speed
			else:
				if wizard.rect.left > 150:
					wizard.rect.right -= wizard.speed
				else:
					if wizard.rect.left > 0:
						wizard.rect.right -= wizard.speed
		if wizard.move() == 'right' and not wizard.Dead:
			if bgx != 0 and wizard.rect.left == 150:
				bgx -= wizard.speed
				for monster in monsters:
					monster.rect.left -= wizard.speed
				for bullet in bullets:
					bullet.rect.right -= wizard.speed
			elif distance != maxdistance and wizard.rect.left == 150:
				bgx -= wizard.speed
				for monster in monsters:
					monster.rect.left -= wizard.speed
				for bullet in bullets:
					bullet.rect.right -= wizard.speed
			else:
				if wizard.rect.left < 150:
					wizard.rect.right += wizard.speed
				else:
					if wizard.rect.right < winWidth:
						wizard.rect.right += wizard.speed
#If the wizard hits a monster, it loses health
		for attacker in monsters + bullets[:]:
			if attacker.rect.colliderect(wizard.rect) and not Dying:
				started_dying = time.time()
				wizard.lose_health()
				Dying = True
				if isinstance(attacker, Bullet):
					for i in range(1, attacker.strength):
						wizard.lose_health()
					del bullets[bullets.index(attacker)]
				break
		if Dying and time.time() - started_dying > 1:
			Dying = False
		pygame.display.update()

#parses and runs the fileparser function on every single level
fileparser("water")
