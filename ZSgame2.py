# Use new pygame engine: sge
from ZSgame2_init import *
import os,pygame

__version__ = "0.1"
DATA = os.path.join(os.path.abspath(os.path.dirname(__file__)),"resources","images")
game_in_progress = True

class Game(sge.dsp.Game):

    def event_step(self,time_passed,delta_mult):
        self.project_sprite(hud_sprite,0,self.width-100,0)

    def event_key_press(self,key,char):
        global game_in_progress
        if key == 'f8':
            sge.gfx.Sprite.from_screenshot().save('screenshot.jpg')
        elif key == 'f11':
            self.fullscreen = not self.fullscreen
        elif key == 'escape':
            self.event_close()
        elif key in ('p', 'enter'):
            if game_in_progress:
                self.pause()
            else:
                game_in_progress = True
                self.current_room.start()

    def event_close(self):
        self.end()

    def event_paused_key_press(self, key, char):
        if key == 'escape':
            # This allows the player to still exit while the game is
            # paused, rather than having to unpause first.
            self.event_close()
        else:
            self.unpause()

    def event_paused_close(self):
        # This allows the player to still exit while the game is paused,
        # rather than having to unpause first.
        self.event_close()

class Scene(sge.dsp.Room):
    def __init__(self,difficulty=0):
        super(Scene,self).__init__(background=background)

    def event_room_start(self):
        coord = zmap_info['start']
        Badguy.create(MAP_SCALE*coord[1],MAP_SCALE*coord[0],coord[2])
        for each in zmap_info['turn']:
            Barrier.create(MAP_SCALE*each[1],MAP_SCALE*each[0],each[2])

class Attackter(sge.dsp.Object):
    def hurt(self):
        pass

    def kill(self):
        pass

    def turn(self,direction):
        self.direction += direction
        self.turning_direction = direction
        print self.direction
        if self.direction > 4:
            self.direction = 1
        elif self.direction < 1:
            self.direction = 4
        if self.direction % 2 != 0:
            self.xvelocity = -1* self.speed*(self.direction-2)
            self.yvelocity = 0
        else :
            self.yvelocity = -1* self.speed*(self.direction-3)
            self.xvelocity = 0
        self.image_rotation+=10*direction
        self.alarms['rotate']=ROTATE_INTERVAL

    def event_alarm(self,alarm_id):
        if alarm_id == 'rotate':
            self.image_rotation+=10*self.turning_direction
            print self.image_rotation
            if self.image_rotation % 90 !=0:
                self.alarms['rotate']=ROTATE_INTERVAL

    def event_create(self):
        if self.direction % 2 != 0:
            self.xvelocity = -1* self.speed*(self.direction-2)
            self.yvelocity = 0
        else :
            self.yvelocity = -1* self.speed*(self.direction-3)
            self.xvelocity = 0

class Badguy(Attackter):
    health = 100
    speed = 2
    def __init__(self,x,y,direction):
        super(Badguy,self).__init__(x,y,sprite=badguy_sprite,
        checks_collisions=False)
        self.sprite.rotate(180)
        self.direction = direction

class Barrier(sge.dsp.Object):
    def __init__(self,x,y,b_type):
        super(Barrier,self).__init__(x,y)
        self.b_type = b_type

    def event_collision(self,other,xdirection,ydirection):
        if(isinstance(other,Attackter)):
            if self.b_type == MAP_RIGHT_DOWN:
                if other.direction == DIRECTION_RIGHT:
                    if other.x>self.x:
                        other.x = self.x
                        other.turn(TURN_RIGHT)
                if other.direction == DIRECTION_UP:
                    if other.y<self.y:
                        other.y = self.y
                        other.turn(TURN_LEFT)
            elif self.b_type == MAP_RIGHT_UP:
                if other.direction == DIRECTION_DOWN:
                    if other.y>self.y:
                        other.y = self.y
                        other.turn(TURN_RIGHT)
                if other.direction == DIRECTION_RIGHT:
                    if other.x>self.x:
                        other.x=self.x
                        other.turn(TURN_LEFT)
            elif self.b_type == MAP_LEFT_UP:
                if other.direction == DIRECTION_LEFT:
                    if other.x<self.x:
                        other.x=self.x
                        other.turn(TURN_RIGHT)
                if other.direction == DIRECTION_DOWN:
                    if other.y>self.y:
                        other.y=self.y
                        other.turn(TURN_LEFT)
            elif self.b_type == MAP_LEFT_DOWN:
                if other.direction == DIRECTION_LEFT:
                    if other.x<self.x:
                        other.x=self.x
                        other.turn(TURN_LEFT)
                if other.direction == DIRECTION_UP:
                    if other.y<self.y:
                        other.y=self.y
                        other.turn(TURN_RIGHT)

class Defence(sge.dsp.Object):
    def kill(self):
        pass

class Dude(Defence):
    def __init__(self,x,y):
        super(Dude,self).__init__(x,y,sprite=dude_sprite)

class Bullet(sge.dsp.Object):
    def attact(self):
        pass

class Arrow(Bullet):
    def __init__(self,x,y):
        super(Arrow,self).__init__(x,y,sprite=arrow_sprite)

Game(width=640,height=480,scale=1,fps=60,window_text='Zealseeker Game {}'.format(__version__),
     window_icon=None)
# load sprites
badguy_sprite = sge.gfx.Sprite('badguy',DATA,fps=10,origin_x=32,origin_y=15)
dudu_sprite   = sge.gfx.Sprite('dude',DATA,origin_x=32,origin_y=23)
arrow_sprite  = sge.gfx.Sprite('bullet',DATA,origin_x=21,origin_y=5)
hud_sprite    = sge.gfx.Sprite(width=320, height=120, origin_x=160, origin_y=0)
import ZSgame_map
# load background
zmap_info = {'turn':[]}
layers = [sge.gfx.BackgroundLayer(sge.gfx.Sprite('grass',DATA,transparent=False),0,0,-10000,repeat_down=True,repeat_right=True)]
ZSgame_map.addLayer(layers,zmap_info)
background = sge.gfx.Background(layers,sge.gfx.Color((85,170,255)))
sge.game.start_room = Scene()

if __name__ == '__main__':
    try:
        sge.game.start()
    finally:
        pass
