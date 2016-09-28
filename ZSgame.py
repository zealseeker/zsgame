# Use new pygame engine: sge
from ZSgame_init import *
import os,pygame,math

from player import *
__version__ = "0.1"

try:
    DATA = os.path.join(os.path.abspath(os.path.dirname(__file__)),"resources","images")
except NameError:
    import sys
    # to be complatible for py2exe
    DATA = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),"resources","images")
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
        elif key == 'p':
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
        self.deploying = None  # Whether some defence is deploying (fields will show)
        self.countDown = -1
        self.Islost = False

    def myevent_attacker_destroy(self,obj):
        self.attacker_alive -= 1
        self.check_win()

    def check_win(self):
        if self.attacker_alive == 0 and self.empty==True and self.processing:
            self.background.layers.append(sge.gfx.BackgroundLayer(sge.gfx.Sprite('youwin',DATA),0,0,10000))
            self.stop_process()
            self.countDown = 5
            self.alarms['next_custom']=sge.game.fps


    def lose(self):
        self.background.layers.append(sge.gfx.BackgroundLayer(sge.gfx.Sprite('gameover',DATA),0,0,10000))
        self.stop_process()
        self.Islost=True

    def stop_process(self):
        self.processing = False
        for obj in self.objects:
            obj.tangible = False
            obj.active   = False

    def event_room_start(self):
        for each in self.zmap_info['turn']:
            Barrier.create(*each)
        Barrier.create(self.zmap_info['end'][0],self.zmap_info['end'][1],MAP_END)
        self.player = Player()
        self.alarms['add_badguy']=1
        self.controlBar=ControlBar.create(self)
        music_bg.play()


    def event_key_press(self, key, char):
        if key=='enter' and self.Islost:
            Scene().start()
        pass

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
            AttackerDict[modelname].create(*coord,**kwargs)
            self.attackerPoint+=1
            if self.attackerPoint == len(self.attackers):
                self.empty = True
            else:
                self.alarms['add_badguy']=120



    def event_step(self,time_passed,delta_mult):

        if self.countDown >0:
            self.project_text(hud_font,str(self.countDown),WINDOW_WIDTH/2-10,WINDOW_HEIGHT/2-10,100,width=20,height=20)
        elif self.Islost:
            self.project_text(hud_font,'Input Enter to start again!',WINDOW_WIDTH/2-100,WINDOW_HEIGHT/2-10,100,width=200,height=20)


class Attacker(sge.dsp.Object):

    def __init__(self,x,y,direction,**kwargs):
        del kwargs['model']
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

    def hurt(self,obj,damage):
        self.health -= damage
        if self.health <= 0:
            sge.game.current_room.player.gold+=self.gold
            self.destroy()
            Float_gold.create(self.x,self.y,self.gold)
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
                    sge.game.current_room.player.life_hurt()
                    other.destroy()


class Magic(sge.dsp.Object):
    deployed = False
    attack_range = 150
    magic_dict = {}

    def __init__(self,*args,**kwarges):
        self.show_range=True
        self.magic_sprite = kwarges['sprite']
        self.deployed=False
        del kwarges['sprite']
        super(Magic,self).__init__(*args,**kwarges)

    def deploy(self):
        self.sprite = self.magic_sprite
        self.image_fps = self.sprite.fps
        #self.image_xscale=0.1
        #self.image_yscale=0.1
        self.deployed=True
        self.checks_collisions=True
        sge.game.current_room.deploying = None
        self.show_range = False
        for obj in sge.game.current_room.objects[:]:
            if isinstance(obj,Field):
                obj.destroy()

    def event_mouse_move(self,x,y):
        if not self.deployed:
            self.x = sge.game.mouse.x
            self.y = sge.game.mouse.y

    def event_mouse_button_press(self,button):

        if not self.deployed:
            if button=='left':
                self.deploy()
            elif button == 'right':
                self.destroy()
                sge.game.current_room.deploying=None
                for obj in sge.game.current_room.objects[:]:
                    if isinstance(obj,Field):
                        obj.destroy()
    def event_alarm(self,alarm_id):
        if alarm_id == 'kill':
            self.killed=False
            self.tangible=True
            self.alarms['pause']=5
        elif alarm_id == 'pause':
            self.tangible=False
            self.attacted=[]
            self.alarms['kill']=self.freq-5
        if alarm_id == 'destroy':
            self.destroy()

    def event_step(self,time_passed,delta_mult):
        if self.show_range:
            sge.game.current_room.project_circle(self.x,self.y,50,self.attack_range,fill=RANGE_COLOR,outline=RANGE_OUTLINE_COLOR)

    def event_animition_end(self):
        print '1'

