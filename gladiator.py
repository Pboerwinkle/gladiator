import numpy
import random
import math as m
import pygame
import pygame.draw
pygame.init()
screenSize = (1200, 900)
screen = pygame.display.set_mode(screenSize)
while not pygame.display.get_active():
	time.sleep(0.1)
pygame.display.set_caption("snake", "snake")
clock = pygame.time.Clock()
framerate = 60

tileCodes = {0: "floor", 1: "wall", 2: "hole"}
imgs = {"floor": [pygame.image.load("floor.png"), 8],
		"wall": [pygame.image.load("wall.png"), 80],
		"hole": [pygame.image.load("hole.png"), 0],
		"gladiator": [pygame.image.load("gladiator.png"), 80],
		"snake": [pygame.image.load("snake.png"), 80]}

mapList = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
		   [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		   [1, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 1],
		   [1, 0, 2, 2, 2, 2, 0, 0, 2, 0, 0, 1],
		   [1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1],
		   [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		   [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]
entityList = [[0 for i in range(12)] for i in range(7)]

class Gladiator:
	def __init__(self, pos):
		self.pos = pos
		self.controls = {"q": [0, -1], "w": [-1, 0], "e": [0, 1], "a": [1, -1], "s": [1, 0], "d": [1, 1]}
		entityList[self.pos[0]][self.pos[1]] = "gladiator"
	def move(self, inp):
		entityList[self.pos[0]][self.pos[1]] = 0
		addend = 0
		x = self.pos[1]
		if inp != "w" and inp != "s":
			if self.pos[1]%2 != 0:
				addend = -1
			x = self.pos[1] + self.controls[inp][1]
		y = self.pos[0] + self.controls[inp][0] + addend
		for i, snake in enumerate(snakes):
			if snake != 0 and snake.pos == [y, x]:
				entityList[snake.pos[0]][snake.pos[1]] = 0
				snakes[i] = 0
				y = player.pos[0]
				x = player.pos[1]
				break
		if mapList[y][x] == 0:
			self.pos = [y, x]
		entityList[self.pos[0]][self.pos[1]] = "gladiator"

player = Gladiator([3, 6])

class Snake:
	def __init__(self, pos):
		self.pos = pos
		entityList[self.pos[0]][self.pos[1]] = "snake"

	def move(self):
		distance = [[m.inf for i in range(12)] for i in range(7)]
		unvisited = [[1 for i in range(12)] for i in range(7)]
		distance[self.pos[0]][self.pos[1]] = 0
		while True:
			smallest = m.inf
			current = [0, 0]
			for i, y in enumerate(distance):
				for j, x in enumerate(y):
					if x < smallest and unvisited[i][j] == 1:
						smallest = x
						current = [i, j]
			if smallest == m.inf:
				break
			neighbors = getNeighbors(current)
			for neighbor in neighbors:
				if mapList[neighbor[0]][neighbor[1]] == 0 and smallest+1 < distance[neighbor[0]][neighbor[1]]:
					distance[neighbor[0]][neighbor[1]] = smallest+1
			unvisited[current[0]][current[1]] = 0
			if current == player.pos:
				path = [current[:]]
				while True:
					neighbors = getNeighbors(current)
					smallest = m.inf
					current = [0, 0]
					for neighbor in neighbors:
						if distance[neighbor[0]][neighbor[1]] < smallest:
							smallest = distance[neighbor[0]][neighbor[1]]
							current = neighbor
					path.append(current[:])
					if current == self.pos:
						break
				entityList[self.pos[0]][self.pos[1]] = 0
				self.pos = path[-2]
				if path[-2] == player.pos:
					killPlayer()
					self.pos = path[-1]
				entityList[self.pos[0]][self.pos[1]] = "snake"
				break

snakes = [0 for i in range(10)]
snakes[0] = Snake([1, 3])

def drawHex(img, x, y, s=120):
	screen.blit(imgs[img][0], (x*(2/3)*s, y*(2/3*s) + (x%2==0)*(2/6)*s - imgs[img][1]))

def getNeighbors(pos):
	neighbors = []
	addend = 0
	if pos[1]%2 != 0:
		addend = -1
	diffs = [[0+addend, -1], [-1, 0], [0+addend, 1], [1+addend, -1], [1, 0], [1+addend, 1]]
	for diff in diffs:
		neighbors.append([pos[0]+diff[0], pos[1]+diff[1]])
	return neighbors

def killPlayer():
	global player
	entityList[player.pos[0]][player.pos[1]] = 0
	player = 0

while True:
	clock.tick(framerate)
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()
		if event.type == pygame.KEYDOWN and player != 0 and event.unicode in player.controls.keys():
			player.move(event.unicode)
			for snake in snakes:
				if snake != 0:
					snake.move()

	screen.fill((22, 19, 16))

	for y in range(len(mapList)):
		for x in range(len(mapList[y])):
			if x%2 != 0:
				drawHex(tileCodes[mapList[y][x]], x, y)
				if entityList[y][x] != 0:
					drawHex(entityList[y][x], x, y)
		for x in range(len(mapList[y])):
			if x%2 == 0:
				drawHex(tileCodes[mapList[y][x]], x, y)
				if entityList[y][x] != 0:
					drawHex(entityList[y][x], x, y)

	pygame.display.flip()
