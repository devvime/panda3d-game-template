from panda3d.core import Vec3

from GameObject import GameObject

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