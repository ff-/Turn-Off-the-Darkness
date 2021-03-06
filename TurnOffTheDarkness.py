#!/usr/bin/python
from imports import *

from player import *
from wall import *
from sounds import *
from effects import *
from menus import *
from slide import *
from background import *

class Game(pygame.sprite.Sprite):
	def __init__(self):
		# se funziona si tiene
		pygame.sprite.Sprite.__init__(self)
		#
		
		self.quit = False
		
		pygame.init()
		
		self.clock = pygame.time.Clock()
		self.max_fps = 120
		self.tick = 0
		self.speed = 10*UNIT  # per second
		self.frenzy = 1
		self.soundAction = False
		self.lightAction = False
		self.countActionPerBpm = 0
		self.pastActionsPerBpm = 0
		self.death = False
		self.lives = 3
		self.lightTimer = 0
		self.soundTimer = 0
		self.levelCompletion = 0
		self.points = 0
		self.paused = True
		self.slideCount = 1
		
		# se usati insieme permettono di muovere il mouse infinitamente
		# ma bloccano la tastiera "all'esterno"
		pygame.mouse.set_visible(False)
		#pygame.event.set_grab(True)
		
		# game.state_varible
		pygame.time.set_timer(USEREVENT, int(60*1000/BPM))
		self.beat = False
		self.sounds = Sounds(self)
		
		self.left = False
		self.right = False
		#
		
		
		self.image = pygame.display.set_mode(
			#(800,600),DOUBLEBUF
			(1366,768),DOUBLEBUF|FULLSCREEN|HWSURFACE
		)
		self.rect = self.image.get_rect()
		pygame.display.set_caption('GGJ')
		
		self.effects = pygame.sprite.Group()
		self.foreground = pygame.sprite.Group()
		self.menusGroup = pygame.sprite.OrderedUpdates()
		self.slideGroup = pygame.sprite.Group()
		
		self.background = Background(self)
		
		self.slide = Slide(self)
		self.slideGroup.add(self.slide)
		
		self.player = Player(self)
		self.foreground.add(self.player)
		
		self.walls = Walls(self)
		
		self.lifebar = LifeBar(self)
		self.pointWrite = Points(self)
		self.keysBar = KeysBar(self)
		self.bar = Bar(self)
		self.frenzyNegBar = FrenzyNegBar(self)

		self.menusGroup.add(self.bar)
		self.menusGroup.add(self.lifebar)
		self.menusGroup.add(self.pointWrite)
		self.menusGroup.add(self.frenzyNegBar)
		self.menusGroup.add(self.keysBar)


		self.light = Light(self)
		self.effects.add(self.light)
		
		self.black = Black(self)
		self.effects.add(self.black)

		self.radar = Radar(self)
		self.effects.add(self.radar)
		

		#self.test_wall = Wall(self)
		#self.foreground.add(self.test_wall)
		
		
	def run(self):
		while not self.quit:
			self.events()
			self.update()
			self.draw()
			self.tick = float(self.clock.tick(self.max_fps))/1000
		pygame.quit()
	
	def events(self):
		for event in pygame.event.get():
			if event.type==QUIT:
				self.quit = True
			elif event.type == KEYDOWN:
				if self.paused and self.slideCount > 2:
					self.paused = False
				elif self.paused and self.slideCount < 2:
					self.slideCount +=1
				elif self.paused and self.slideCount == 2:
					self.slideCount +=1
					self.paused = False
					self.player.image = self.player.images[0]

				if event.key == K_ESCAPE:
					self.quit = True
				if event.key == K_LEFT:
					self.left = True
				if event.key == K_RIGHT:
					self.right = True
				if event.key == K_z:
					self.soundAction = True
					self.countActionPerBpm += 1
				if event.key == K_x:
					self.lightAction = True
					self.countActionPerBpm += 1
				
				if event.key == K_s:
					pygame.image.save(self.image,"screenshot.jpg")
				
			elif event.type == KEYUP:
				if event.key == K_LEFT:
					self.left = False
				if event.key == K_RIGHT:
					self.right = False
			
			if event.type==USEREVENT:
				self.beat = True
			
		
		self.mouse_rel = pygame.mouse.get_rel()
	
	def update(self):
		if self.beat:
			#there is the frenzy
			self.pastActionsPerBpm = self.countActionPerBpm
			if self.countActionPerBpm > 2 and self.frenzy < 10:
				self.frenzy += 1
			elif self.countActionPerBpm < 1 and self.pastActionsPerBpm < 1 and self.frenzy > 1:
				self.frenzy -= 1

			#events: light&sound
			if self.lightAction:
				self.lightTimer = 2 #parameters
			if self.soundAction:
				self.soundTimer = 2
				

			self.countActionPerBpm = 0

			if not self.paused:
				self.speed = 10 * UNIT * math.log(math.log(self.points +1) +1)# era 10
		
		if self.soundTimer > 0:
			self.background.black = True
		else:
			self.background.black = False
		
		if self.beat:
			if self.lightTimer > 0:
				self.lightTimer -= 1
			if self.soundTimer > 0:  
				self.soundTimer -= 1

		self.background.update()
		if not self.paused:
			self.sounds.update()
			self.effects.update()
			self.walls.update()
		self.foreground.update()
		self.menusGroup.update()
		self.slideGroup.update()

		if self.beat and not self.paused:
			self.lightAction = False
			self.soundAction = False
			
			# punteggio
			if (self.frenzy <= F_CALM):
				self.points += random.randint(10,20)
			elif (self.frenzy <= F_TRANS2):
				self.points += random.randint(100,200)
			else:
				self.points += random.randint(1000,2000)
		#print "Punteggio: %s" %self.points

		if self.death:
			self.lives -= 1
			self.reset()
			self.paused = True

		if self.paused:
			self.speed = 0
			self.player.image = self.player.deadIm
			
			if self.lives<1:
				self.slideCount = 0
				self.lives = 3
				self.frenzy = 1
				self.points = 0
		
		self.beat = False
		self.death = False
	
	def reset(self):
		self.walls.empty()
		
	def draw(self):
		self.image.fill(0)
		
		self.background.draw(self.image)
		self.walls.draw(self.image)
		self.effects.draw(self.image)
		self.foreground.draw(self.image)
		self.menusGroup.draw(self.image)
		
		# raise backgrount to top for debug
		#self.background.draw(self.image)
		
		
		#slides
		self.slideGroup.draw(self.image)
		
		
		fps = pygame.font.SysFont(
				"monospace", 24
			).render(
				str(int(self.clock.get_fps()))+"fps",
				True, (100,100,100)
			)
		
		self.image.blit(
			fps,
			(
				self.rect.w-fps.get_width(),
				self.rect.h-fps.get_height()
			)
		)
		
		pygame.display.update()
		#pygame.display.flip()


def main():
	print "GGJ"
	Game().run()

if __name__=="__main__":
	main()
