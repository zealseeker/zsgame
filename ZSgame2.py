# Use new pygame engine: sge
from ZSgame2_init import *
import os,pygame,math

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
        for each in zmap_info['turn']:
            Barrier.create(*each)
        self.alarms['add_badguy']=1

    def event_key_press(self, key, char):
        if key == '1':
            Dude.create(sge.game.mouse.x,sge.game.mouse.y)
            create_fields()

    def event_alarm(self,alarm_id):
        if alarm_id == 'add_badguy':
            coord = zmap_info['start']
            Badguy.create(*coord)
            self.alarms['add_badguy']=120



class Attackter(sge.dsp.Object):
    health = 1
    speed = 0
    def __init__(self,x,y,direction,**kwargs):
        i=x;j=y
        x=j*MAP_SCALE+MAP_SCALE/2
        y=i*MAP_SCALE+MAP_SCALE/2
        self.direction = direction
        super(Attackter,self).__init__(x,y,**kwargs)
    def hurt(self,obj,dmage):
        self.health -= dmage
        print 'I am hurted, current health:',self.health
        if self.health <= 0:
            self.destroy()
        return True

    def kill(self):
        pass

    def turn(self,direction):  #only consider 4 directions
        self.direction += direction
        self.turning_direction = direction
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

    def set_speed(self,speed):
        self.speed = speed
        self.turn(0)


    def event_alarm(self,alarm_id):
        if alarm_id == 'rotate':
            self.image_rotation+=10*self.turning_direction
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

        super(Badguy,self).__init__(x,y,direction,sprite=badguy_sprite,
        checks_collisions=False)

class Barrier(sge.dsp.Object):
    def __init__(self,x,y,b_type):
        i=x;j=y
        x=j*MAP_SCALE+MAP_SCALE/2
        y=i*MAP_SCALE+MAP_SCALE/2
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

    deployed=False
    attack_freq = 60
    attack_range = 150

    def __init__(self,*args,**kwarges):
        kwarges['image_alpha']=50
        super(Defence,self).__init__(*args,**kwarges)

    def kill(self,obj):

        return True

    def search_enemy(self):
        for obj in sge.game.current_room.objects[:]:
            if isinstance(obj,Badguy):
                if distance(self.x,self.y,obj.x,obj.y) < self.attack_range:

                    self.kill(obj)
                    return True
        return False

    def deploy(self):
        # now only consider size 1
        i = int(self.y // MAP_SCALE)
        j = int(self.x // MAP_SCALE)
        if zmap[i][j]==0:
            self.image_alpha=255
            self.deployed = True
            self.alarms['kill']= self.attack_freq
            self.x = j * MAP_SCALE + MAP_SCALE/2
            self.y = i * MAP_SCALE + MAP_SCALE/2
            # hidden FIELDS
            for obj in sge.game.current_room.objects[:]:
                if isinstance(obj,Field):
                    obj.destroy()


    def event_mouse_move(self,x,y):
        if not self.deployed :
            self.x = sge.game.mouse.x // MAP_SCALE * MAP_SCALE + MAP_SCALE/2
            self.y = sge.game.mouse.y // MAP_SCALE * MAP_SCALE + MAP_SCALE/2
    def event_mouse_button_press(self,button):
        if not self.deployed :
            if button == 'left':
                self.deploy()
            elif button == 'right':
                self.destroy()

    def event_alarm(self,alarm_id):
        if alarm_id == 'kill':
            self.search_enemy()
            self.alarms['kill']= self.attack_freq

class Dude(Defence):
    attack_freq = 60
    attack_rage = 40
    def __init__(self,x,y):
        super(Dude,self).__init__(x,y,sprite=dude_sprite,checks_collisions=False)
    def kill(self,obj):
        Arrow.create(self.x,self.y,obj)

class Bullet(sge.dsp.Object):
    def __init__(self,obj,x,y,z=0,**kwargs):
        super(Bullet,self).__init__(x,y,z,**kwargs)
        self.obj = obj

    def attact(self):
        pass

    def event_create(self):
        self.attact(self.obj)

class Arrow(Bullet):
    speed = 10
    dmage = 30
    def __init__(self,x,y,obj):
        super(Arrow,self).__init__(obj,x,y,9,sprite=arrow_sprite)
        self.attacted = []

    def attact(self,obj):
        self.angle = math.atan2(self.obj.y-self.y,self.obj.x-self.x)
        self.image_rotation = self.angle*57.29
        self.xvelocity=math.cos(self.angle)*self.speed
        self.yvelocity=math.sin(self.angle)*self.speed

    def event_collision(self,obj,xdirection,ydirection):
        if isinstance(obj,Attackter):
            if obj not in self.attacted:
                obj.hurt(self,self.dmage)
                self.attacted.append(obj)

    def event_step(self,time_passed, delta_mult):
        if self.bbox_bottom < 0 or self.bbox_top > sge.game.current_room.height \
            or self.bbox_right < 0 or self.bbox_left > sge.game.current_room.width:
            self.destroy()

class Field(sge.dsp.Object):
    def __init__(self,x,y,f_type):
        super(Field,self).__init__(x,y,10,sprite=field_sprites[f_type],
        checks_collisions=False,tangible=False)

def create_fields():
    for i,row in enumerate(zmap):
        for j,col in enumerate(row):
            if col != 0:
                bit = 0
                if i==0 or zmap[i-1][j]==0:
                    bit+=1
                if i==MAP_HEIGHT-1 or zmap[i+1][j]==0:
                    bit+=4
                if j==0 or zmap[i][j-1]==0:
                    bit+=2
                if j==MAP_WIDTH-1 or zmap[i][j+1]==0:
                    bit+=8
                Field.create(MAP_SCALE*j,MAP_SCALE*i,bit)

def distance(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)

Game(width=640,height=480,scale=1,fps=60,window_text='Zealseeker Game {}'.format(__version__),
     window_icon=None)
# load sprites
badguy_sprite = sge.gfx.Sprite('badguy',DATA,fps=10,origin_x=32,origin_y=15)
badguy_sprite.rotate(180)
dude_sprite   = sge.gfx.Sprite('dude',DATA,origin_x=32,origin_y=23)
arrow_sprite  = sge.gfx.Sprite('bullet',DATA,origin_x=21,origin_y=5)
hud_sprite    = sge.gfx.Sprite(width=320, height=120, origin_x=160, origin_y=0)

import ZSgame_map
field_sprites = ZSgame_map.field_sprites
zmap = ZSgame_map.zmap
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
