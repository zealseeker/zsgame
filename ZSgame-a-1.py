import pygame
from pygame.locals import *
import math,random,sys, thread

# Initialize the game
pygame.init()
width, height = 640, 480
screen=pygame.display.set_mode((width, height))
pygame.mixer.init()
grass = pygame.image.load("resources/images/grass.png")
gameover = pygame.image.load("resources/images/gameover.png")
youwin = pygame.image.load("resources/images/youwin.png")
healthbar1 = pygame.image.load("resources/images/healthbar.png")
health1    = pygame.image.load("resources/images/health.png")
healthbar2 = pygame.transform.scale(healthbar1,(40,4)).convert()
health2    = pygame.transform.scale(health1,(1,3)).convert()
clock = pygame.time.Clock()
#Load audio
hit = pygame.mixer.Sound("resources/audio/explode.wav")
enemy = pygame.mixer.Sound("resources/audio/enemy.wav")
shoot = pygame.mixer.Sound("resources/audio/shoot.wav")
hit.set_volume(0.05)
enemy.set_volume(0.05)
shoot.set_volume(0.05)
pygame.mixer.music.load('resources/audio/moonlight.wav')
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(0.25)

#define classes
class Arrow:
    def __init__(self,sub,obj):
        self.obj = obj
        self.x   = sub.x + 32
        self.y   = sub.y + 15
        self.bullet = pygame.image.load("resources/images/bullet.png")
        self.rect = self.bullet.get_rect()
        self.rect.topleft = [self.x,self.y]
        global enemy
        enemy.play()

    def move(self):
        x,y = self.rect.center
        self.angle = math.atan2(self.obj.y+15- y ,self.obj.x+32- x)
        velx = math.cos(self.angle)*10
        vely = math.sin(self.angle)*10
        self.x+=velx
        self.y+=vely

    def judgeDmage(self):
        rect = self.obj.getRect()
        if (rect.colliderect(self.rect)):
            return True
        return False

class Defence:
    def __init__(self,pos):
        self.dmg = 10
        self.sp  = 1
        self.health = 10
        self.x   = pos[0]
        self.y   = pos[1]
        self.ar  = 150 # attack range
        self.img = pygame.image.load("resources/images/dude.png")
        self.arrows = []

    def attack(self,obj):
        self.arrows.append(Arrow(self,obj))

    def controlArrow(self,screen,lock):
        #draw arrows
        for i,arrow in enumerate(self.arrows):
            arrow.move()
            if arrow.judgeDmage():
                arrow.obj.health -= self.dmg
                self.arrows.remove(arrow)
            arrow1 = pygame.transform.rotate(arrow.bullet, 360-arrow.angle*57.29)
            arrow.rect = arrow1.get_rect()
            arrow.rect.topleft = [arrow.x,arrow.y]
            screen.blit(arrow1,arrow.rect.topleft)
        lock.release()

    def draw(self,screen):
        #draw defence
        screen.blit(self.img,(self.x,self.y))
        

    def controlArrow_and_draw(self,screen,lock):
        for i,arrow in enumerate(self.arrows):
            arrow.move()
            if arrow.judgeDmage():
                arrow.obj.health -= self.dmg
                self.arrows.remove(arrow)
            arrow1 = pygame.transform.rotate(arrow.bullet, 360-arrow.angle*57.29)
            arrow.rect = arrow1.get_rect()
            arrow.rect.topleft = [arrow.x,arrow.y]
            screen.blit(arrow1,arrow.rect.topleft)
        screen.blit(self.img,(self.x,self.y))
        print random.random()
        lock.release()

    def findEnemy(self,badguys):
        def distance(x1,y1,x2,y2):
            return math.sqrt((x1-x2)**2+(y1-y2)**2)
        for badguy in badguys:
            if distance(self.x,self.y,badguy.x,badguy.y) < self.ar:
                self.attack(badguy)
                return True
        return False
    
class Badguy:
    sp = 1
    health = 30
    def __init__(self,pos):
        global health2, healthbar2
        self.health = Badguy.health
        self.reward = 1
        self.x   = pos[0]
        self.y   = pos[1]
        self.sp  = Badguy.sp
        self.health_per = 40./self.health
        self.healthbar = healthbar2
        self.health2 = health2
        self.img = pygame.image.load("resources/images/badguy.png")
        
    def moveOut(self):
        self.x += self.sp
        if self.x<-64 or self.x >640 or self.y<-64 or self.y>480:
            return True
        return False
        
    def draw(self,screen):
        
        screen.blit(self.img,(self.x,self.y))
        screen.blit(self.healthbar,(self.x+5,self.y-8))
        for i in range(int(self.health*self.health_per)):
            screen.blit(self.health2,(i+self.x+5,self.y-7))

    def getRect(self):
        rect=pygame.Rect(self.img.get_rect())
        rect.left=self.x
        rect.top=self.y
        return rect

