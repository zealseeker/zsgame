from ZSgame_init import *

'''
Put all information about the play into the module
'''



class Player():
    def __init__(self):
        #currently the life and default gold cannot be set
        #we will change it in the next version
        #TODO make it dependent by map
        self.gold = 100
        self.life = 5

    def life_hurt(self):
        self.life -= 1
        if self.life <=0:
            sge.game.current_room.lose()
