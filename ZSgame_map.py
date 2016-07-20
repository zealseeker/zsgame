# -*- coding:utf-8 -*-
'''
Constants of the tags in map:
1 :  start point
2 ： end point
3 :  -   HORIZONTAL
4 :  ┐   Right_DOWN
5 :  ┘   RIGHT_UP
6 : ┌    LEFT_DOWN
7 : └    LEFT_UP
8 : |    VERTICAL
'''
from ZSgame2_init import *

# set customs_pass information
customs_pass = []
# For each customs pass, use two Lists to define the map which are:
zmap =[]
attackers = []

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
    attackers.append({'model':'Badguy','health':100,'speed':1.5,'gold':8})
for i in range(10):
    attackers.append({'model':'Badguy','health':110,'speed':3,'gold':2})


#attackers = [{'model':'Badguy','health':1,'speed':5}]    # This is for test

customs_pass.append({'zmap':zmap,'attackers':attackers})

# the second custom:
zmap=[]
attackers = []
maps = '''
0    0    0    0    0    0    0    0    0    0    0    0
0    6    3    4    0    0    0    6    3    3    4    0
0    8    0    8    0    0    0    8    0    0    8    0
0    8    0    8    0    0    0    8    0    0    8    0
0    8    0    8    0    0    0    8    0    0    8    0
0    8    0    8    0    0    0    8    0    0    8    0
0    1    0    7    3    3    3    5    0    0    2    0
0    0    0    0    0    0    0    0    0    0    0    0
'''.strip().split('\n')
zmap = [[int(x)for x in line.split('   ')]for line in maps]
for i in range(10):
    attackers.append({'model':'Badguy','health':100,'speed':1.5,'gold':8})
for i in range(10):
    attackers.append({'model':'Badguy','health':150,'speed':2,'gold':2})

customs_pass.append({'zmap':zmap,'attackers':attackers})


def addLayer(layer,zmap_info):
    zmap = zmap_info['zmap']

    for i in range(MAP_HEIGHT):
        for j in range(MAP_WIDTH):

            if zmap[i][j]!=0:
                layer.append(sge.gfx.BackgroundLayer(map_sprites[zmap[i][j]-1],50*j,50*i,-10000))
            if zmap[i][j]==MAP_START:
                # ensure the direction
                direction = 0
                if i!=0 and zmap[i-1][j]==MAP_VERTICLE:
                    direction = DIRECTION_UP
                elif i!=MAP_HEIGHT-1 and zmap[i+1][j]==MAP_VERTICLE:
                    direction = DIRECTION_DOWN
                elif j!=0 and zmap[i][j-1]==MAP_HORIZON:
                    direction = DIRECTION_LEFT
                elif j!=MAP_WIDTH-1 and zmap[i][j+1]==MAP_HORIZON:
                    direction = DIRECTION_RIGHT
                else:
                    return False
                zmap_info['start']=(i,j,direction)
            elif zmap[i][j]==MAP_END:
                zmap_info['end'] = (i,j)
            elif zmap[i][j]>3 and zmap[i][j]<8:
                zmap_info['turn'].append((i,j,zmap[i][j]))
    return True

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
