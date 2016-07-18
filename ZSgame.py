# Use new pygame engine: sge
from ZSgame_init import *
import os,pygame,math

__version__ = "0.1"
DATA = os.path.join(os.path.abspath(os.path.dirname(__file__)),"resources","images")
game_in_progress = True

class Game(sge.dsp.Game):

    def event_step(self,time_passed,delta_mult):
        pass

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
    def __init__(self,custom_id=0):
        customs_pass = ZSgame_map.customs_pass[custom_id]
        self.zmap_info = {'turn':[],'attacker':customs_pass['attackers'],'zmap':customs_pass['zmap']}
        layers = [sge.gfx.BackgroundLayer(sge.gfx.Sprite('grass',DATA,transparent=False),0,0,-10000,repeat_down=True,repeat_right=True)]
        if not ZSgame_map.addLayer(layers,self.zmap_info):
            print 'map error'
            sge.game.end()
        background = sge.gfx.Background(layers,sge.gfx.Color((85,170,0)))
        super(Scene,self).__init__(background=background)
        self.attackers = self.zmap_info['attacker']
        self.attackerPoint = 0
        self.empty = False
        self.processing = True
        self.attacker_alive = len(self.attackers)
        self.gold = 100
        self.deploying = None  # Whether some defence is deploying (fields will show)
        self.countDown = -1

    def myevent_attacker_destroy(self,obj):
        self.attacker_alive -= 1
        self.check_win()

    def check_win(self):
        if self.attacker_alive == 0 and self.empty==True:
            self.background.layers.append(sge.gfx.BackgroundLayer(sge.gfx.Sprite('youwin',DATA),0,0,10000))
            self.stop_process()
            self.countDown = 5
            self.alarms['next_custom']=sge.game.fps


    def lose(self):
        self.background.layers.append(sge.gfx.BackgroundLayer(sge.gfx.Sprite('gameover',DATA),0,0,10000))
        self.stop_process()
        #TODO Give entrance to start again

    def stop_process(self):
        self.processing = False
        for obj in self.objects:
            obj.tangible = False
            obj.active   = False

    def event_room_start(self):
        for each in self.zmap_info['turn']:
            Barrier.create(*each)
        Barrier.create(self.zmap_info['end'][0],self.zmap_info['end'][1],MAP_END)
        self.alarms['add_badguy']=1
        self.controlBar=ControlBar.create(self)


    def event_key_press(self, key, char):
        if key in '123456':

            if self.deploying:
                self.deploying.destroy()
                self.deploying = None
            else:
                create_fields(self.zmap_info['zmap'])
        if key == '1' and self.processing:
            self.deploying = Dude.create(sge.game.mouse.x,sge.game.mouse.y)


    def event_alarm(self,alarm_id):
        if alarm_id == 'next_custom':
            if self.countDown == 1:
                Scene(1).start()
            else :
                self.countDown -= 1
                self.alarms['next_custom']=sge.game.fps
        if not self.processing:
            return False
        if alarm_id == 'add_badguy':
            coord = self.zmap_info['start']
            kwargs = self.attackers[self.attackerPoint]
            modelname = self.attackers[self.attackerPoint]['model']
            del kwargs['model']
            AttackerDict[modelname].create(*coord,**kwargs)
            self.attackerPoint+=1
            if self.attackerPoint == len(self.attackers):
                self.empty = True
            else:
                self.alarms['add_badguy']=120



    def event_step(self,time_passed,delta_mult):
        hud_sprite.draw_clear()
        hud_sprite.draw_text(hud_font,'GOLD: '+str(sge.game.current_room.gold),0,0,color=sge.gfx.Color("white"))
        hud_sprite.draw_text(hud_font,'REMAIN:' +str(sge.game.current_room.attacker_alive),0,20,color=sge.gfx.Color('white'))
        self.project_sprite(hud_sprite,0,WINDOW_WIDTH-100,WINDOW_HEIGHT-80,60)
        if self.countDown >0:
            self.project_text(hud_font,str(self.countDown),WINDOW_WIDTH/2-10,WINDOW_HEIGHT/2-10,100,width=20,height=20)


