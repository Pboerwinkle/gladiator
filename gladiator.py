import config
import numpy
import random
import math as m
import pygame
import pygame.draw
pygame.init()
screenSize = config.SCREEN_SIZE
screen = pygame.display.set_mode(screenSize)
while not pygame.display.get_active():
	time.sleep(0.1)
pygame.display.set_caption("snake", "snake")
clock = pygame.time.Clock()
framerate = 60

assets = "assets"+config.CHANGE_FOLDER
tileCodes = {0: "floor", 1: "wall", 2: "hole", 3: "grate", 4: "pillar"}
imgs = {"floor": [pygame.image.load(assets+"floor.png"), 8],
		"wall": [pygame.image.load(assets+"wall.png"), 160],
		"pillar": [pygame.image.load(assets+"pillar.png"), 88],
		"grate": [pygame.image.load(assets+"grate.png"), 0],
		"gladiator": [pygame.image.load(assets+"gladiator.png"), 80],
		"gladiatorDying": [pygame.image.load(assets+"gladiatorDying.png"), 80],
		"snake1": [pygame.image.load(assets+"snake1.png"), 80],
		"snake2": [pygame.image.load(assets+"snake2.png"), 80],
		"snakeDying": [pygame.image.load(assets+"snakeDying.png"), 80],
		"timer": pygame.image.load(assets+"timer.png")}
walkableTiles = [0, 3]

mapList = config.MAP_LIST
mapSize = [len(mapList), len(mapList[0])]
spawns = {"gladiator": [6, 2], "snake": [[6, 7], [6, 9], [7, 7], [7, 9]]}
entityList = [[0 for i in range(mapSize[1])] for i in range(mapSize[0])]
animationList = []

class Gladiator:
	def __init__(self, pos):
		self.pos = pos
		self.controls = config.CONTROLS
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
				playerStats["killed"] += 1
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
	global playerStats
	entityList[player.pos[0]][player.pos[1]] = 0
	dying.append({"pos": player.pos, "img": "gladiatorDying", "percent": 0})
	player = 0
	playerStats["totalTime"] = (pygame.time.get_ticks()-playerStats["totalTime"])/1000
	print(playerStats)

def spawnSnakes():
	global snakesToSpawn
	global roundNum
	global snakeSpawns
	global timeLimit
	snakesLeft = False
	for snake in snakes:
		if snake != 0:
			snakesLeft = True
			break
	if not snakesLeft and snakesToSpawn == 0:
		roundNum += 1
		snakesToSpawn += roundNum
		timeLimit -= 467
		if timeLimit < 3000:
			timeLimit = 3000
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
snakeSpawns.extend(spawns["snake"])
for spawn in spawnNeighbors:
	if mapList[spawn[0]][spawn[1]] in walkableTiles and spawn not in snakeSpawns:
		snakeSpawns.append(spawn)
snakes = [0 for i in range(100)]
roundNum = 0
snakesToSpawn = 0

def drawImg(img, pos, height = 0):
	screen.blit(imgs[img][0], (pos[1] - offset[0], pos[0] - imgs[img][1] - height - offset[1]))

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
	imgsToRemove = []
	for i, img in enumerate(entityImgs):
		if img["pos"][0]/80 - 1/2 <= tilePos[0]/80:
			if round(img["pos"][1]/80) == round(tilePos[1]/80):
				drawImg(img["img"], img["pos"], height=img["height"])
				imgsToRemove.append(i)
	imgsToRemove.sort()
	for i, img in enumerate(imgsToRemove):
		del entityImgs[img-i]

dying = []
particles = []

playerMoved = False
moveTime = 0
camera = convertHex(player.pos)

playerStats = {"killed": 0, "moves": 1, "totalTime": pygame.time.get_ticks()}

timerStart = pygame.time.get_ticks()
timerRect = (screenSize[0]/2-70, screenSize[1]-140-40, 140, 140)
timeLimit = 10467
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
			timerStart = pygame.time.get_ticks()
	if (playerMoved and pygame.time.get_ticks() - moveTime >= 500) or pygame.time.get_ticks() - timerStart >= timeLimit:
			for snake in snakes:
				if snake != 0:
					snake.move()
			spawnSnakes()
			playerMoved = False
			playerStats["moves"] += 1
	if pygame.time.get_ticks() - timerStart >= timeLimit:
			timerStart = pygame.time.get_ticks()

	if player != 0:
		playerPos = convertHex(player.pos)
		posDiff = [camera[1]-playerPos[1], camera[0]-playerPos[0]]
		cameraDist = m.sqrt((posDiff[0])**2+(posDiff[1])**2)
		angle = m.atan2(posDiff[1], posDiff[0])
		camera = [camera[0]-m.sin(angle)*(cameraDist/3), camera[1]-m.cos(angle)*(cameraDist/3)]
		offset = [camera[1]-screenSize[0]/2+60, camera[0]-screenSize[1]/2+40]
		if offset[0] < -200:
			offset[0] = -200
		if offset[0] > (len(mapList[0])*80)-screenSize[0]+200+40:
			offset[0] = (len(mapList[0])*80)-screenSize[0]+200+40
		if offset[1] < 0-240:
			offset[1] = 0-240
		if offset[1] > (len(mapList)*80)-screenSize[1]+40:
			offset[1] = (len(mapList)*80)-screenSize[1]+40

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
				if mapList[y][x] != 2:
					hexPos = convertHex([y, x])
					drawImg(tileCodes[mapList[y][x]], hexPos)
					checkImgPos(hexPos)
		for x in range(len(mapList[y])):
			if x%2 == 0:
				if mapList[y][x] != 2:
					hexPos = convertHex([y, x])
					drawImg(tileCodes[mapList[y][x]], hexPos)
					checkImgPos(hexPos)

	for particle in particles:
		distance = particle["percent"]*particle["distance"]
		height = -4*particle["height"]*(1/particle["distance"]*distance - 1/2)**2 + particle["height"]
		x = particle["start"][1]+distance+60
		y = particle["start"][0]-height+40
		pygame.draw.circle(screen, particle["color"], (x-offset[0], y-offset[1]), particle["size"])
		particle["percent"] += 0.05
		if y > screenSize[1] + offset[1]:
			particles.remove(particle)

	pygame.draw.ellipse(screen, (0, 0, 0), timerRect, width=48)
	currentTimeProp = (pygame.time.get_ticks() - timerStart)/timeLimit
	pygame.draw.arc(screen, (150, 0, 0), timerRect, m.pi/2, -currentTimeProp*2*m.pi + m.pi/2, width=48)
	screen.blit(imgs["timer"], (timerRect[0]-5, timerRect[1]-5))
	pygame.display.flip()
