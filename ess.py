from matplotlib import pyplot
import pygame
import random
import math

pygame.init() #run pygame

#WINDOWS SECTION
WIDTH = 800
HEIGHT = 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

# COLORCODE SECTION
COLOR_DEFINITIONS = {
	"grey" : (48, 56, 65),
	"light_grey" : (70, 70, 90),
	"white" : (255, 248, 240),
	"red" : (239, 71, 111),
	"blue" : (17, 138, 178)
}
COLORS = {
	"background" : COLOR_DEFINITIONS["grey"],
	"healthy" : COLOR_DEFINITIONS["white"],
	"infected": COLOR_DEFINITIONS["red"],
	"immune": COLOR_DEFINITIONS["blue"],
	"dead": COLOR_DEFINITIONS["light_grey"]
}


class Cell():
	def __init__(self, row, col):
		self.row = row
		self.col = col
		self.people = []

	def get_neighboring_cells(self, n_rows, n_cols):
		index = self.row * n_cols + self.col
		N = index - n_cols if self.row > 0 else None
		S = index + n_cols if self.row < n_rows - 1 else None
		W = index - 1 if self.col > 0 else None
		E = index + 1 if self.col < n_cols - 1 else None
		NW = index - n_cols - 1 if self.row > 0 and self.col > 0 else None
		NE = index - n_cols + 1 if self.row > 0 and self.col < n_cols - 1 else None
		SW = index + n_cols - 1 if self.row < n_rows - 1 and self.col > 0 else None
		SE = index + n_cols + 1 if self.row < n_rows - 1 and self.col < n_cols - 1 else None
		return [i for i in [index, N, S, E, W, NW, NE, SW, SE] if i]


class Grid():
	def __init__(self, people, h_size = 20, v_size = 20):
		self.h_size = h_size
		self.v_size = v_size
		self.n_rows = HEIGHT // v_size
		self.n_cols = WIDTH // h_size
		self.cells = []
		for row in range(self.n_rows):
			for col in range(self.n_cols):
				self.cells.append(Cell(row,col))
		self.store_people(people)

	def store_people(self, people):
		for p in people:
			row = int(p.y / self.v_size)
			col = int (p.x/ self.h_size)
			index = row * self.n_cols + col
			self.cells[index].people.append(p)
	def show(self, widht = 1):
		for c in self.cells:
			x = c.col * self.h_size
			y = c.row * self.v_size
			rect = pygame.Rect(x, y, self.h_size, self.v_size)
			pygame.draw.rect(SCREEN, COLOR_DEFINITIONS["light_grey"], rect, width = widht)


#PERSON
class Person:
	def __init__(self):
		self.x = random.uniform(0, WIDTH)
		self.y = random.uniform(0, HEIGHT)
		self.dx = 0
		self.dy = 0
		self.state = "healthy"
		self.recover_counter = 0
		self.immunity_counter = 0

	def show(self, size = 10):
		pygame.draw.circle(SCREEN, COLORS[self.state], (self.x,self.y), size)

	def move(self, speed = 0.01 ):
		#position vector
		self.x += self.dx
		self.y += self.dy

		#bounds return
		if self.x >= WIDTH:
			self.x = WIDTH - 1
			self.dx *= - 1
		if self.y >= HEIGHT:
			self.y = HEIGHT - 1
			self.dy *= - 1
		if self.x <= 0:
			self.x = 1
			self.dx *= -1
		if self.y <= 0:
			self.y = 1
			self.dy *= -1

		#velocity vector
		self.dx += random.uniform(-speed, speed)
		self.dy += random.uniform(-speed, speed)

	def get_infected(self, value = 250):
		self.state = "infected"
		self.recover_counter = value

	def recover(self, value = 50):
		self.recover_counter -= 1 
		if self.recover_counter == 0:
			self.state = "immune"
			self.immunity_counter = value

	def lose_immunity(self):
		self.immunity_counter -= 1
		if self.immunity_counter == 0:
			self.state = "healthy"

	def die(self, probability = 0.00001):
		if random.uniform(0,1) < probability:
			self.state = "dead"

class Pandemic():
	def __init__(self, n_people = 1000, size = 3, 
		speed = 0.09, infect_dist = 10, recover_time = 200, 
		immune_time = 1000, prob_catch = 0.1, prob_death = 0.00005):
		self.people = [Person() for i in range(n_people)]
		self.size = size
		self.speed = speed
		self.infect_dist = infect_dist
		self.recover_time = recover_time
		self.immune_time = immune_time
		self.prob_catch = prob_catch
		self.prob_death = prob_death
		self.people[0].get_infected(self.recover_time)
		self.grid = Grid(self.people)
		self.record = []
		self.over = False

	def update_grid(self):
		self.grid = Grid(self.people)
		
	def slowly_infect_people(self):
		for p in self.people:
			if p.state == "infected":
				for other in self.people:
					if other.state =="healthy":
						dist = math.sqrt((p.x-other.x)**2 + (p.y-other.y)**2)
						if dist < self.infect_dist:
							other.get_infected()

	def infect_people(self):
		for c in self.grid.cells:
			states = [p.state for p in c.people]
			if states.count("infected") == 0:
				continue
			#create list of all infected/healthy people in area
			people_in_area = []
			for index in c.get_neighboring_cells(self.grid.n_rows, self.grid.n_cols):
				people_in_area += self.grid.cells[index].people
				infected_people = [p for p in people_in_area if p.state == "infected"]
				healthy_people = [p for p in people_in_area if p.state == "healthy"]
				if len(healthy_people) == 0:
					continue

				for i in infected_people:
					for h in healthy_people:
						dist = math.sqrt((i.x-h.x)**2 + (i.y-h.y)**2)
						if dist < self.infect_dist:
							if random.uniform(0,1) < self.prob_catch:
								h.get_infected(self.recover_time)

	def run(self):
		self.update_grid()
		self.slowly_infect_people()
		for p in self.people:
			if p.state == "infected":
				p.die(self.prob_death)
				p.recover(self.immune_time)
			elif p.state == "immune":
				p.lose_immunity()
			p.move(self.speed)
			p.show(self.size)

	def keep_tack(self):
		states = [p.state for p in self.people]
		n_infected = states.count("infected")
		n_dead = states.count("dead")
		self.record.append([n_infected, n_dead])
		if n_infected == 0 :
			self.over = True

	def summarize(self):
		time_index = range(1 , len(self.record)+1)		
		infected = [r[0] for r in self.record]
		dead = [r[1] for r in self.record]

		fig, ax = pyplot.subplots()
		ax.plot(time_index, infected, color = "red")
		ax.set_xlabel("Period")
		ax.set_ylabel("People currently infected", color = "red")

		#cumulative deaths
		ax2 = ax.twinx()
		ax2.plot(time_index, dead, color = "black")
		ax2.set_ylabel("Cumulative death count", color = "black")


		pyplot.show()

pandemic = Pandemic()

animating = True
pausing = False
while animating and not pandemic.over:

	if not pausing:
		#animating code
		SCREEN.fill(COLORS["background"])

		#run pandemic and keep track
		pandemic.run()
		pandemic.keep_tack()


		pygame.display.flip()

	#user interaction(exit)
	for event in pygame.event.get():
		#user close pygame
		if event.type == pygame.QUIT:
			animating = False

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				animating = False

			if event.key == pygame.K_RETURN:
				pausing = False
				pandemic = Pandemic()

			if event.key ==pygame.K_SPACE:
				pausing = not pausing

#symmary plot of pandemic
pandemic.summarize()
