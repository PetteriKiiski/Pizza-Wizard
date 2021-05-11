import pygame, sys, time
from pygame.locals import *

#TO - DO List:
#Key: Person - Task

#1. Petteri - Fix paddle problem(wizard can't jump on left side of paddle)
#2.
#3.

pygame.init()
winWidth = 1200
winHeight = 600
canvas = pygame.display.set_mode((1200, 600))
clock = pygame.time.Clock()

#--- Paddle Class ---
class Paddle:
	def __init__(self, bound1, bound2, y, width, height, speed):
		self.bound1 = bound1
		self.bound2 = bound2
		self.speed = abs(speed)
		self.rect = pygame.Rect(bound1, y, width, height)
		self.direction = 'right'
	def move(self):
		if self.rect.right > self.bound2:
			self.direction = 'left'

		if self.rect.left < self.bound1:
			self.direction = 'right'

		self.rect.left += self.speed if self.direction == 'right' else -self.speed
	def display(self, canvas):
		pygame.draw.rect(canvas, (0, 255, 0), self.rect)

#--- Bullet Class ---
class Bullet:

	#Math variables for where to shoot bullets (where the wizard is)
	def __init__(self, imgs, x, y, width, height, target_x, target_y, speed, strength):
		self.rect = pygame.Rect(x, y, width, height)
		self.strength = strength
		orig_1 = 7
		orig_2 = speed + orig_1
		try:
			slope = (abs(self.rect.top - target_y) / abs(self.rect.left - target_x))
		except ZeroDivisionError:
			slope = None
		if slope is not None:
			y1 = slope * orig_1 + self.rect.top
			y2 = slope * orig_2 + self.rect.top
		self.dif_y = y1 - y2
		if y < target_y:
			self.dif_y = abs(self.dif_y)
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

#--- Monster Class ---
class Monster:
	def __init__(self, bullet_speed, bullet_height, bullet_imgs, imgsRight, imgsLeft, x, y, width, height, direction, speed, bullet_strength, health=1, jumps=False):
		self.bullet_speed = bullet_speed
		self.jumpcount = 10
		self.jumps = jumps
		self.health = health
		self.index = 0
		self.bullet_height = bullet_height
		self.healthImg = pygame.image.load("Bar{}.png".format(self.health))
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
	def lose_health(self):
		self.health -= 1
		if self.health > 0:
			self.healthImg = pygame.image.load("Bar{}.png".format(self.health))
	def display(self, wizard):
		if self.rect.left < winWidth and self.rect.right > 0:
			self.SeenWizard = True
			canvas.blit(self.imgs[self.index], self.rect)

		canvas.blit(self.healthImg, (self.rect.left-25, self.rect.top - 60))

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
			if self.rect.bottom < 500:
				self.rect.bottom += 4
			self.jump()
	def jump(self):
		if not self.jumps:
			return
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

	def fly(self):pass

	def shoot_bullet(self, wizard):
		bullet_shot.play()
		if self.direction == 'left':
			point1 = (self.rect.left, self.rect.bottom)
		else:
			point1 = (self.rect.right, self.rect.bottom)
		point2 = (wizard.rect.centerx, wizard.rect.bottom - 50)
		bullets.append(Bullet(self.bullet_imgs, point1[0], point1[1], 80, self.bullet_height, point2[0], point2[1], self.bullet_speed, self.bullet_strength))

