from panda3d.core import Vec2, BitMask32, CollisionNode, CollisionSegment, CollisionHandlerQueue

from GameObject import GameObject

import random

class Enemy(GameObject):
    def __init__(self, pos, modelName, modelAnims, maxHealth, maxSpeed, colliderName):
        GameObject.__init__(self, pos, modelName, modelAnims, maxHealth, maxSpeed, colliderName)
        
        self.scoreValue = 1
        
    def update(self, player, dt):
        GameObject.update(self, dt)
        self.runLogic(player, dt)
        
        if self.walking:
            walkingControl = self.actor.getAnimControl("walk")
            if not walkingControl.isPlaying():
                self.actor.loop("walk")
        else:
            spawnControl = self.actor.getAnimControl("spawn")
            if spawnControl is None or not spawnControl.isPlaying():
                attackControl = self.actor.getAnimControl("attack")
                if attackControl is None or not attackControl.isPlaying():
                    standControl = self.actor.getAnimControl("stand")
                    if not standControl.isPlaying():
                        self.actor.loop("stand")

    def runLogic(self, player, dt):
        pass

class WalkingEnemy(Enemy):
    def __init__(self, pos):
        Enemy.__init__(
            self, 
            pos,
            "assets/models/enemy/simpleEnemy",
            {
            "stand" : "assets/models/enemy/simpleEnemy-stand",
            "walk" : "assets/models/enemy/simpleEnemy-walk",
            "attack" : "assets/models/enemy/simpleEnemy-attack",
            "die" : "assets/models/enemy/simpleEnemy-die",
            "spawn" : "assets/models/enemy/simpleEnemy-spawn"
            },
            3.0,
            7.0,
            "walkingEnemy"
        )
        
        self.attackDistance = 0.75
        self.acceleration = 100.0
        self.yVector = Vec2(0, 1)
        
        mask = BitMask32()
        mask.setBit(2)

        self.collider.node().setIntoCollideMask(mask)
        
        self.attackSegment = CollisionSegment(0, 0, 0, 1, 0, 0)

        segmentNode = CollisionNode("enemyAttackSegment")
        segmentNode.addSolid(self.attackSegment)
        
        mask = BitMask32()
        mask.setBit(1)

        segmentNode.setFromCollideMask(mask)

        mask = BitMask32()

        segmentNode.setIntoCollideMask(mask)

        self.attackSegmentNodePath = render.attachNewNode(segmentNode)
        self.segmentQueue = CollisionHandlerQueue()

        base.cTrav.addCollider(self.attackSegmentNodePath, self.segmentQueue)
        
        self.attackDamage = -1
        
        self.attackDelay = 0.3
        self.attackDelayTimer = 0
        self.attackWaitTimer = 0
        
    def runLogic(self, player, dt):
        vectorToPlayer = player.actor.getPos() - self.actor.getPos()

        vectorToPlayer2D = vectorToPlayer.getXy()
        distanceToPlayer = vectorToPlayer2D.length()

        vectorToPlayer2D.normalize()

        heading = self.yVector.signedAngleDeg(vectorToPlayer2D)

        if distanceToPlayer > self.attackDistance*0.9:
            attackControl = self.actor.getAnimControl("attack")
            if not attackControl.isPlaying():
                self.walking = True
                vectorToPlayer.setZ(0)
                vectorToPlayer.normalize()
                self.velocity += vectorToPlayer*self.acceleration*dt
                self.attackWaitTimer = 0.2
                self.attackDelayTimer = 0
        else:
            self.walking = False
            self.velocity.set(0, 0, 0)

            if self.attackDelayTimer > 0:
                self.attackDelayTimer -= dt
                if self.attackDelayTimer <= 0:
                    if self.segmentQueue.getNumEntries() > 0:
                        self.segmentQueue.sortEntries()
                        segmentHit = self.segmentQueue.getEntry(0)

                        hitNodePath = segmentHit.getIntoNodePath()
                        if hitNodePath.hasPythonTag("owner"):
                            hitObject = hitNodePath.getPythonTag("owner")
                            hitObject.alterHealth(self.attackDamage)
                            self.attackWaitTimer = 1.0
            elif self.attackWaitTimer > 0:
                self.attackWaitTimer -= dt
                if self.attackWaitTimer <= 0:
                    self.attackWaitTimer = random.uniform(0.5, 0.7)
                    self.attackDelayTimer = self.attackDelay
                    self.actor.play("attack")

        self.actor.setH(heading)
        
        self.attackSegment.setPointA(self.actor.getPos())
        self.attackSegment.setPointB(self.actor.getPos() + self.actor.getQuat().getForward()*self.attackDistance)
        
    def cleanup(self):
        base.cTrav.removeCollider(self.attackSegmentNodePath)
        self.attackSegmentNodePath.removeNode()

        GameObject.cleanup(self)
        
    def alterHealth(self, dHealth):
        Enemy.alterHealth(self, dHealth)
        self.updateHealthVisual()

    def updateHealthVisual(self):
        perc = self.health/self.maxHealth
        if perc < 0:
            perc = 0
        
        self.actor.setColorScale(perc, perc, perc, 1)