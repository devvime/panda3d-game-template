from panda3d.core import Vec2

from GameObject import GameObject

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
        
    def runLogic(self, player, dt):
        vectorToPlayer = player.actor.getPos() - self.actor.getPos()

        vectorToPlayer2D = vectorToPlayer.getXy()
        distanceToPlayer = vectorToPlayer2D.length()

        vectorToPlayer2D.normalize()

        heading = self.yVector.signedAngleDeg(vectorToPlayer2D)

        if distanceToPlayer > self.attackDistance*0.9:
            self.walking = True
            vectorToPlayer.setZ(0)
            vectorToPlayer.normalize()
            self.velocity += vectorToPlayer*self.acceleration*dt
        else:
            self.walking = False
            self.velocity.set(0, 0, 0)

        self.actor.setH(heading)