#--- Wizard Class ---
class Wizard:
	def __init__(self):
		self.health = 10
		self.healthImg = pygame.image.load("Bar{}.png".format(self.health))
		self.rect = pygame.Rect(150, 307, 138, 193)
		self.spells = []
		self.spell_timer = time.time()
		self.timer = time.time()
		self.speed = 12
		self.Dead = False

		#List of picture animations
		self.imagesFront = [pygame.image.load("WizardFront.png"), pygame.image.load("WizardFront.png")]
		self.imagesRight = [pygame.image.load("WizardRight1.png"), pygame.image.load("WizardRight2.png")]
		self.imagesLeft = [pygame.image.load("WizardLeft1.png"), pygame.image.load("WizardLeft2.png")]
		self.imagesDead = [pygame.image.load("WizardDead.png"), pygame.image.load("WizardDead.png")]
		self.index = 0
		self.images = self.imagesFront
		self.atboarder = False
		self.jumping = False
		self.jumpcount = 10
	def can_shoot_magic(self):
		if time.time() - self.spell_timer >= 3:
			return True
		return False
	def shoot_magic(self, targetx, targety):
		if not self.can_shoot_magic():
			return
		lazer.play()
		self.spell_timer = time.time()
		if self.move() == 'left':
			point1 = (self.rect.left, self.rect.top)
		else:
			point1 = (self.rect.right, self.rect.top)
		point2 = (targetx, targety)
		magics.append(Bullet(['Magic1.png', 'Magic1.png'], point1[0], point1[1], 100, 20, point2[0], point2[1], 15, 1))

	def lose_health(self):
		self.health -= 1
		if self.health > 0:
			self.healthImg = pygame.image.load("Bar{}.png".format(self.health))
			return
		self.healthImg = pygame.image.load("HealthBar.png")
		self.images = self.imagesDead
		self.Dead = True
		magics = []

	#Parabola Jump
	def jump(self):
		if self.jumpcount >= -10:
			neg = 1
			if self.jumpcount < 0:
				neg = -1
			self.rect.bottom -= int((self.jumpcount**2) * 0.5 * neg)
			self.jumpcount -= 1
			if self.rect.bottom >= 500:
				self.jumping = False
				self.jumpcount = 10
				self.rect.bottom = 500
		else:
			if self.rect.bottom < 500:
				self.jumpcount = -9

			else:
				self.jumping = False
				self.jumpcount = 10

	#Displays wizard, and changes images every 0.3 seconds
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

	#Changes animation images
	def turn(self, direction):
		if not self.Dead:
			if direction == 'right':
				self.images = self.imagesRight
			if direction == 'left':
				self.images = self.imagesLeft
			if direction == 'front':
				self.images = self.imagesFront


	#Moves/ Jumps wizard
	def move(self):
		print (self.jumpcount)
		if self.jumping:
			self.jump()
		for i, paddle in enumerate(paddles):
			print ('identity:' + str(i))
			#<rect(150, 207, 138, 193)> #self.rect
			#<rect(251, 400, 200, 30)> #paddle.rect
			if self.rect.bottom >= paddle.rect.top \
				and self.rect.bottom <= paddle.rect.bottom \
				and ((self.rect.left >= paddle.rect.left \
				and self.rect.left <= paddle.rect.right) \
				or (self.rect.right >= paddle.rect.left \
				and self.rect.right <= paddle.rect.right) and self.jumpcount <= 0):
				print ('on paddle')
				self.jumpcount = 10
				print (self.jumpcount)
				self.jumping = False
				self.rect.bottom = paddle.rect.top
				break
			elif self.rect.bottom != 500 and not self.jumping:
				print ('start goin down!!!')
				print (self.rect)
				print (paddle.rect)
				self.jumpcount = -1
				self.jumping = True

		if self.Dead:
			return
		if self.images == self.imagesFront:
			return
		if self.images == self.imagesRight:
			return 'right'
		if self.images == self.imagesLeft:
			return 'left'

class Container:
	def __init__(self):
		pass

#this funcion will parse a file and play the level
def fileparser(filename):

