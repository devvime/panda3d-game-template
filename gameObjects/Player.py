from panda3d.core import Vec2, Vec3, Vec4, CollisionRay, CollisionHandlerQueue, CollisionNode, BitMask32, Plane, Point3, TextNode, PointLight
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

from GameObject import GameObject
from gameObjects.TrapEnemy import TrapEnemy

import random, math

class Player(GameObject):
    def __init__(self):
        GameObject.__init__(
            self,
            Vec3(0, 0, 0),
            "assets/models/character/act_p3d_chan",
            {
                "idle" : "assets/models/character/a_p3d_chan_idle",
                "walk" : "assets/models/character/a_p3d_chan_run"
            },
            5,
            10,
            "player"
        )
        
        self.actor.getChild(0).setH(180)
        
        base.pusher.addCollider(self.collider, self.actor)
        base.cTrav.addCollider(self.collider, base.pusher)

        self.actor.loop("idle")
        
        self.ray = CollisionRay(0, 0, 0, 0, 1, 0)
        rayNode = CollisionNode("playerRay")
        rayNode.addSolid(self.ray)
        self.rayNodePath = render.attachNewNode(rayNode)
        self.rayQueue = CollisionHandlerQueue()

        base.cTrav.addCollider(self.rayNodePath, self.rayQueue)

        self.damagePerSecond = -5.0
        
        mask = BitMask32()
        mask.setBit(1)
        
        self.collider.node().setIntoCollideMask(mask)

        mask = BitMask32()
        mask.setBit(1)

        self.collider.node().setFromCollideMask(mask)

        mask = BitMask32()

        mask.setBit(2)
        rayNode.setFromCollideMask(mask)

        mask = BitMask32()
        rayNode.setIntoCollideMask(mask)
        
        self.beamModel = loader.loadModel("assets/models/BambooLaser/bambooLaser")
        self.beamModel.reparentTo(self.actor)
        self.beamModel.setZ(1.5)
        self.beamModel.setLightOff()
        self.beamModel.hide()
        
        self.lastMousePos = Vec2(0, 0)
        
        self.groundPlane = Plane(Vec3(0, 0, 1), Vec3(0, 0, 0))
        
        self.yVector = Vec2(0, 1)
        
        self.score = 0

        self.scoreUI = OnscreenText(
            text = "0",
            pos = (-1.3, 0.825),
            mayChange = True,
            align = TextNode.ALeft
        )

        self.healthIcons = []
        for i in range(self.maxHealth):
            icon = OnscreenImage(
                image = "assets/UI/health.png",
                pos = (-1.275 + i*0.075, 0, 0.95),
                scale = 0.04
            )
            icon.setTransparency(True)
            self.healthIcons.append(icon)
        
        self.beamHitModel = loader.loadModel("assets/models/BambooLaser/bambooLaserHit")
        self.beamHitModel.reparentTo(render)
        self.beamHitModel.setZ(1.5)
        self.beamHitModel.setLightOff()
        self.beamHitModel.hide()

        self.beamHitPulseRate = 0.15
        self.beamHitTimer = 0

        self.beamHitLight = PointLight("beamHitLight")
        self.beamHitLight.setColor(Vec4(0.1, 1.0, 0.2, 1))
        self.beamHitLight.setAttenuation((1.0, 0.1, 0.5))
        self.beamHitLightNodePath = render.attachNewNode(self.beamHitLight)
        
        self.damageTakenModel = loader.loadModel("assets/models/BambooLaser/playerHit")
        self.damageTakenModel.setLightOff()
        self.damageTakenModel.setZ(1.0)
        self.damageTakenModel.reparentTo(self.actor)
        self.damageTakenModel.hide()

        self.damageTakenModelTimer = 0
        self.damageTakenModelDuration = 0.15
        
    def update(self, keys, dt):
        GameObject.update(self, dt)
        
        self.walking = False
        
        #movement
        if keys["up"]:
            self.walking = True
            self.velocity.addY(self.acceleration*dt)
        if keys["down"]:
            self.walking = True
            self.velocity.addY(-self.acceleration*dt)
        if keys["left"]:
            self.walking = True
            self.velocity.addX(-self.acceleration*dt)
        if keys["right"]:
            self.walking = True
            self.velocity.addX(self.acceleration*dt)

        #animation
        if self.walking:
            standControl = self.actor.getAnimControl("idle")
            if standControl.isPlaying():
                standControl.stop()

            walkControl = self.actor.getAnimControl("walk")
            if not walkControl.isPlaying():
                self.actor.loop("walk")
        else:
            standControl = self.actor.getAnimControl("idle")
            if not standControl.isPlaying():
                self.actor.stop("walk")
                self.actor.loop("idle")

        if keys["shoot"]:
            if self.rayQueue.getNumEntries() > 0:
                scoredHit = False

                self.rayQueue.sortEntries()
                rayHit = self.rayQueue.getEntry(0)
                hitPos = rayHit.getSurfacePoint(render)

                hitNodePath = rayHit.getIntoNodePath()
                if hitNodePath.hasPythonTag("owner"):
                    hitObject = hitNodePath.getPythonTag("owner")
                    if not isinstance(hitObject, TrapEnemy):
                        hitObject.alterHealth(self.damagePerSecond*dt)
                        scoredHit = True

                beamLength = (hitPos - self.actor.getPos()).length()
                self.beamModel.setSy(beamLength)

                self.beamModel.show()

                if scoredHit:
                    self.beamHitModel.show()

                    self.beamHitModel.setPos(hitPos)
                    self.beamHitLightNodePath.setPos(hitPos + Vec3(0, 0, 0.5))

                    if not render.hasLight(self.beamHitLightNodePath):
                        render.setLight(self.beamHitLightNodePath)
                else:
                    if render.hasLight(self.beamHitLightNodePath):
                        render.clearLight(self.beamHitLightNodePath)

                    self.beamHitModel.hide()
        else:
            if render.hasLight(self.beamHitLightNodePath):
                render.clearLight(self.beamHitLightNodePath)

            self.beamModel.hide()

            self.beamHitModel.hide()
            
        mouseWatcher = base.mouseWatcherNode
        if mouseWatcher.hasMouse():
            mousePos = mouseWatcher.getMouse()
        else:
            mousePos = self.lastMousePos
            
        mousePos3D = Point3()
        nearPoint = Point3()
        farPoint = Point3()
        
        base.camLens.extrude(mousePos, nearPoint, farPoint)
        
        self.groundPlane.intersectsLine(
            mousePos3D,
            render.getRelativePoint(base.camera, nearPoint),
            render.getRelativePoint(base.camera, farPoint)
        )
        
        firingVector = Vec3(mousePos3D - self.actor.getPos())
        firingVector2D = firingVector.getXy()
        firingVector2D.normalize()
        firingVector.normalize()

        heading = self.yVector.signedAngleDeg(firingVector2D)

        self.actor.setH(heading)

        if firingVector.length() > 0.001:
            self.ray.setOrigin(self.actor.getPos())
            self.ray.setDirection(firingVector)

        self.lastMousePos = mousePos
        
        self.beamHitTimer -= dt
        
        if self.beamHitTimer <= 0:
            self.beamHitTimer = self.beamHitPulseRate
            self.beamHitModel.setH(random.uniform(0.0, 360.0))
            
        self.beamHitModel.setScale(math.sin(self.beamHitTimer*3.142/self.beamHitPulseRate)*0.4 + 0.9)
        
        if self.damageTakenModelTimer > 0:
            self.damageTakenModelTimer -= dt
            self.damageTakenModel.setScale(2.0 - self.damageTakenModelTimer/self.damageTakenModelDuration)
            if self.damageTakenModelTimer <= 0:
                self.damageTakenModel.hide()
                        
    def cleanup(self):
        base.cTrav.removeCollider(self.rayNodePath)

        GameObject.cleanup(self)
        
        self.scoreUI.removeNode()

        for icon in self.healthIcons:
            icon.removeNode()
            
        self.beamHitModel.removeNode()

        render.clearLight(self.beamHitLightNodePath)
        self.beamHitLightNodePath.removeNode()
        
    def updateScore(self):
        self.scoreUI.setText(str(self.score))

    def alterHealth(self, dHealth):
        GameObject.alterHealth(self, dHealth)

        self.updateHealthUI()
        
        self.damageTakenModel.show()
        self.damageTakenModel.setH(random.uniform(0.0, 360.0))
        self.damageTakenModelTimer = self.damageTakenModelDuration

    def updateHealthUI(self):
        for index, icon in enumerate(self.healthIcons):
            if index < self.health:
                icon.show()
            else:
                icon.hide()