class Attacker(sge.dsp.Object):

    def __init__(self,x,y,direction,**kwargs):
        if 'health' in kwargs:
            self.max_health = kwargs['health']
            del kwargs['health']
        if 'speed'  in kwargs:
            self.speed = kwargs['speed']
            del kwargs['speed']
        if 'gold' in kwargs:
            self.gold = kwargs['gold']
            del kwargs['gold']
        i=x;j=y
        x=j*MAP_SCALE+MAP_SCALE/2
        y=i*MAP_SCALE+MAP_SCALE/2
        self.direction = direction
        self.health = self.max_health
        super(Attacker,self).__init__(x,y,**kwargs)
        self.healthBar = AttackerHealthBar.create(self)

    def hurt(self,obj,dmage):
        self.health -= dmage
        if self.health <= 0:
            sge.game.current_room.gold+=self.gold
            self.destroy()
            # TODO effects of getting golds
        else:
            self.healthBar.refresh(self.health)
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
    def event_destroy(self):
        sge.game.current_room.myevent_attacker_destroy(self)
        self.healthBar.destroy()

class Badguy(Attacker):
    health = 100
    speed = 2
    gold = 0
    def __init__(self,x,y,direction,**kwargs):
        self.max_health = self.health
        super(Badguy,self).__init__(x,y,direction,sprite=badguy_sprite,
        checks_collisions=False,**kwargs)
        self.image_rotation += 90*(self.direction-1)

class Barrier(sge.dsp.Object):
    def __init__(self,x,y,b_type):
        i=x;j=y
        x=j*MAP_SCALE+MAP_SCALE/2
        y=i*MAP_SCALE+MAP_SCALE/2
        super(Barrier,self).__init__(x,y)
        self.b_type = b_type

    def event_collision(self,other,xdirection,ydirection):
        if(isinstance(other,Attacker)):
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
            elif self.b_type == MAP_END:
                judge_dic = {DIRECTION_LEFT: other.x < self.x,
                 DIRECTION_RIGHT: other.x > self.x,
                 DIRECTION_UP: other.y > self.y,
                 DIRECTION_DOWN: other.y < self.y
                 }
                if judge_dic[other.direction]:
                    other.destroy()
                    sge.game.current_room.lose()

