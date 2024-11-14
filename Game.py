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
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()        
        self.pusher.setHorizontal(True) # set horizontal 2D not 3D collision        
        self.updateTask = self.taskMgr.add(self.update, "update")
        
    def create(self):
        self.createLights()
        
        self.environment = self.loader.loadModel("assets/models/environment/environment")
        self.environment.reparentTo(self.render)
        self.setWallColider()
        
        self.player = Player()
        self.tempEnemy = WalkingEnemy(Vec3(5, 0, 0))
        
    def update(self, task):
        dt = globalClock.getDt()
        
        self.player.update(self.keyMap, dt)
        self.tempEnemy.update(self.player, dt)
        
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
        
game = Game()
game.run()
    
