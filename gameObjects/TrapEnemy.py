from panda3d.core import BitMask32

from GameObject import GameObject
from gameObjects.Enemy import Enemy

import math

class TrapEnemy(Enemy):
    def __init__(self, pos):
        Enemy.__init__(self, pos,
            "assets/models/SlidingTrap/trap",
            {
                "stand" : "assets/models/SlidingTrap/trap-stand",
                "walk" : "assets/models/SlidingTrap/trap-walk",
                },
            100.0,
            10.0,
            "trapEnemy"
        )

        base.pusher.addCollider(self.collider, self.actor)
        base.cTrav.addCollider(self.collider, base.pusher)

        self.moveInX = False

        self.moveDirection = 0

        # This will allow us to prevent multiple
        # collisions with the player during movement
        self.ignorePlayer = False
        
        mask = BitMask32()
        mask.setBit(2)
        mask.setBit(1)

        self.collider.node().setIntoCollideMask(mask)

        mask = BitMask32()
        mask.setBit(2)
        mask.setBit(1)

        self.collider.node().setFromCollideMask(mask)
        
    def runLogic(self, player, dt):
        if self.moveDirection != 0:
            self.walking = True
            if self.moveInX:
                self.velocity.addX(self.moveDirection*self.acceleration*dt)
            else:
                self.velocity.addY(self.moveDirection*self.acceleration*dt)
        else:
            self.walking = False
            diff = player.actor.getPos() - self.actor.getPos()
            if self.moveInX:
                detector = diff.y
                movement = diff.x
            else:
                detector = diff.x
                movement = diff.y

            if abs(detector) < 0.5:
                self.moveDirection = math.copysign(1, movement)

    def alterHealth(self, dHealth):
        pass