class Defence(sge.dsp.Object):

    deployed=False
    attack_freq = 60
    attack_range = 150

    def __init__(self,*args,**kwarges):
        kwarges['image_alpha']=50
        self.show_range = True
        self.searching_enemy = False
        super(Defence,self).__init__(*args,**kwarges)

    def kill(self,obj):
        self.killing_obj = obj
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
        zmap = sge.game.current_room.zmap_info['zmap']
        i = int(self.y // MAP_SCALE)
        j = int(self.x // MAP_SCALE)
        if zmap[i][j]==0 and sge.game.current_room.gold >= self.gold:
            self.image_alpha=255
            self.deployed = True
            self.searching_enemy = True
            self.x = j * MAP_SCALE + MAP_SCALE/2
            self.y = i * MAP_SCALE + MAP_SCALE/2
            sge.game.current_room.gold -= self.gold
            # hidden FIELDS
            sge.game.current_room.deploying = None
            self.show_range=False
            for obj in sge.game.current_room.objects[:]:
                if isinstance(obj,Field):
                    obj.destroy()



    def event_mouse_move(self,x,y):
        if not self.deployed :
            map_x = sge.game.mouse.x // MAP_SCALE
            map_y = sge.game.mouse.y // MAP_SCALE
            self.x = (map_x if map_x < MAP_WIDTH else MAP_WIDTH-1) * MAP_SCALE + MAP_SCALE/2
            self.y = (map_y if map_y < MAP_HEIGHT else MAP_HEIGHT-1) * MAP_SCALE + MAP_SCALE/2
    def event_mouse_button_press(self,button):
        if not self.deployed :
            if button == 'left':
                self.deploy()
            elif button == 'right':
                self.destroy()
                sge.game.current_room.deploying = None
                # destroy Fields
                for obj in sge.game.current_room.objects[:]:
                    if isinstance(obj,Field):
                        obj.destroy()

    def event_alarm(self,alarm_id):
        if alarm_id == 'kill':
            self.searching_enemy = True


    def event_step(self, time_passed, delta_mult):
        if self.show_range:
            sge.game.current_room.project_circle(self.x,self.y,50,self.attack_range,fill=RANGE_COLOR,outline=RANGE_OUTLINE_COLOR)
        if self.searching_enemy:
            if self.search_enemy():
                self.searching_enemy = False
                self.alarms['kill']= self.attack_freq

class Dude(Defence):
    attack_freq = 60
    attack_rage = 40
    gold = 50
    name = 'dude'
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
    dmage = 20
    def __init__(self,x,y,obj):
        super(Arrow,self).__init__(obj,x,y,9,sprite=arrow_sprite)
        self.attacted = []

    def attact(self,obj):
        self.angle = math.atan2(self.obj.y-self.y,self.obj.x-self.x)
        self.image_rotation = self.angle*57.29
        self.xvelocity=math.cos(self.angle)*self.speed
        self.yvelocity=math.sin(self.angle)*self.speed

    def event_collision(self,obj,xdirection,ydirection):
        if isinstance(obj,Attacker):
            if obj not in self.attacted:
                obj.hurt(self,self.dmage)
                self.attacted.append(obj)

    def event_step(self,time_passed, delta_mult):
        if self.bbox_bottom < 0 or self.bbox_top > sge.game.current_room.height \
            or self.bbox_right < 0 or self.bbox_left > sge.game.current_room.width:
            self.destroy()

class HealthBar(sge.dsp.Object):
    def __init__(self,to,*args,**kwargs):
        self.bindObject = to
        self.max_health = to.max_health
        kwargs['tangible']=False
        super(HealthBar,self).__init__(self.bindObject.x,self.bindObject.bbox_top - 20,10,*args,**kwargs)

    def event_step(self,time_passed,delta_mult):
        self.x = self.bindObject.x
        self.y = self.bindObject.bbox_top - 10

class AttackerHealthBar(HealthBar):
    def __init__(self,to):
        super(AttackerHealthBar,self).__init__(to)
        self.max_width = 48  # 50 - 2 (border)
        self.max_height = 6  # 8 - 2
        self.refresh(self.bindObject.max_health)

    def refresh(self,health):
        temp_sprite = AttackerHealthBar_sprite.copy()
        width = int(self.max_width * self.bindObject.health / self.bindObject.max_health // 1)
        temp_sprite.draw_rectangle(1,1,width,self.max_height,fill=sge.gfx.Color('red'))
        self.sprite = temp_sprite

class Field(sge.dsp.Object):
    def __init__(self,x,y,f_type):
        super(Field,self).__init__(x,y,10,sprite=field_sprites[f_type],
        checks_collisions=False,tangible=False)


class ControlBar(sge.dsp.Object):
    def __init__(self,room):
        y = sge.game.height -controlBar_sprite.height
        super(ControlBar,self).__init__(0,y,50,sprite=controlBar_sprite)
        Skill.create(0,50,y,Dude)


class Skill(sge.dsp.Object):
    skill_width = 50
    def __init__(self,skillid,left,height,Defencer,*args,**kwargs):
        x = left + self.skill_width * (skillid)
        y = height + 20
        super(Skill,self).__init__(x,y,60,*args,sprite=skill_sprites[Defencer.name],**kwargs)
        self.sprite.draw_text(hud_font,str(skillid+1),self.skill_width-10,self.skill_width-20)

    def event_key_press(self,key, char):
        #TODO put the key_press function of room here
        pass


def create_fields(zmap):
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

Game(width=WINDOW_WIDTH,height=WINDOW_HEIGHT,scale=1,fps=60,delta=True,window_text='Zealseeker Game {}'.format(__version__),
     window_icon=None)
# state model
AttackerDict = {'Badguy':Badguy}
# load sprites
controlBar_sprite = sge.gfx.Sprite(width=WINDOW_WIDTH,height=100)
controlBar_sprite.draw_rectangle(0,0,controlBar_sprite.width,controlBar_sprite.height,fill=sge.gfx.Color('green'))
badguy_sprite = sge.gfx.Sprite('badguy',DATA,fps=10,origin_x=32,origin_y=15)
badguy_sprite.rotate(180)
dude_sprite   = sge.gfx.Sprite('dude',DATA,origin_x=32,origin_y=23)
dude_skill_sprite = sge.gfx.Sprite('red_border',DATA)
dude_skill_sprite.draw_sprite(sge.gfx.Sprite('dude',DATA,width=47,height=47),0,0,0)
arrow_sprite  = sge.gfx.Sprite('bullet',DATA,origin_x=21,origin_y=5)
AttackerHealthBar_sprite = sge.gfx.Sprite(width=50,height=8,origin_x=25,origin_y=4)
red_border_sprite = sge.gfx.Sprite('red_border',DATA,origin_x=25,origin_y=25)
AttackerHealthBar_sprite.draw_rectangle(0,0,50,8,outline=sge.gfx.Color('black'),fill=sge.gfx.Color('green'))
hud_sprite  = sge.gfx.Sprite(width=100, height=80)
skill_sprites = {'dude':dude_skill_sprite}
#load font
hud_font = sge.gfx.Font("Arial", size=18)

# load map
import ZSgame_map
field_sprites = ZSgame_map.field_sprites

# load background


sge.game.start_room = Scene()

if __name__ == '__main__':
    try:
        sge.game.start()
    finally:
        pass
