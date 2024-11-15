from panda3d.core import loadPrcFile
loadPrcFile('config.prc')
from panda3d.core import (
    AmbientLight, 
    DirectionalLight, 
    Vec3, 
    Vec4, 
    CollisionTraverser, 
    CollisionHandlerPusher,
    CollisionSphere, 
    CollisionNode,
    CollisionTube
)
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

from gameObjects.Player import Player
from gameObjects.Enemy import Enemy, WalkingEnemy
from gameObjects.TrapEnemy import TrapEnemy

import random

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        self.initConfig()
        self.create()
        
    def initConfig(self):
        self.disableMouse()
        
        self.camera.setPos(0, 0, 32)
        self.camera.setP(-90)
        self.render.setShaderAuto()    
        
        self.setKeyMap()
        
        # init collisions
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()        
        self.pusher.setHorizontal(True) # set horizontal 2D not 3D collision  
        self.pusher.add_in_pattern("%fn-into-%in")
        
        self.accept("trapEnemy-into-wall", self.stopTrap)
        self.accept("trapEnemy-into-trapEnemy", self.stopTrap)
        self.accept("trapEnemy-into-player", self.trapHitsSomething)
        self.accept("trapEnemy-into-walkingEnemy", self.trapHitsSomething)
        # end collisions

        self.updateTask = self.taskMgr.add(self.update, "update")
        
    def create(self):
        self.createLights()
        
        self.environment = self.loader.loadModel("assets/models/environment/environment")
        self.environment.reparentTo(self.render)
        self.setWallColider()
        
        self.player = None
        self.enemies = []
        self.trapEnemies = []
        self.deadEnemies = []
        
        self.spawnPoints = []
        numPointsPerWall = 5
        for i in range(numPointsPerWall):
            coord = 7.0/numPointsPerWall + 0.5
            self.spawnPoints.append(Vec3(-7.0, coord, 0))
            self.spawnPoints.append(Vec3(7.0, coord, 0))
            self.spawnPoints.append(Vec3(coord, -7.0, 0))
            self.spawnPoints.append(Vec3(coord, 7.0, 0))
            
        self.initialSpawnInterval = 1.0
        self.minimumSpawnInterval = 0.2
        self.spawnInterval = self.initialSpawnInterval
        self.spawnTimer = self.spawnInterval
        self.maxEnemies = 2
        self.maximumMaxEnemies = 20

        self.numTrapsPerSide = 2

        self.difficultyInterval = 5.0
        self.difficultyTimer = self.difficultyInterval

        self.startGame()
        
        self.exitFunc = self.cleanup
        
        music = loader.loadMusic("assets/sounds/bg.ogg")
        music.setLoop(True)
        music.setVolume(0.075)
        music.play()
        
        self.enemySpawnSound = loader.loadSfx("assets/sounds/enemySpawn.ogg")
        
    def update(self, task):
        dt = globalClock.getDt()
        
        self.player.update(self.keyMap, dt)
        
        if self.player is not None:
            if self.player.health > 0:
                self.player.update(self.keyMap, dt)

                self.spawnTimer -= dt
                if self.spawnTimer <= 0:
                    self.spawnTimer = self.spawnInterval
                    self.spawnEnemy()

                [enemy.update(self.player, dt) for enemy in self.enemies]
                [trap.update(self.player, dt) for trap in self.trapEnemies]

                newlyDeadEnemies = [enemy for enemy in self.enemies if enemy.health <= 0]
                self.enemies = [enemy for enemy in self.enemies if enemy.health > 0]

                for enemy in newlyDeadEnemies:
                    enemy.collider.removeNode()
                    enemy.actor.play("die")
                    self.player.score += enemy.scoreValue
                if len(newlyDeadEnemies) > 0:
                    self.player.updateScore()

                self.deadEnemies += newlyDeadEnemies
                
                enemiesAnimatingDeaths = []
                for enemy in self.deadEnemies:
                    deathAnimControl = enemy.actor.getAnimControl("die")
                    if deathAnimControl is None or not deathAnimControl.isPlaying():
                        enemy.cleanup()
                    else:
                        enemiesAnimatingDeaths.append(enemy)
                self.deadEnemies = enemiesAnimatingDeaths
                
                self.difficultyTimer -= dt
                if self.difficultyTimer <= 0:
                    self.difficultyTimer = self.difficultyInterval
                    if self.maxEnemies < self.maximumMaxEnemies:
                        self.maxEnemies += 1
                    if self.spawnInterval > self.minimumSpawnInterval:
                        self.spawnInterval -= 0.1
        
        return task.cont
        
    def setKeyMap(self):
        self.keyMap = {
            "up" : False,
            "down" : False,
            "left" : False,
            "right" : False,
            "shoot" : False
        }
        
        self.accept("w", self.updateKeyMap, ["up", True])
        self.accept("w-up", self.updateKeyMap, ["up", False])
        self.accept("s", self.updateKeyMap, ["down", True])
        self.accept("s-up", self.updateKeyMap, ["down", False])
        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])
        self.accept("mouse1", self.updateKeyMap, ["shoot", True])
        self.accept("mouse1-up", self.updateKeyMap, ["shoot", False])
        
    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState
        
    def createLights(self):
        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.ambientLightNodePath = self.render.attachNewNode(ambientLight)
        self.render.setLight(self.ambientLightNodePath)
        
        mainLight = DirectionalLight("main light")
        self.mainLightNodePath = self.render.attachNewNode(mainLight)
        self.mainLightNodePath.setHpr(45, -45, 0)
        self.render.setLight(self.mainLightNodePath)
    
    def setWallColider(self):
        wallSolid = CollisionTube(-8.0, 0, 0, 8.0, 0, 0, 0.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = render.attachNewNode(wallNode)
        wall.setY(8.0)
        wall.show()

        wallSolid = CollisionTube(-8.0, 0, 0, 8.0, 0, 0, 0.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = render.attachNewNode(wallNode)
        wall.setY(-8.0)
        wall.show()

        wallSolid = CollisionTube(0, -8.0, 0, 0, 8.0, 0, 0.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = render.attachNewNode(wallNode)
        wall.setX(8.0)
        wall.show()

        wallSolid = CollisionTube(0, -8.0, 0, 0, 8.0, 0, 0.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = render.attachNewNode(wallNode)
        wall.setX(-8.0)
        wall.show()
        
    def stopTrap(self, entry):
        collider = entry.getFromNodePath()
        if collider.hasPythonTag("owner"):
            trap = collider.getPythonTag("owner")
            trap.moveDirection = 0
            trap.ignorePlayer = False
            
    def trapHitsSomething(self, entry):
        collider = entry.getFromNodePath()
        if collider.hasPythonTag("owner"):
            trap = collider.getPythonTag("owner")

            # We don't want stationary traps to do damage,
            # so ignore the collision if the "moveDirection" is 0
            if trap.moveDirection == 0:
                return

            collider = entry.getIntoNodePath()
            if collider.hasPythonTag("owner"):
                obj = collider.getPythonTag("owner")
                if isinstance(obj, Player):
                    if not trap.ignorePlayer:
                        obj.alterHealth(-1)
                        trap.ignorePlayer = True
                else:
                    obj.alterHealth(-10)
                    
    def startGame(self):
        self.cleanup()

        self.player = Player()

        self.maxEnemies = 2
        self.spawnInterval = self.initialSpawnInterval

        self.difficultyTimer = self.difficultyInterval

        sideTrapSlots = [
            [],
            [],
            [],
            []
        ]
        trapSlotDistance = 0.4
        slotPos = -8 + trapSlotDistance
        while slotPos < 8:
            if abs(slotPos) > 1.0:
                sideTrapSlots[0].append(slotPos)
                sideTrapSlots[1].append(slotPos)
                sideTrapSlots[2].append(slotPos)
                sideTrapSlots[3].append(slotPos)
            slotPos += trapSlotDistance

        for i in range(self.numTrapsPerSide):
            slot = sideTrapSlots[0].pop(random.randint(0, len(sideTrapSlots[0])-1))
            trap = TrapEnemy(Vec3(slot, 7.0, 0))
            self.trapEnemies.append(trap)

            slot = sideTrapSlots[1].pop(random.randint(0, len(sideTrapSlots[1])-1))
            trap = TrapEnemy(Vec3(slot, -7.0, 0))
            self.trapEnemies.append(trap)

            slot = sideTrapSlots[2].pop(random.randint(0, len(sideTrapSlots[2])-1))
            trap = TrapEnemy(Vec3(7.0, slot, 0))
            trap.moveInX = True
            self.trapEnemies.append(trap)

            slot = sideTrapSlots[3].pop(random.randint(0, len(sideTrapSlots[3])-1))
            trap = TrapEnemy(Vec3(-7.0, slot, 0))
            trap.moveInX = True
            self.trapEnemies.append(trap)
            
    def cleanup(self):
        for enemy in self.enemies:
            enemy.cleanup()
        self.enemies = []

        for enemy in self.deadEnemies:
            enemy.cleanup()
        self.deadEnemies = []

        for trap in self.trapEnemies:
            trap.cleanup()
        self.trapEnemies = []

        if self.player is not None:
            self.player.cleanup()
            self.player = None

    def quit(self):
        self.cleanup()
        base.userExit()
        
    def spawnEnemy(self):
        if len(self.enemies) < self.maxEnemies:
            spawnPoint = random.choice(self.spawnPoints)

            newEnemy = WalkingEnemy(spawnPoint)

            self.enemies.append(newEnemy)
            
            self.enemySpawnSound.play()
        
game = Game()
game.run()
    
