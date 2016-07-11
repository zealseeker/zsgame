# -*- coding:utf-8 -*-
'''
1 :  start
2 ： end
3 :  -
4 :  ┐
5 :  ┘
6 : ┌
7 : └
8 : |
'''
from ZSgame2_init import *

# set map information
zmap =[]
attacker = []

# set map texture
for i in range(20):
    zmap.append([0]*20)
zmap[1][1]=1
zmap[1][10]=4
zmap[4][10]=5
for i in range(2,10):
    zmap[1][i]=3
    zmap[4][i]=3
zmap[2][10]=8
zmap[3][10]=8
zmap[4][1]=7
zmap[3][1]=8
zmap[2][1]=6
for i in range(2,9):
    zmap[2][i]=3
zmap[2][9]=2

# define attackers
for i in range(10):
    attacker.append({'model':'Badguy','health':100,'speed':1.5})
for i in range(10):
    attacker.append({'model':'Badguy','health':110,'speed':2})


def addLayer(layer,zmap_info):
    for i in range(20):
        for j in range(20):

            if zmap[i][j]!=0:
                layer.append(sge.gfx.BackgroundLayer(map_sprites[zmap[i][j]-1],50*j,50*i,-10000))
            if zmap[i][j]==MAP_START:
                zmap_info['start']=(i,j,DIRECTION_RIGHT)
            elif zmap[i][j]==MAP_END:
                zmap_info['end'] = (i,j)
            elif zmap[i][j]>3 and zmap[i][j]<8:
                zmap_info['turn'].append((i,j,zmap[i][j]))

### Sprites
map_sprites=[]
field_sprites = []
# start
map_sprite=sge.gfx.Sprite(width=50,height=50)
map_sprite.draw_rectangle(20,20,10,10,fill=sge.gfx.Color('white'))
map_sprites.append(map_sprite)
# end
map_sprites.append(map_sprite)
#  -
map_sprite=sge.gfx.Sprite(width=50,height=50)
map_sprite.draw_rectangle(0,20,50,10,fill=sge.gfx.Color('black'))
map_sprites.append(map_sprite)

# ┐
map_sprite=sge.gfx.Sprite(width=50,height=50)
map_sprite.draw_rectangle(0,20,30,10,fill=sge.gfx.Color('black'))
map_sprite.draw_rectangle(20,20,10,30,fill=sge.gfx.Color('black'))
map_sprites.append(map_sprite)
# ┘
map_sprite=sge.gfx.Sprite(width=50,height=50)
map_sprite.draw_rectangle(0,20,30,10,fill=sge.gfx.Color('black'))
map_sprite.draw_rectangle(20,0,10,30,fill=sge.gfx.Color('black'))
map_sprites.append(map_sprite)
# ┌
map_sprite=sge.gfx.Sprite(width=50,height=50)
map_sprite.draw_rectangle(20,20,30,10,fill=sge.gfx.Color('black'))
map_sprite.draw_rectangle(20,20,10,30,fill=sge.gfx.Color('black'))
map_sprites.append(map_sprite)
# └
map_sprite=sge.gfx.Sprite(width=50,height=50)
map_sprite.draw_rectangle(20,20,30,10,fill=sge.gfx.Color('black'))
map_sprite.draw_rectangle(20,0,10,30,fill=sge.gfx.Color('black'))
map_sprites.append(map_sprite)
# |
map_sprite=sge.gfx.Sprite(width=50,height=50)
map_sprite.draw_rectangle(20,0,10,50,fill=sge.gfx.Color('black'))
map_sprites.append(map_sprite)

# FIELDS - used to control the range of the field of avaiable field when deploying.

P_FIELD_UP = [[0,0,MAP_SCALE,0]]
P_FIELD_DOWN = [[0,MAP_SCALE-1,MAP_SCALE,MAP_SCALE-1]]
P_FIELD_LEFT = [[0,0,0,MAP_SCALE]]
P_FIELD_RIGHT = [[MAP_SCALE-1,0,MAP_SCALE-1,MAP_SCALE]]
P_FIELDS = [[],P_FIELD_UP,P_FIELD_LEFT,P_FIELD_LEFT+P_FIELD_UP,P_FIELD_DOWN,
P_FIELD_UP+P_FIELD_DOWN,P_FIELD_LEFT+P_FIELD_DOWN,P_FIELD_UP+P_FIELD_DOWN+P_FIELD_LEFT,P_FIELD_RIGHT,
P_FIELD_RIGHT+P_FIELD_UP,P_FIELD_LEFT+P_FIELD_RIGHT,P_FIELD_UP+P_FIELD_LEFT+P_FIELD_RIGHT,P_FIELD_RIGHT+P_FIELD_DOWN,
P_FIELD_UP+P_FIELD_DOWN+P_FIELD_RIGHT,P_FIELD_DOWN+P_FIELD_LEFT+P_FIELD_RIGHT,P_FIELD_UP+P_FIELD_DOWN+P_FIELD_LEFT+P_FIELD_RIGHT]
for p_field in P_FIELDS:
    field_sprite=sge.gfx.Sprite(width=MAP_SCALE,height=MAP_SCALE,origin_x=0,origin_y=0)
    for edge in p_field:
        field_sprite.draw_line(edge[0],edge[1],edge[2],edge[3],FIELD_OUTLINE_COLOR)
    field_sprite.draw_rectangle(0,0,MAP_SCALE,MAP_SCALE,fill=FIELD_COLOR)
    field_sprites.append(field_sprite)