#initializes a bunch of lists and variables needed from beginning to end in this function
	global bullets, magics, current_time, paddles
	monsters = []
	bullets = []
	magics = []
	paddles = []
	breakout = False
	boss = None
	pygame.display.set_caption("Pizza Wizard")
	canvas.fill((255, 255, 255))
	Renderable = pygame.font.SysFont(None, 48)
	DisplayText = Renderable.render('Ingredient 1 : water', True, (0, 0, 0))
	bg = pygame.image.load("Level1BG.png")
	grass = pygame.image.load("Grass.png")
	ogreRight = pygame.image.load("Monster3Right.png")
	ogreLeft = pygame.image.load("Monster3Left.png")
	rottingRight = pygame.image.load("Monster2Right.png")
	rottingLeft = pygame.image.load("Monster2Left.png")
	skatingRight = pygame.image.load("Monster1Right.png")
	skatingLeft = pygame.image.load("Monster1Left.png")
	bdragonRight = pygame.image.load("Monster4Right.png")
	bdragonLeft = pygame.image.load("Monster4Left.png")
	spiralRight = pygame.image.load("Monster6Right.png")
	spiralLeft = pygame.image.load("Monster6Left.png")
	furryRight = pygame.image.load("Monster5Right.png")
	furryLeft = pygame.image.load("Monster5Left.png")
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
				bg = pygame.image.load("Level4BG.png")
				DisplayText = Renderable.render('Ingredient 2 : flour', True, (0, 0, 0))
			if co[1] == '3':
				bg = pygame.image.load("Level3BG.png")
				DisplayText = Renderable.render('Ingredient 3 : ?????', True, (0, 0, 0))
			if co[1] == '4':
				bg = pygame.image.load("Level4BG.png")
				DisplayText = Renderable.render('Ingredient 4 : ?????', True, (0, 0, 0))
		if co[0] == 'length':
			maxdistance = int(co[1])
		if co[0] == 'ogre':
			monsters += [Monster(15, 30, ['Bullet2Right.png', 'Bullet2Left.png'], [ogreRight, ogreRight], [ogreLeft, ogreLeft], int(co[1][0]), int(co[1][1]), 115, 145, 'left', 4, 1)]
		if co[0] == 'rotting':
			monsters += [Monster(15, 30, ['Bullet2Right.png', 'Bullet2Left.png'], [rottingRight, rottingRight], [rottingLeft, rottingLeft], int(co[1][0]), int(co[1][1]), 133, 144, 'left', 6, 1, 2)]
		if co[0] == 'skating':
			monsters += [Monster(15, 40, ['Bullet1Right.png', 'Bullet1Left.png'], [skatingRight, skatingRight], [skatingLeft, skatingLeft], int(co[1][0]), int(co[1][1]), 147, 145, 'left', 8, 2, 3)]
		if co[0] == 'broken-dragon':
			monsters += [Monster(15, 40, ['Bullet1Right.png', 'Bullet1Left.png'], [bdragonRight, bdragonRight], [bdragonLeft, bdragonLeft], int(co[1][0]), int(co[1][1]), 129, 179, 'left', 10, 2, health=3, jumps = True)]
		if co[0] == 'paddle':
			paddles += [Paddle(int(co[1][0]), int(co[1][1]), int(co[2]), int(co[3]), int(co[4]), int(co[5]))]
		if co[0] == 'boss':
			if co[1] == 'furry':
				boss = Monster(15, 40, ['Bullet1Right.png', 'Bullet1Left.png'], [furryRight, furryRight], [furryLeft, furryLeft], int(co[2][0]), int(co[2][1]), 119, 282, 'left', 4, 5, 5)
			if co[1] == 'spiral-eyes':
				boss = Monster(15, 40, ['Bullet1Right.png', 'Bullet1Left.png'], [spiralRight, spiralRight], [spiralLeft, spiralLeft], int(co[2][0]), int(co[2][1]), 266, 283, 'left', 1, 3, 5)
