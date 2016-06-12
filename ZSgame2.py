# Use new pygame engine: sge
from ZSgame2_init import *
import os

__version__ = "0.1"
DATA = os.path.join(os.path.dirname(__file__),"resources","images")
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

class Attackter(sge.dsp.Object):
    def hurt(self):
        pass

    def kill(self):
        pass

    def event_collision(self):
        pass

    def turn(self,direction):
        self.direction += direction
        if self.direction > 4:
            self.direction = 1
        elif self.direction < 1:
            self.direction = 4

class Badguy(Attackter):
    health = 100
    xv = 2
    def __init__(self,x,y,direction):
        super(Badguy,self).__init__(x,y,sprite=badguy_sprite,xvelocity=self.xv,
        image_xscale=-1)
        self.direction = direction




Game(width=640,height=480,scale=1,fps=60,window_text='Zealseeker Game {}'.format(__version__),
     window_icon=None)
# load sprites
badguy_sprite = sge.gfx.Sprite('badguy',DATA,fps=10,origin_x=32,origin_y=15)
hud_sprite    = sge.gfx.Sprite(width=320, height=120, origin_x=160, origin_y=0)
import ZSgame_map
# load background
zmap_info = {}
layers = [sge.gfx.BackgroundLayer(sge.gfx.Sprite('grass',DATA,transparent=False),0,0,-10000,repeat_down=True,repeat_right=True)]
ZSgame_map.addLayer(layers,zmap_info)
background = sge.gfx.Background(layers,sge.gfx.Color((85,170,255)))
sge.game.start_room = Scene()

if __name__ == '__main__':
    try:
        sge.game.start()
    finally:
        pass