#main
running = 1
exitcode = 0
defences = [Defence([50,120])]
badguys = []
badtimer = 100
badtimer1 =0
golds = 100
lostValue  = 15
badguyRemain = 200
while running:
    badtimer-=1
    locks=[]
    clock.tick()
    screen.fill(0)
    for x in range(width/grass.get_width()+1):
        for y in range(height/grass.get_height()+1):
            screen.blit(grass,(x*100,y*100))

    #Defence
    for defence in defences:
        lock=thread.allocate_lock()
        lock.acquire()
        locks.append(lock)
        thread.start_new_thread(defence.controlArrow,(screen,lock))
        #defence.controlArrow(screen,lock)
        defence.draw(screen)
        

    #Add badbuy
    if badtimer==0 and badguyRemain > 0:
        badguys.append(Badguy([0, random.randint(50,430)]))
        badguyRemain -= 1
        badtimer=100
        badtimer=100-(badtimer1*2)
        if badtimer1>=35:
            badtimer1=35
        else:
            badtimer1+=5

    #Game difficulty
    if badguyRemain <= 80:
        Badguy.sp =3
    elif badguyRemain <= 150:
        Badguy.sp = 2
    if badguyRemain <= 30:
        Badguy.health = 50
        
    #Defence Active
    if badtimer % 20 == 0:
        for defence in defences:
            defence.findEnemy(badguys)
        
    for badguy in badguys:
        #check whether badguy dead
        if badguy.moveOut():
            badguys.remove(badguy)
            lostValue-=1
            hit.play()
        elif badguy.health <= 0 :
            badguys.remove(badguy)
            golds += badguy.reward
        badguy.draw(screen)

    #Draw golds,lost,remain
    font = pygame.font.Font('resources/font/arial.ttf', 14)
    goldtext   =   font.render('golds:     %d' % golds,True,(0,0,0))
    losttext   =   font.render('lost:     %d' % lostValue,True,(255,0,0))
    remaintext =   font.render('remains:     %d' % badguyRemain,True,(0,0,0))
    fpstext    =   font.render('fps: %d'%clock.get_fps(),True,(0,0,0))
    textRect = goldtext.get_rect()
    textRect.topright = [635,5]
    screen.blit(goldtext,textRect)
    textRect = losttext.get_rect()
    textRect.topright = [635,20]
    screen.blit(losttext,textRect)
    textRect = remaintext.get_rect()
    textRect.topright = [635,35]
    screen.blit(remaintext,textRect)
    textRect = fpstext.get_rect()
    textRect.topleft = [5,5]
    screen.blit(fpstext,textRect)
                                 

        
    pygame.display.flip()    
    for event in pygame.event.get():
        # check if the event is the X button 
        if event.type==pygame.QUIT:
            # if it is quit the game
            pygame.quit()
            sys.exit(0)
        if event.type==pygame.MOUSEBUTTONDOWN:
            if golds > 50:
                shoot.play()
                position = pygame.mouse.get_pos()
                #check whether upgrade or create a new
                IsUpgrade = False
                for defence in defences:
                    rect = defence.img.get_rect()
                    rect.topleft = [defence.x,defence.y]
                    rect1 = defence.img.get_rect()
                    rect1.topleft = position
                    if rect.colliderect(rect1) and defence.dmg==10:
                        defence.img = pygame.image.load("resources/images/dude2.png")
                        defence.dmg = 20
                        defence.ar = 300
                        defence.y  -=6
                        IsUpgrade = True
                        golds -=50
                        break
                if IsUpgrade == False:
                    newp = [position[0]-32,position[1]-26]
                    defences.append(Defence(newp))
                    golds -=50
            
    for lock in locks:
        while lock.locked():
            pass
    #Win/Lose check
    if lostValue <=0 :
        running = 0
        exitcode = 0 #0->lose
    if badguyRemain <= 0 and len(badguys) ==0:
        running = 0
        exitcode = 1 #1->win

if exitcode==0:
    screen.blit(gameover, (0,0))
else:
    screen.blit(youwin, (0,0))


while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
            
    pygame.display.flip()