#bullet_speed, bullet_height, bullet_imgs, imgsRight, imgsLeft, x, y, width, height, direction, speed, bullet_strength, health=1
	wizard = Wizard()
	dirchanged = False #direction changed
	Dying = False
	started_dying = time.time()

	#While statement that runs and displays game, and ticks clock
	while True:
		clock.tick(50)
		if time.time() - current_time >= 160:
			current_time = time.time()
			pygame.mixer.music.stop()
			pygame.mixer.music.play()
		canvas.fill((255, 255, 255))
		canvas.blit(bg, (bgx, 0))

		#Moving background
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

		for i, paddle in enumerate(paddles):
			paddle.move()
			paddle.display(canvas)

		for monster in monsters + [boss]:
			if breakout and boss:
				continue
			monster.move(wizard)
			monster.display(wizard)

		canvas.blit(grass, (0, 500))

		for bullet in bullets[:] + magics[:]:
			bullet.update()
			if (bullet.rect.right <= 0 or bullet.rect.left >= winWidth) and bullet.hasBeenInMain:
				try:
					del bullets[bullets.index(bullet)]
				except:pass
				try:
					del magics[magics.index(bullet)]
				except:pass
				continue
			bullet.move()
			bullet.display(canvas)
		canvas.blit(DisplayText, (canvas.get_rect().centerx - 150, canvas.get_rect().top))
		if breakout:
			pygame.display.update()
			break

		#Keyboard handling
		for event in pygame.event.get():

			#Quits
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

			#Reloop the music
			if event.type == 1000:
				pygame.mixer.music.rewind()

			#Turns wizard
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
				if event.type == MOUSEBUTTONDOWN:
					pos = pygame.mouse.get_pos()
					wizard.shoot_magic(*pos)

				#Stops turning wizard
				if event.type == KEYUP:
					if event.key in [K_LEFT, K_RIGHT]:
						dirchanged = False
		if not dirchanged:
			wizard.turn('front')

		#Moves backround or wizard (depending on location)
		if wizard.move() == 'left' and not wizard.Dead:
			if bgx != 0 and wizard.rect.left == 150:
				bgx += wizard.speed
				for monster in monsters + bullets + magics + paddles +[boss]:
					monster.rect.right += wizard.speed
				for paddle in paddles:
					paddle.bound1 += wizard.speed
					paddle.bound2 += wizard.speed
			elif distance != 1 and wizard.rect.left == 150:
				bgx += wizard.speed
				for monster in monsters + bullets + magics + paddles + [boss]:
					monster.rect.right += wizard.speed
				for paddle in paddles:
					paddle.bound1 += wizard.speed
					paddle.bound2 += wizard.speed
			else:
				if wizard.rect.left > 150:
					wizard.rect.right -= wizard.speed
				else:
					if wizard.rect.left > 0:
						wizard.rect.right -= wizard.speed
		if wizard.move() == 'right' and not wizard.Dead:
			if bgx != 0 and wizard.rect.left == 150:
				bgx -= wizard.speed
				for monster in monsters + bullets + magics + paddles + [boss]:
					monster.rect.left -= wizard.speed
				for paddle in paddles:
					paddle.bound1 -= wizard.speed
					paddle.bound2 -= wizard.speed
			elif distance != maxdistance and wizard.rect.left == 150:
				bgx -= wizard.speed
				for monster in monsters + bullets + magics + paddles + [boss]:
					monster.rect.left -= wizard.speed
				for paddle in paddles:
					paddle.bound1 -= wizard.speed
					paddle.bound2 -= wizard.speed
			else:
				if wizard.rect.left < 150:
					wizard.rect.right += wizard.speed
				else:
					if wizard.rect.right < winWidth:
						wizard.rect.right += wizard.speed

		for bullet in bullets[:]:
			for paddle in paddles:
				if bullet.rect.colliderect(paddle.rect):
					del bullets[bullets.index(bullet)]

		#Wizard loses health if hit
		for attacker in monsters + bullets[:] + [boss]:
			if attacker.rect.colliderect(wizard.rect) and not Dying:
				started_dying = time.time()
				wizard.lose_health()
				Dying = True
				if isinstance(attacker, Bullet):
					for i in range(1, attacker.strength):
						wizard.lose_health()
					del bullets[bullets.index(attacker)]
				break
		for monster in monsters[:] + [boss]:
			if breakout:
				break
			for magic in magics[:]:
				if monster.rect.colliderect(magic.rect):
					monster.lose_health()
					if monster.health == 0:
						if monster == boss:
							print ('you win')
							breakout = True
						else:
							del monsters[monsters.index(monster)]
					del magics[magics.index(magic)]
					if breakout:
						break


		if Dying and time.time() - started_dying > 1:
			Dying = False
		if wizard.Dead:
			magics = []

		pygame.display.update()

def endloop():
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
		pygame.display.update()
#parses and runs the fileparser function on every single level
bullet_shot = pygame.mixer.Sound("bullet_shot.wav")
lazer = pygame.mixer.Sound("lazer.wav")
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.play()
current_time = time.time()
fileparser("water")
time.sleep(3)
fileparser("level2")
time.sleep(3)
fileparser("level3")
time.sleep(3)
fileparser("level4")
endloop()
