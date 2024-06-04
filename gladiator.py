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

tileCodes = {0: "floor", 1: "wall", 2: "hole", 3: "grate"}
imgs = {"floor": [pygame.image.load("floor.png"), 8],
		"wall": [pygame.image.load("wall.png"), 80],
		"hole": [pygame.image.load("hole.png"), 0],
		"grate": [pygame.image.load("grate.png"), 0],
		"gladiator": [pygame.image.load("gladiator.png"), 80],
		"gladiatorDying": [pygame.image.load("gladiatorDying.png"), 80],
		"snake1": [pygame.image.load("snake1.png"), 80],
		"snake2": [pygame.image.load("snake2.png"), 80],
		"snakeDying": [pygame.image.load("snakeDying.png"), 80]}
walkableTiles = [0, 3]

mapList = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
		   [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
		   [1, 0, 2, 0, 0, 0, 1, 0, 0, 0, 2, 0, 1],
		   [1, 0, 0, 0, 0, 3, 1, 3, 0, 0, 0, 0, 1],
		   [1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
		   [1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
		   [2, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 2],
		   [2, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 2],
		   [2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2],
		   [2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 2],
		   [2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2, 2],
		   [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]
mapSize = [len(mapList), len(mapList[0])]
spawns = {"gladiator": [3, 2], "snake": [[3, 5], [3, 7]]}
entityList = [[0 for i in range(mapSize[1])] for i in range(mapSize[0])]
animationList = []

class Gladiator:
	def __init__(self, pos):
		self.pos = pos
		self.controls = {"q": [0, -1], "w": [-1, 0], "e": [0, 1], "a": [1, -1], "s": [1, 0], "d": [1, 1], "1": [0, 0]}
		entityList[self.pos[0]][self.pos[1]] = "gladiator"
		self.animation = {"img": "gladiator", "type": "stand", "pos": [self.pos[:], self.pos[:]], "percent": None}

	def move(self, inp):
		entityList[self.pos[0]][self.pos[1]] = 0
		addend = 0
		x = self.pos[1]
		if inp != "w" and inp != "s" and inp != "1":
			if self.pos[1]%2 != 0:
				addend = -1
			x = self.pos[1] + self.controls[inp][1]
		y = self.pos[0] + self.controls[inp][0] + addend
		killedSnake = False
		for i, snake in enumerate(snakes):
			if snake != 0 and snake.pos == [y, x]:
				entityList[snake.pos[0]][snake.pos[1]] = 0
				dying.append({"pos": snake.pos, "img": "snakeDying", "percent": 0})
				snakes[i] = 0
				break
		if mapList[y][x] not in walkableTiles:
			y = self.pos[0]
			x = self.pos[1]
		self.animation = {"img": "gladiator", "type": "move", "pos": [self.pos[:], [y, x]], "percent": 0}
		player.pos = [y, x]
		entityList[self.pos[0]][self.pos[1]] = "gladiator"

player = Gladiator(spawns["gladiator"])

class Snake:
	def __init__(self, pos, state):
		self.pos = pos
		self.state = state
		self.speed = 2
		entityList[self.pos[0]][self.pos[1]] = "snake"+str(self.state)
		self.animation = {"img": "snake"+str(self.state), "type": "stand", "pos": [self.pos[:], self.pos[:]], "percent": None}

	def move(self):
		if self.state < self.speed:
			self.state += 1
			self.animation = {"img": "snake"+str(self.state), "type": "shake", "pos": [self.pos[:], self.pos[:]], "percent":0.5}
			entityList[self.pos[0]][self.pos[1]] = "snake"+str(self.state)
			return
		self.state = 1
		if player == 0:
			return
		distance = [[m.inf for i in range(mapSize[1])] for i in range(mapSize[0])]
		unvisited = [[1 for i in range(mapSize[1])] for i in range(mapSize[0])]
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
				noEnts = False
				if entityList[neighbor[0]][neighbor[1]] == 0 or entityList[neighbor[0]][neighbor[1]] == "gladiator":
					noEnts = True
				if mapList[neighbor[0]][neighbor[1]] in walkableTiles and noEnts and smallest+1 < distance[neighbor[0]][neighbor[1]]:
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
				self.animation = {"img": "snake"+str(self.state), "type": "move", "pos": [self.pos[:], path[-2]], "percent": 0}
				self.pos = path[-2]
				if path[-2] == player.pos:
					killPlayer()
				entityList[self.pos[0]][self.pos[1]] = "snake"+str(self.state)
				break

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
	dying.append({"pos": player.pos, "img": "gladiatorDying", "percent": 0})
	player = 0

def spawnSnakes():
	global snakesToSpawn
	global roundNum
	global snakeSpawns
	snakesLeft = False
	for snake in snakes:
		if snake != 0:
			snakesLeft = True
			break
	if not snakesLeft and snakesToSpawn == 0:
		roundNum += 1
		snakesToSpawn += roundNum
	if snakesToSpawn:
		availableSpawns = []
		for spawn in snakeSpawns:
			if entityList[spawn[0]][spawn[1]] == 0:
				availableSpawns.append(spawn[:])
		while snakesToSpawn > 0 and 0 in snakes and len(availableSpawns) > 0:
			i = random.randint(0, len(availableSpawns)-1)
			pos = availableSpawns[i]
			state = random.randint(1, 2)
			snakes[snakes.index(0)] = Snake(pos, state)
			del availableSpawns[i]
			snakesToSpawn -= 1
			

spawnNeighbors = []
for spawn in spawns["snake"]:
	spawnNeighbors.extend(getNeighbors(spawn))
snakeSpawns = []
for spawn in spawnNeighbors:
	if mapList[spawn[0]][spawn[1]] in walkableTiles:
		snakeSpawns.append(spawn)
snakeSpawns.extend(spawns["snake"])
snakes = [0 for i in range(100)]
roundNum = 0
snakesToSpawn = 0

def drawImg(img, pos, height = 0):
	screen.blit(imgs[img][0], (pos[1], pos[0] - imgs[img][1] - height))

def convertHex(pos, s=120):
	return [pos[0]*(2*s/3) + (pos[1]%2==0)*(1*s/3), pos[1]*(2*s/3)]

def playAnim(actor):
	global entityImgs
	if actor.animation["percent"] != None:
		actor.animation["percent"] += 0.05
		if actor.animation["percent"] >= 0.95:
			actor.animation = {"img": actor.animation["img"], "type": "stand", "pos": [actor.animation["pos"][1], actor.animation["pos"][1]], "percent": None}

	pos = [convertHex(actor.animation["pos"][0]), convertHex(actor.animation["pos"][1])]
	if actor.animation["type"] == "move":
		y = pos[0][0] + (pos[1][0] - pos[0][0])*actor.animation["percent"]
		x = pos[0][1] + (pos[1][1] - pos[0][1])*actor.animation["percent"]
		height = -500*(actor.animation["percent"]-0.5)**2+120
		if height<0:
			height = 0
		entityImgs.append({"img": actor.animation["img"], "pos": [y, x], "height": height})
	elif actor.animation["type"] == "stand":
		entityImgs.append({"img": actor.animation["img"], "pos": pos[0], "height": 0})
	elif actor.animation["type"] == "shake":
		height = 20*m.sin(6*m.pi*actor.animation["percent"])
		entityImgs.append({"img": actor.animation["img"], "pos": pos[0], "height": height})

entityImgs = []
def checkImgPos(tilePos):
	for img in entityImgs:
		if img["pos"][0]/80 - 1/2 <= tilePos[0]/80:
			if round(img["pos"][1]/80) == round(tilePos[1]/80):
				drawImg(img["img"], img["pos"], height=img["height"])
				entityImgs.remove(img)

dying = []
particles = []

playerMoved = False
moveTime = 0
while True:
	clock.tick(framerate)
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()
		if event.type == pygame.KEYDOWN and player != 0 and event.unicode in player.controls.keys() and not playerMoved:
			player.move(event.unicode)
			playerMoved = True
			moveTime = pygame.time.get_ticks()
	if playerMoved and pygame.time.get_ticks() - moveTime >= 500:
			for snake in snakes:
				if snake != 0:
					snake.move()
			spawnSnakes()
			playerMoved = False

	for death in dying:
		if death["percent"] < 1:
			death["percent"] += .05
			entityImgs.append({"img": death["img"], "pos": convertHex(death["pos"]), "height": 0})
		else:
			if death["img"] == "snakeDying":
				color = (81, 57, 49)
			else:
				color = (140, 133, 114)
			start = convertHex(death["pos"])
			dying.remove(death)
			for i in range(15):
				distance = random.randint(-200, 200)
				if distance == 0:
					distance = 1
				height = random.randint(100, 200)
				size = random.randint(5, 10)
				darkness = random.randint(-40, 40)
				thisColor = (color[0]+darkness, color[1]+darkness, color[2]+darkness)
				particles.append({"start": start, "distance": distance, "height": height, "size": size, "color": thisColor, "percent": 0})
	if player != 0:
		playAnim(player)
	for snake in snakes:
		if snake != 0:
			playAnim(snake)

	screen.fill((22, 19, 16))

	for y in range(len(mapList)):
		for x in range(len(mapList[y])):
			if x%2 != 0:
				hexPos = convertHex([y, x])
				drawImg(tileCodes[mapList[y][x]], hexPos)
				checkImgPos(hexPos)
		for x in range(len(mapList[y])):
			if x%2 == 0:
				hexPos = convertHex([y, x])
				drawImg(tileCodes[mapList[y][x]], hexPos)
				checkImgPos(hexPos)

	for particle in particles:
		distance = particle["percent"]*particle["distance"]
		height = -4*particle["height"]*(1/particle["distance"]*distance - 1/2)**2 + particle["height"]
		x = particle["start"][1]+distance+60
		y = particle["start"][0]-height+40
		pygame.draw.circle(screen, particle["color"], (x, y), particle["size"])
		particle["percent"] += 0.05
		if y > screenSize[1]:
			particles.remove(particle)
	pygame.display.flip()