class Leiyu(Magic):
    attack_range = 30
    gold = 10
    name = 'leiyu'
    freq = 48
    life_cycle = 180
    damage = 30
    killed = False

    def __init__(self,x,y):
        self.attacted = []
        super(Leiyu,self).__init__(x,y,51,sprite=magic_leiyu,tangible=False)
        super(Leiyu,self).magic_dict['leiyu']=Leiyu

    def deploy(self):
        self.alarms['kill']=20 #before the killing
        self.alarms['destroy']=self.life_cycle
        super(Leiyu,self).deploy()

    def event_collision(self,obj,xdirection,ydirection):
        if isinstance(obj,Attacker) and obj not in self.attacted:
            obj.hurt(self,self.damage)
            self.attacted.append(obj)

class MG_Cold(Magic):
    attack_range = 50
    gold = 10
    name = 'cold'
    freq = 10
    life_cycle = 180

    def __init__(self,x,y):
        self.attacted = []
        super(MG_Cold,self).__init__(x,y,51,sprite=magic_cold,tangible=False)
        super(MG_Cold,self).magic_dict['leiyu']=Leiyu

    def deploy(self):
        self.alarms['kill']=3 #before the killing
        self.alarms['destroy']=self.life_cycle
        super(MG_Cold,self).deploy()

    def event_collision(self,obj,xdirection,ydirection):
        self.killed=True
        if isinstance(obj,Attacker) and obj not in self.attacted:
            obj.hurt(self,5)
            self.attacted.append(obj)


class Defence(sge.dsp.Object):

    deployed=False
    attack_freq = 60
    attack_range = 150
    defence_dict = {}

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
        'now only consider size 1'
        #check avaiability of deploying
        zmap = sge.game.current_room.zmap_info['zmap']
        i = int(self.y // MAP_SCALE)
        j = int(self.x // MAP_SCALE)
        if zmap[i][j]==0 and sge.game.current_room.player.gold >= self.gold:
            #deploying
            self.image_alpha=255
            self.deployed = True
            self.searching_enemy = True
            self.x = j * MAP_SCALE + MAP_SCALE/2
            self.y = i * MAP_SCALE + MAP_SCALE/2
            sge.game.current_room.player.gold -= self.gold
            snd_dead.play()
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
        super(Dude,self).defence_dict['dude']=Dude

    def kill(self,obj):
        Arrow.create(self.x,self.y,obj)
        snd_shoot.play()

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
    damage = 20
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
                obj.hurt(self,self.damage)
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
        Skill.create(1,50,y,Dude)
        Skill.create(2,50,y,Leiyu)
        Skill.create(3,50,y,MG_Cold)

    def event_step(self,time_passed,delta_mult):
        hud_sprite.draw_clear()
        hud_sprite.draw_text(hud_font,'GOLD: '+str(sge.game.current_room.player.gold),0,0,color=sge.gfx.Color("white"))
        hud_sprite.draw_text(hud_font,'REMAIN:' +str(sge.game.current_room.attacker_alive),0,20,color=sge.gfx.Color('white'))
        hud_sprite.draw_text(hud_font,"LIFE:"+str(sge.game.current_room.player.life),0,40,color=sge.gfx.Color('white'))
        sge.game.project_sprite(hud_sprite,0,WINDOW_WIDTH-100,WINDOW_HEIGHT-80,60)

class Skill(sge.dsp.Object):
    skill_width = 50
    def __init__(self,skillid,left,height,origin,*args,**kwargs):
        '@param origin: the origin model(Defence or Magic)'
        x = left + self.skill_width * (skillid)
        y = height + 20
        self.Origin = origin
        self.skillid = skillid
        self.selected = False
        super(Skill,self).__init__(x,y,60,*args,sprite=skill_sprites[origin.name],tangible=False,**kwargs)
        self.sprite.draw_text(hud_font,str(skillid),self.skill_width-10,self.skill_width-20)

    def event_key_press(self,key, char):
        if key == str(self.skillid):
            if sge.game.current_room.deploying:
                sge.game.current_room.deploying.destroy()
                sge.game.current_room.deploying = None
            elif issubclass(self.Origin,Defence): 
                create_fields(sge.game.current_room.zmap_info['zmap'])
        if key == str(self.skillid) and sge.game.current_room.processing:
            sge.game.current_room.deploying = self.Origin.create(sge.game.mouse.x,sge.game.mouse.y)

    def event_mouse_move(self,x,y):
        x=sge.game.mouse.x
        y=sge.game.mouse.y
        if x > self.bbox_left and x < self.bbox_right and y > self.bbox_top and y < self.bbox_bottom:
            self.selected = True
        else:
            self.selected = False
    def event_mouse_button_press(self,button):
        if self.selected and button=='left':
            self.event_key_press(str(self.skillid),str(self.skillid))

    def event_step(self,time_passed, delta_mult):
        if self.selected:
            sge.game.current_room.project_sprite(selected_skill_sprite,0,self.x,self.y,100)

class Float_obj(sge.dsp.Object):

    def __init__(self,x,y,sprite):
        super(Float_obj,self).__init__(x,y,50,sprite=sprite,checks_collisions=False,tangible=False)

class Float_gold(Float_obj):
    'upward float of gold'
    def __init__(self,x,y,gold_value):
        sprite = sge.gfx.Sprite(width=80,height=20)
        sprite.draw_sprite(gold_sprite,0,0,0)
        sprite.draw_text(hud_font,str(gold_value),20,0)
        super(Float_gold,self).__init__(x,y,sprite)
        self.yvelocity = -1
        self.frame = 0

    def event_step(self,time_passed,delta_mult):

        if self.image_alpha <=10:
            self.destroy()
        elif self.frame>30:
            self.image_alpha -=10
        else:
            self.frame +=1

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
selected_skill_sprite = sge.gfx.Sprite('selected',DATA,width=50,height=50)
gold_sprite = sge.gfx.Sprite('gold',DATA,width=20,height=20)
magic_leiyu = sge.gfx.Sprite('magic_leiyu',DATA,width=50,height=80,fps=10,origin_x=25,origin_y=60,bbox_y=-20)
magic_cold = sge.gfx.Sprite('magic_cold',DATA,width=100,height=80,fps=12,origin_x=50,origin_y=50,bbox_y=-20)
skill_magic_leiyu = sge.gfx.Sprite('red_border',DATA)
skill_magic_leiyu.draw_sprite(sge.gfx.Sprite('magic_leiyu-4',DATA,width=47,height=47),0,0,0)
skill_magic_cold = sge.gfx.Sprite('red_border',DATA)
skill_magic_cold.draw_sprite(sge.gfx.Sprite('magic_cold-4',DATA,width=47,height=47),0,0,0)
skill_sprites = {'dude':dude_skill_sprite,'leiyu':skill_magic_leiyu,'cold':skill_magic_cold}

#load font
hud_font = sge.gfx.Font("Arial", size=18)

# load map
import ZSgame_map
field_sprites = ZSgame_map.field_sprites

# load sound
sound_root = os.path.join('resources','audio')
snd_shoot = sge.snd.Sound(os.path.join(sound_root,'shoot.wav'))
snd_dead  = sge.snd.Sound(os.path.join(sound_root,'explode.wav'))
music_bg  = sge.snd.Music(os.path.join(sound_root,'moonlight.wav'))


sge.game.start_room = Scene()

if __name__ == '__main__':
    try:
        sge.game.start()
    finally:
        pass
