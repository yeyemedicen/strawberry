import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from itertools import cycle
import pygame as pg
import random
from numpy import linspace, gradient, arctan, pi
from scipy.interpolate import interp1d
import pygame.freetype
import ruamel.yaml as yaml

#
# Strawberry Battle Field Game
#

from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_RETURN,
    K_c,
    K_m,
    K_r,
    K_i,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
)

def CreateTrajectory(coordsA,coordsB, get_gradient = False):
    ''' 
        Arrow trajectory from A to B
    '''

    A0x = min([coordsB[0], coordsA[0]])
    A0y = min([coordsB[1], coordsA[1]])
    B0x = abs(coordsB[0] - coordsA[0])
    B0y = abs(coordsB[1] - coordsA[1])
    alpha = [0.15,0.65]
    beta = [0.5,-0.1]

    if coordsB[1]>coordsA[1]:
        beta = [-0.2,-0.1]

    if coordsB[0]<coordsA[0]:
        if coordsB[1]>coordsA[1]:
            beta = [-0.1,-0.85]
        else:
            beta = [-0.1,0.1]

    x_aux1 = A0x + alpha[0]*B0x
    x_aux2 = A0x + alpha[1]*B0x
    y_aux1 = A0y + beta[0]*B0y
    y_aux2 = A0y + beta[1]*B0y
    xdata = [coordsA[0], x_aux1, x_aux2, coordsB[0]]
    ydata = [coordsA[1], y_aux1, y_aux2, coordsB[1]]
    xtraj = linspace(min([coordsB[0], coordsA[0]]),max([coordsB[0], coordsA[0]]),100)
    f_cont = interp1d(xdata,ydata,kind='cubic')

    if coordsB[0]<coordsA[0]:
        xtraj = xtraj[::-1]

    ytraj = f_cont(xtraj)

    if get_gradient:
        dx = abs(xtraj[1] - xtraj[0])
        dtraj = gradient(ytraj,dx)
        return ytraj, xtraj, dtraj
    else:
        return ytraj, xtraj

def ChangeSprite(rect_frames, rect_size0 , sheet , pos, final_size, index):
    rect = pg.Rect(rect_frames[index])
    surf = pg.Surface(rect_size0 ,pg.SRCALPHA)
    surf.blit(sheet, (0, 0), rect)
    
    rect = surf.get_rect(center=(pos[0],pos[1]))
    surf = pg.transform.scale(surf, (final_size[0], final_size[1]))

    return surf, rect

def DamageCalculation(unit_name, damage):
    ''' 
        return the damage value according to unit and attack type
    '''
    damage_value = 0
    critical = ''

    if unit_name == 'Archer':
            
        x = random.randint(damage[0],damage[1])
        g = random.randint(0,100)
        # Calculation of damage. For the moment all attacks are the same here
        # Low-Damage attack
        if g < 20:
            x = int(x*0.5)
        elif g > 90:
            # Critical hit. Reported
            x = 2*x
            critical = 'critical'
        else:
            # Normal damage
            pass    

        damage_value = x

    return damage_value , critical

def DistanceBetween(unitA,unitB):
    
    xA = unitA.rect.centerx
    yA = unitA.rect.centery

    xB = unitB.rect.centerx
    yB = unitB.rect.centery
    
    return ((xB-xA)**2 + (yB - yA)**2)**(0.5)

def DisplayResources(Players_list):
    for Player_ in Players_list:
        resources_str = 'Food={i}/Wood={j}/Rock={k}'.format(i=Player_.food,j=Player_.wood,k=Player_.rock)
        text, _ = GAME_FONT.render(resources_str, (0, 0, 0) , size=12)
        if Player_.name == 'Player A':
            SCREEN.blit(text, (SCREEN_WIDTH*0.01,SCREEN_HEIGHT*0.97))
        elif Player_.name == 'Player B':
            SCREEN.blit(text, (SCREEN_WIDTH*0.76,SCREEN_HEIGHT*0.01))

def DisplayDamage(coords,damage):
    yoffset = -50
    xoffset = -10
    if damage[1] == 'critical':
        damage_text, _ = GAME_FONT.render(str(damage[0]), (255,102,102) , size=14)
    else:
        damage_text, _ = GAME_FONT.render(str(damage[0]), (204, 204, 0) , size=12)

    SCREEN.blit(damage_text, (coords[0]+xoffset,coords[1]+yoffset))
    pg.display.flip()
    pg.time.delay(500)
    SCREEN.fill(SCREEN_COLOR)

def DisplayInfo(unit, SCREEN, number_images, info_mode=False):
    # Canvas

    if info_mode:
        name = 'info01_ss'
        info_sheet , rect_frames = ReadSpriteSheet(main_dir + '/data/objects/info/' + name + '.png' , [2,3] , number_images)
        if unit.name == 'Archer':
            ind = -(-number_images*unit.resource//unit.full_resource)
            rect = pg.Rect(rect_frames[6-ind])
        else:
            rect = pg.Rect(rect_frames[0])
        #info_surf = pg.Surface(rect.size).convert_alpha()
        info_surf = pg.Surface(rect.size,pg.SRCALPHA)
        info_surf.blit(info_sheet, (0, 0), rect)
        info_surf.set_colorkey((0,0,0), RLEACCEL)
    else:
        if unit.IsMoving:
            name = 'info04'
        elif unit.IsAttacking:
            name = 'info05'
        else:
            name = 'info03'
        info_surf = pg.image.load(main_dir + '/data/objects/info/' + name + '.png').convert_alpha()
    
    size = info_surf.get_size()
    x_offset = 82
    y_offset = 5
    
    scale_factor = 0.7
    info_rect = info_surf.get_rect()
    info_rect.x = unit.rect.x + x_offset
    info_rect.y = unit.rect.y + y_offset
    info_surf = pg.transform.scale(info_surf,(int(size[0]*scale_factor),int(size[1]*scale_factor) ))
    SCREEN.blit(info_surf,info_rect)
    size_info = info_surf.get_size()

    if info_mode:
        # Health info
        if unit.name == 'Archer':
            hp_text, _ = GAME_FONT.render(str(unit.hp) + '/' + str(unit.full_hp), (0, 0, 0) , size=12)
            SCREEN.blit(hp_text,(unit.rect.x + 130 ,unit.rect.y+20))
    else:
        # actions info
        ac_text01, _ = GAME_FONT.render('Move', (0, 0, 0) , size=12)
        ac_text02, _ = GAME_FONT.render('Attack', (0, 0, 0) , size=12)
        Movex = info_rect.x + size_info[0]*0.2
        Movey = info_rect.y + size_info[1]*(0.44-0.25)
        Attackx = info_rect.x + size_info[0]*0.2
        Attacky = info_rect.y + size_info[1]*(0.44+0.25)
        SCREEN.blit(ac_text01,(Movex, Movey))
        SCREEN.blit(ac_text02,(Attackx, Attacky))
        unit.ActionBar_buttoms['Move'] = [Movex, Movey, size_info[0],size_info[1]*0.5]
        unit.ActionBar_buttoms['Attack'] = [Attackx, Attacky, size_info[0],size_info[1]*0.5]
        
        
    # Name info
    name_text, _ = GAME_FONT.render(unit.name, (0, 0, 0) , size=18)
    size_unit = unit.surf.get_size()
    SCREEN.blit(name_text, (unit.rect.x - size_unit[0]*0.2,unit.rect.y - size_unit[1]*0.28))

def ActionBar_IsClick(mouse_pos, unit):
    '''
         if there is a click in the Action Bar buttoms
    '''

    xoffset = 40
    yoffset = 8
    
    isclick = False

    B_move = unit.ActionBar_buttoms['Move']
    
    B_move_rx = (B_move[0] + B_move[2]*0.5 - (B_move[0] - B_move[2]*0.5) -6)*0.5
    B_move_x0 =  B_move[0]

    B_move_ry = (B_move[1] + B_move[3]*0.5 - (B_move[1] - B_move[3]*0.5) + 6 )*0.5
    B_move_y0 =  B_move[1]

    B_attack_y0 =  unit.ActionBar_buttoms['Attack'][1]

    if abs(mouse_pos[0] - (B_move_x0 + xoffset)) < B_move_rx :
        if abs(mouse_pos[1] - B_move_y0 ) < B_move_ry :
            unit.IsMoving = True
            isclick = True
            return isclick
    

    if abs(mouse_pos[0] - (B_move_x0 + xoffset)) < B_move_rx :
        if abs(mouse_pos[1] - (B_attack_y0 + yoffset)) < B_move_ry :
            unit.IsAttacking = True
            isclick = True
            return isclick

def ReadSpriteSheet(path_to_ss, RC_tup , number_images):
    
    sheet = pg.image.load(path_to_ss).convert_alpha()
    rect_frames = []
    image_count = 0
    size_full = sheet.get_size()
    sprite_width = int(size_full[0]/RC_tup[0])
    sprite_height = int(size_full[1]/RC_tup[1])

    for j in range(RC_tup[1]):
        for k in range(RC_tup[0]):
            rect_frames.append(( sprite_width*k , sprite_height*j, sprite_width , sprite_height ))
            image_count +=1
            if image_count == number_images:
                break

    return sheet , rect_frames
    
def MovingLoop(Player, unit, MovingUnit, ActionBars, WaitingEnd, pressed_keys):
    '''
        Moving loop using the player and the unit
    '''

    Logger.info([Player.name + ' is moving...', 1 ])
    pg.mouse.set_cursor(pg.cursors.broken_x)
    MovingUnit['on'] = True

    if pressed_keys[K_r]:
        # Display Unit's range of movement
        pg.draw.circle(SCREEN,color=(255,102,102),center=(unit.rect.centerx,unit.rect.centery),radius=unit.mov_range,width=2)
    if pressed_keys[K_c]:
        # Cancel the Movement
        Logger.info([Player.name + ' turn', 1])
        unit.IsMoving = False
        unit.DisplayActionBar = False
        ActionBars = False
        pg.mouse.set_cursor(pg.cursors.arrow)
        MovingUnit['on'] = False
        MovingUnit['coords'] = []
    if MovingUnit['coords']:
        # the unit will try to move
        IsMoved , msg = unit.Move(MovingUnit['coords'])
        if IsMoved:
            unit.IsMoving = False
            Player.NumberOfActions -= 1
            Player.diamonds.sprites()[Player.NumberOfActions].surf = Player.diamond0_img
            Logger.info([Player.name + ' had moved' , 1], holdtime = 2)
            # Checking InHome condition
            if DistanceBetween(unit,Player.Home) < 130:
                unit.InHome = True
            else:
                unit.InHome = False
            if Player.NumberOfActions == 0:
                WaitingEnd = True
            unit.HadMoved += 1
            unit.DisplayActionBar = False
            ActionBars = False
            pg.mouse.set_cursor(pg.cursors.arrow)
            MovingUnit['on'] = False
            MovingUnit['coords'] = []
        else:
            if msg == 'range':
                Logger.info(['Movement longer than Unit\'s range ' , 1], holdtime = 2)
                MovingUnit['coords'] = []
                
            elif msg == 'resource':
                pg.mouse.set_cursor(pg.cursors.arrow)
                unit.IsMoving = False
                Logger.info(['I am tired ... I need some rest! ' , 1], holdtime = 2)
                ActionBars = False
                MovingUnit['on'] = False
                MovingUnit['coords'] = []

        
    return Player, ActionBars, WaitingEnd

def AttackingLoop(Player, unit, AttackingUnit, ActionBars, WaitingEnd, pressed_keys):
    '''
        Attacking loop using the player and the unit
    '''

    Logger.info([Player.name + ' is attacking...' , 1])
    pg.mouse.set_cursor(pg.cursors.broken_x)
    AttackingUnit['on'] = True

    if pressed_keys[K_r]:
        # Display Unit's range of movement
        for attack in unit.attacks:
            #pg.draw.circle(SCREEN,color=(102,178,255),center=(unit.rect.centerx,unit.rect.centery),radius=unit.range_a[0],width=1)
            pg.draw.circle(SCREEN,color=(250,102,102),center=(unit.rect.centerx,unit.rect.centery),
                         radius=attack['range'],width=1)
        
    if pressed_keys[K_c]:
        # Cancel the Attack
        Logger.info([Player.name + ' turn', 1])
        unit.IsAttacking = False
        unit.DisplayActionBar = False
        ActionBars = False
        pg.mouse.set_cursor(pg.cursors.arrow)
        AttackingUnit['on'] = False
        AttackingUnit['target'] = []

    if unit.InHome:
        # Cancel the Attack
        Logger.info(['I cannot fight here!' , 1], holdtime=2)
        unit.IsAttacking = False
        unit.DisplayActionBar = False
        ActionBars = False
        pg.mouse.set_cursor(pg.cursors.arrow)
        AttackingUnit['on'] = False
        AttackingUnit['target'] = []

    if AttackingUnit['target']:
        # the unit will try to attack
        IsAttack , msg = unit.Attack(AttackingUnit['target'])
        if IsAttack:
            unit.IsAttacking = False
            Player.NumberOfActions -= 1
            Player.diamonds.sprites()[Player.NumberOfActions].surf = Player.diamond0_img

            if AttackingUnit['unit']:
                DisplayDamage(AttackingUnit['target'],msg)
                AttackingUnit['unit'].hp -= msg[0]
                if AttackingUnit['unit'].hp < 0:
                    AttackingUnit['unit'].Died()

                if msg[1] == 'critical':
                    Logger.info(['Critical hit!', 1], holdtime = 2)

            if Player.NumberOfActions == 0:
                WaitingEnd = True
                        
            unit.HadAttacked += 1
            unit.DisplayActionBar = False
            ActionBars = False
            pg.mouse.set_cursor(pg.cursors.arrow)
            AttackingUnit['on'] = False
            AttackingUnit['target'] = []
            AttackingUnit['unit'] = []
        else:
            if msg == 'range':
                Logger.info(['The target is too far away!' , 1], holdtime=2)
                AttackingUnit['target'] = []
                
            elif msg == 'resource':
                pg.mouse.set_cursor(pg.cursors.arrow)
                unit.IsAttacking = False
                Logger.info(['I am tired ... need some rest! ' , 1], holdtime = 2)
                ActionBars = False
                AttackingUnit['on'] = False
                AttackingUnit['target'] = []
            elif msg == 'accuracy':
                pg.mouse.set_cursor(pg.cursors.arrow)
                Player.NumberOfActions -= 1
                Player.diamonds.sprites()[Player.NumberOfActions].surf = Player.diamond0_img
                if Player.NumberOfActions == 0:
                    WaitingEnd = True
                unit.HadAttacked = True
                unit.IsAttacking = False
                Logger.info(['The attack failed... ' , 1], holdtime = 2)
                ActionBars = False
                AttackingUnit['on'] = False
                AttackingUnit['target'] = []
            

        
    return Player, ActionBars, WaitingEnd

class Player():
    def __init__(self , name ):

        self.name = name
        self.food = 25
        self.wood = 25
        self.rock = 10
        self.MaxActions = 5
        self.TotalActions = 1
        self.NumberOfActions = 1
        self.Unites = []
        self.UnitsGroup = pg.sprite.Group()
        self.Home = None

        if name == 'Player A':
            diamond_path = main_dir + '/data/objects/diamond01.png'
            self.diamond_height = SCREEN_HEIGHT*0.978
        elif name == 'Player B':
            diamond_path = main_dir + '/data/objects/diamond02.png'
            #self.diamond_height = SCREEN_HEIGHT*0.018
            self.diamond_height = SCREEN_HEIGHT*0.978

        self.diamond0_img  = pg.image.load(main_dir + '/data/objects/diamond00.png').convert_alpha()
        self.diamond_img = pg.image.load(diamond_path).convert_alpha()
        self.diamonds = []

    def DisplayDiamonds(self):
        if not self.diamonds:
            x0 = SCREEN_WIDTH*0.38
            self.diamonds = pg.sprite.Group()
            for k in range(self.TotalActions):
                xk = x0 + 30*k
                rect = self.diamond_img.get_rect(center=(xk,self.diamond_height))
                d = pg.sprite.Sprite()
                d.surf = self.diamond_img
                d.rect = rect
                d.name = 'diamond'
                self.diamonds.add(d)
            
            for d in self.diamonds.sprites():
                ALL_SPRITES.add(d)
        else:
            pass

class Unit(pg.sprite.Sprite):

    def __init__(self , name , pos, player_name):
        super(Unit, self).__init__()


        self.data = units_dct[name]
        self.name = name
        self.pos = pos

        if 'A' in player_name:
            self.type = self.data['types'][0]
        else:
            self.type = self.data['types'][1]

        
        # Image
        self.scale_factor = self.data['Image']['scale_factor']
        self.number_of_sprites = self.data['Image']['number_of_sprites']
        self.movement_sprites = [self.data['Image']['movement_sprites']['right'],
                                     self.data['Image']['movement_sprites']['left']]
        self.RC_tup = self.data['Image']['RowColumn_tup']


        # Parameters
        self.mov_range = self.data['Parameters']['mov_range']        
        self.full_hp = self.data['Parameters']['full_hp']
        self.hp = self.full_hp
        self.full_resource = self.data['Parameters']['full_resource']
        self.resource_name = self.data['Parameters']['resource_name']
        self.resource_drain = self.data['Parameters']['resource_drain']
        self.resource = self.full_resource
        self.speed = self.data['Parameters']['speed']

        self.attacks_types = [at for at in self.data['Parameters']['attack_types']]
        self.attacks = []

        for attack_type in self.attacks_types:
            attack_dct = self.data['Parameters']['attack_types'][attack_type]
            for attack in attack_dct:
                self.attacks.append({
                    'name': attack,
                    'range': attack_dct[attack]['range'],
                    'damage': attack_dct[attack]['damage'],
                    'accuracy': attack_dct[attack]['accuracy'],
                    'type': attack_type,
                    })
        
        
        self.path_to_ss = main_dir + self.data['path'] + self.name + self.type + '_ss.png'
        self.sheet , self.rect_frames = ReadSpriteSheet(self.path_to_ss , self.RC_tup , self.number_of_sprites)

        # Sprite
        self.rect_ind = 0
        self.rect = pg.Rect(self.rect_frames[self.rect_ind])
        self.rect_size0 = self.rect.size
        self.surf = pg.Surface(self.rect_size0, pg.SRCALPHA)
        self.surf.blit(self.sheet, (0, 0), self.rect)

        self.rect = self.surf.get_rect(center=(self.pos[0],self.pos[1]))
        self.surf = pg.transform.scale(self.surf, (int(self.rect_size0[0]*self.scale_factor), int(self.rect_size0[1]*self.scale_factor)))
        self.size = self.surf.get_size()
        
        # Info related
        self.DisplayActionBar = False
        self.ActionBar_buttoms = {'Move': [] , 'Attack': []}
        self.InHome = False
        self.IsMoving = False
        self.IsAttacking = False
        self.HadMoved = 0
        self.HadAttacked = 0
 
    def Move(self, coords):

        distance = ((coords[0] - self.rect.centerx)**2 + (coords[1] - self.rect.centery)**2)**(0.5)

        if self.resource-self.resource_drain <= 0:
            return False , 'resource'

        if distance > self.mov_range:
            # displacement higher than unit range!
            return False , 'range'
        else:
            displacement_x = int(coords[0]) - self.rect.centerx
            displacement_y = int(coords[1]) - self.rect.centery
            
            displacement_x_sign = 0
            sprite_chain = []

            if displacement_x > 0:
                displacement_x_sign = 1
                for k in range(1,self.movement_sprites[0]):
                    sprite_chain.append(k)
                sprite_chain_c = cycle(sprite_chain)

            elif displacement_x<0:
                displacement_x_sign = -1
                for k in range(self.movement_sprites[0]+1,sum(self.movement_sprites)):
                    sprite_chain.append(k)
                sprite_chain_c = cycle(sprite_chain)


            displacement_y_sign = 0
            if displacement_y<0:
                displacement_y_sign = -1
            elif displacement_y > 0:
                displacement_y_sign = 1
            

            sprite_ind = next(sprite_chain_c)

            for k in range(int(abs(displacement_x)/self.speed)):
                self.rect.move_ip(self.speed*displacement_x_sign,0)
                self.pos[0] += self.speed*displacement_x_sign # updating inner center coordinates
                
                #self.ChangeSprite(sprite_ind)
                self.surf , self.rect = ChangeSprite(self.rect_frames, self.rect_size0 , self.sheet , 
                             self.pos, self.size, sprite_ind)

                SCREEN.fill(SCREEN_COLOR)
                pg.draw.line(SCREEN,color=(0,0,0),start_pos=(0,LINE_UP),end_pos=(SCREEN_WIDTH,LINE_UP),width=2)
                pg.draw.line(SCREEN,color=(0,0,0),start_pos=(0,LINE_DOWN),end_pos=(SCREEN_WIDTH,LINE_DOWN),width=2)
                Logger.info()
                for entity in ALL_SPRITES:
                    SCREEN.blit(entity.surf, entity.rect)

                pg.display.flip()
                sprite_ind = next(sprite_chain_c)
                clock.tick(20)

            

            for _ in range(int(abs(displacement_y)/self.speed)):
                self.rect.move_ip(0,self.speed*displacement_y_sign)
                self.pos[1] += self.speed*displacement_y_sign # updating inner center coordinates
                
                #self.ChangeSprite(sprite_ind)
                self.surf , self.rect = ChangeSprite(self.rect_frames, self.rect_size0 , self.sheet , 
                             self.pos, self.size , sprite_ind)

                SCREEN.fill(SCREEN_COLOR)
                pg.draw.line(SCREEN,color=(0,0,0),start_pos=(0,LINE_UP),end_pos=(SCREEN_WIDTH,LINE_UP),width=2)
                pg.draw.line(SCREEN,color=(0,0,0),start_pos=(0,LINE_DOWN),end_pos=(SCREEN_WIDTH,LINE_DOWN),width=2)
                Logger.info()
                for entity in ALL_SPRITES:
                    SCREEN.blit(entity.surf, entity.rect)
                
                pg.display.flip()
                sprite_ind = next(sprite_chain_c)
                clock.tick(20)       
            

            self.surf , self.rect = ChangeSprite(self.rect_frames, self.rect_size0 , self.sheet , 
                             self.pos, self.size, sprite_chain[0]-1)

            self.rect_ind = sprite_chain[0]-1
            self.resource -= self.resource_drain
            # Keep player on the SCREEN
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
            if self.rect.top <= LINE_UP:
               self.rect.top = LINE_UP
            if self.rect.bottom >= LINE_DOWN:
                self.rect.bottom = LINE_DOWN
            

            return True , ''
        
    def Attack(self,coords):
        return self.Range_Attack(coords)

    def Range_Attack(self, coords):

        ranges = []
        for att in self.attacks:
            ranges.append(att['range'])

        distance = ((coords[0] - self.rect.centerx)**2 + (coords[1] - self.rect.centery)**2)**(0.5)

        # Failed by Range
        if distance > max(ranges):
            # attack longer than unit range!
            return False , 'range'
        
        # Failed by resource
        if self.resource-self.resource_drain <= 0:
            return False , 'resource'
        
        else:

            accuracy = random.randint(0,100)
            # Creating the arrow
            Arrow  = Weapon('Arrow', self.pos, coords)
            IsShoted = True


            range_check = [ar > distance for ar in ranges]
            range_ind = range_check.index(True)   #Finding the first True
            damage = self.attacks[range_ind]['damage']
            att_accuracy = self.attacks[range_ind]['accuracy']
            
            if att_accuracy <= (100-accuracy):
                IsShoted = False

            if not IsShoted:
                #Failed coords
                nexp = random.randint(0,10)
                x_rand = coords[0] + (-1)**nexp*random.randint(int(0.1*coords[0]),int(0.3*coords[0]))
                y_rand = coords[1] + (-1)**nexp*random.randint(int(0.1*coords[1]),int(0.3*coords[1]))
                coords = [x_rand,y_rand]

            damage_value, critical = DamageCalculation(self.name, damage)
            ytraj , xtraj, dtraj = CreateTrajectory(Arrow.pos,coords, get_gradient=True)

            d_x = coords[0] - Arrow.pos[0]

            if d_x<0:
                if self.rect_ind == 0:
                    self.rect_ind = self.movement_sprites[0]
                    self.surf , self.rect = ChangeSprite(self.rect_frames, self.rect_size0 , self.sheet , 
                             self.pos, self.size, self.movement_sprites[0])
            elif d_x>0:
                if self.rect_ind == self.movement_sprites[0]:
                    self.rect_ind = 0
                    self.surf , self.rect = ChangeSprite(self.rect_frames, self.rect_size0 , self.sheet , 
                             self.pos, self.size, 0)


            Dt = 45 # Milisecond
            theta0 = Arrow.angle
            theta_range = Arrow.angle_range
            ALL_SPRITES.add(Arrow)

            for t in range(len(xtraj)):
                theta = arctan(-dtraj[t])*180/pi
                theta_index = int((theta-theta0)*Arrow.number_of_sprites/theta_range)
                Arrow.surf, Arrow.rect = ChangeSprite(Arrow.rect_frames, Arrow.rect_size0 , 
                             Arrow.sheet , Arrow.pos, Arrow.size, theta_index)

                Arrow.rect.center = (xtraj[t], ytraj[t])
                SCREEN.fill(SCREEN_COLOR)
                pg.draw.line(SCREEN,color=(0,0,0),start_pos=(0,LINE_UP),end_pos=(SCREEN_WIDTH,LINE_UP),width=2)
                pg.draw.line(SCREEN,color=(0,0,0),start_pos=(0,LINE_DOWN),end_pos=(SCREEN_WIDTH,LINE_DOWN),width=2)
                Logger.info()
                for entity in ALL_Objects:
                    SCREEN.blit(entity.surf, entity.rect)
                for entity in ALL_SPRITES:
                    SCREEN.blit(entity.surf, entity.rect)
                
             
                pg.display.flip()
                clock.tick(Dt)
                
            self.resource -= self.resource_drain

            if not IsShoted:
                return False, 'accuracy'
            else:
                return True, [damage_value,critical]

    def Died(self):
        
        sheet , rect_frames = ReadSpriteSheet(main_dir + '/data/characters/Archer01_died_ss.png' , [2,2] , 4)
        if self.rect_ind==0:
            rect = pg.Rect(rect_frames[0])
        else:
            rect = pg.Rect(rect_frames[2])
        rect_size0 = rect.size
        surf = pg.Surface(rect_size0, pg.SRCALPHA)
        surf.blit(sheet, (0, 0), rect)
        
        rect = surf.get_rect(center=(self.pos[0],self.pos[1]))
        surf = pg.transform.scale(surf, (int(rect_size0[0]*self.scale_factor), int(rect_size0[1]*self.scale_factor)))
        size = surf.get_size()
        
        corpse = pg.sprite.Sprite()
        corpse.surf = surf
        corpse.rect = rect
        corpse.name = 'corpse'
        ALL_Objects.add(corpse)

        self.kill()

class Weapon(pg.sprite.Sprite):
    def __init__(self , name , pos, coords=[]):
        super(Weapon, self).__init__()
        
        if name == 'Arrow':
            self.name = 'Arrow'
            self.speed = 10
            self.offset = [0,-8]
            self.target = coords
            self.pos = [pos[0]+self.offset[0], pos[1]+self.offset[1]]
            self.RC_tup = [6,7]
            self.number_of_sprites = 41

            if (coords[0] - self.pos[0])>0:
                self.sheet , self.rect_frames = ReadSpriteSheet(main_dir + '/data/characters/Archer/' + name + '01_ss.png' , 
                             self.RC_tup , self.number_of_sprites)
            else:
                self.sheet , self.rect_frames = ReadSpriteSheet(main_dir + '/data/characters/Archer/' + name + '02_ss.png' , 
                             self.RC_tup , self.number_of_sprites)
                

            self.scale_factor = 0.8
            self.angle = -90
            self.angle_range = 180
            self.rect_ind = 0
            rect = pg.Rect(self.rect_frames[self.rect_ind])
            self.rect_size0 = rect.size
            surf = pg.Surface(self.rect_size0, pg.SRCALPHA)
            surf.blit(self.sheet, (0, 0), rect)
            self.rect = surf.get_rect(center=(self.pos[0],self.pos[1]))
            size = surf.get_size()
            self.surf = pg.transform.scale(surf, (int(size[0]*self.scale_factor), int(size[1]*self.scale_factor)))
            self.size = surf.get_size()

class Object(pg.sprite.Sprite):
    def __init__(self , name , pos):
        super(Object, self).__init__()

        self.pos = pos
        self.call_name = name

        if name == 'rock':
            self.name = 'rock'
            self.RC_tup = [2,3]
            self.number_images = 6
            self.scale_factor = 2
            path_to_ss = main_dir + '/data/objects/Rocks/rock01_ss.png'
        
        elif name == 'tree':
            self.name = 'tree'
            self.RC_tup = [8,7]
            self.number_images = 50
            self.scale_factor = 1.2
            self.SPI = 3
            path_to_ss = main_dir + '/data/objects/Trees/bigtree_small_ss.png'

        elif name in ['House01','House02']:
            self.name = 'house'
            path_to_ss = main_dir + '/data/objects/House/' + name +'_ss.png'
            self.RC_tup = [4,5]
            self.SPI = 8
            self.number_images = 18
            self.scale_factor = 2.3

        elif name == 'sky':
            self.name = 'sky'
            path_to_ss = main_dir + '/data/objects/Sky/Sky01.png'
            self.RC_tup = [1,1]
            self.SPI = 1
            self.number_images = 1
            self.scale_factor = 1

        self.sheet , self.rect_frames = ReadSpriteSheet(path_to_ss, self.RC_tup , self.number_images )
        self.rect = pg.Rect(self.rect_frames[0])
        self.rect_size0 = self.rect.size
        self.rect_ind = 0
        self.surf = pg.Surface(self.rect.size).convert()
        self.surf.blit(self.sheet, (0, 0), self.rect)
        self.surf.set_colorkey((0,0,0), RLEACCEL)
        self.rect = self.surf.get_rect(center=(self.pos[0],self.pos[1]))
        self.surf = pg.transform.scale(self.surf, (int(self.rect_size0[0]*self.scale_factor), int(self.rect_size0[1]*self.scale_factor)))
        self.size = self.surf.get_size()

        # video
        self.animation_time = 0
        self.run_animation = False
        self.DisplayActionBar = False
        self.animation_ind = 0


    def animate(self, backwards = False):
        self.animation_ind += 1
        if self.animation_ind%self.SPI == 0:
            self.rect_ind +=1
            self.surf, self.rect = ChangeSprite(self.rect_frames, self.rect_size0 , 
                            self.sheet , self.pos, self.size, self.rect_ind)

            if self.rect_ind+1  == self.number_images:
                self.rect_ind = 0
                self.animation_ind = 0
                self.run_animation = False
                if backwards:
                    self.rect_frames.reverse()
                else:
                    self.surf, self.rect = ChangeSprite(self.rect_frames, self.rect_size0 , 
                                    self.sheet , self.pos, self.size, self.rect_ind)

class Log():

    def __init__(self, screen , mode):

        self.lines = []
        self.msg = ['',0]
        self.text_aux = ''
        self.counting_time = False
        self.timer = []
        self.tcur = 0
        #self.cur_ind = 0
        #self.new_ind = 0
        self.screen = screen

        if mode == 'all_info':
            self.max_lines = 3
            self.fontsize = 10
            self.position = [SCREEN_WIDTH*0.77,SCREEN_HEIGHT*0.93]
            self.lines_spacing = 15
        elif mode == 'global':
            self.fontsize = 18
            self.big_fontsize = 32
            self.position = [SCREEN_WIDTH*0.1,SCREEN_HEIGHT*0.02]
            self.max_lines = 1

    def write_all(self, text):

        if self.lines:
            if not text == self.lines[-1]:
                self.lines.append(text)
        else:
            self.lines.append(text)

        if len(self.lines) > self.max_lines:
            self.lines.remove(self.lines[0])
        
        for l,line in enumerate(self.lines):
            yoffset = l*self.lines_spacing
            surf_text, _ = GAME_FONT.render(line, (0, 0, 0) , size= self.fontsize)
            self.screen.blit(surf_text,(self.position[0] ,self.position[1] + yoffset))
        
    def info(self , msg = None , holdtime = None):
        
        if self.counting_time:
            self.tcur += clock.get_time()
            if (self.tcur - self.timer[0]) >= 1000*self.timer[1]:
                self.msg[0] = self.text_aux
                self.tcur = 0
                self.timer = [0,0]
                self.counting_time = False
                

        if msg:
            if holdtime and not self.counting_time:
                self.counting_time = True
                self.timer = [clock.get_time(), holdtime]
                self.tcur = self.timer[0]
                self.text_aux = self.msg[0]
                self.msg[0] = msg[0]

            if not self.counting_time:
                if msg[1] < self.msg[1]:
                    pass
                else:
                    self.msg = msg 

    def Print(self):
        text, rect = GAME_FONT.render(self.msg[0], (0, 0, 0) , size= self.fontsize)
        #rect.center = (self.position[0],self.position[1])
        rect.centery = self.position[1]
        self.screen.blit(text,rect)

    def EndGame(self, msg):
        text, rect = GAME_FONT.render(msg[0], (0, 0, 0) , size= self.big_fontsize)
        rect.center = (SCREEN_WIDTH*0.5,SCREEN_HEIGHT*0.5)
        self.screen.blit(text,rect)


# Global variables
pg.init()
pg.mixer.init()
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 950
#SCREEN_COLOR = (240, 230, 245) #~white
SCREEN_COLOR = (229, 255, 204) #light green
LINE_UP = SCREEN_HEIGHT*0.04
LINE_DOWN = SCREEN_HEIGHT*0.96

main_dir = os.path.split(os.path.abspath(__file__))[0]    
GAME_FONT = pygame.freetype.Font('/home/yeye/Desktop/strawberry/data/fonts/PressStartRegular-ay8E.ttf', 32 )
GAME_FONT.origin = True
clock = pg.time.Clock()
SCREEN = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
ALL_SPRITES = pg.sprite.Group()
ALL_Objects = pg.sprite.Group()
Logger = Log(SCREEN , mode = 'global')
pg.display.set_caption('strawberry bf')
Pixel2Mts = 1.7/70

pg.mixer.music.load(main_dir + '/data/music/Death_Bed.ogg')
pg.mixer.music.play(-1)



def main():
    #### Players
    Player_A = Player('Player A')
    Player_B = Player('Player B')
    Player_inturn_cycle = cycle([Player_A, Player_B])
    Player_waiting_cycle = cycle([Player_B, Player_A])
    Player_inturn = next(Player_inturn_cycle)
    #Player_waiting = next(Player_waiting_cycle)
    Players_list = [Player_A, Player_B]
    ####
    
    # Create a custom event for adding a new enemy
    MOVETREES = pg.USEREVENT + 1
    pg.time.set_timer(MOVETREES, 5000)
    CleanBattleField = pg.USEREVENT + 2
    pg.time.set_timer(CleanBattleField, 45000)
    HouseMovement = pg.USEREVENT + 3
    pg.time.set_timer(HouseMovement, 10000)
    

    # Add units to players
    Player_A.UnitsGroup.add(Unit('Archer',[300,500], Player_A.name))
    #Player_A.UnitsGroup.add(Unit('Villager',[340,480], Player_A.name))
    Player_B.UnitsGroup.add(Unit('Archer',[1600,250], Player_B.name))
    
    # Objects
    ALL_Objects.add(Object('sky',[900,0]))
    ALL_Objects.add(Object('rock',[900,700]))
    ALL_Objects.add(Object('rock',[950,720]))
    ALL_Objects.add(Object('tree',[150,400]))
    ALL_Objects.add(Object('tree',[80,180]))
    ALL_Objects.add(Object('tree',[80,300]))
    ALL_Objects.add(Object('tree',[30,310]))
    
    # Houses
    Player_A.Home = Object('House01',[60,600])
    Player_B.Home = Object('House02',[1600,150])

    ALL_Objects.add(Player_A.Home)
    ALL_Objects.add(Player_B.Home)
    

    for sprites in ALL_Objects.sprites():
        ALL_SPRITES.add(sprites)

    for Player_ in Players_list:
        for sprites_ in Player_.UnitsGroup.sprites():
            #all_units.add(sprites_)
            ALL_SPRITES.add(sprites_)
            
    
    # Main loop
    running = True
    ActionBars = False
    WaitingEnd = False
    MovingUnit = {'on': False , 'coords' : []}
    AttackingUnit = {'on': False , 'target' : [], 'unit':[]}


    while running:

        SCREEN.fill(SCREEN_COLOR)
        #pg.draw.line(SCREEN,color=(0,0,0),start_pos=(0,LINE_UP),end_pos=(SCREEN_WIDTH,LINE_UP),width=2)
        pg.draw.line(SCREEN,color=(0,0,0),start_pos=(0,LINE_DOWN),end_pos=(SCREEN_WIDTH,LINE_DOWN),width=2)
        
        Logger.info([Player_inturn.name + ' turn', 1])
        Player_inturn.DisplayDiamonds()
        DisplayResources(Players_list)

        # Look at every event in the queue
        for event in pg.event.get():
            if event.type  == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == QUIT:
                running = False

            elif event.type == MOVETREES:
                for obj in ALL_Objects.sprites():
                    if obj.name == 'tree':
                        if not obj.run_animation:
                            obj.run_animation = True

            elif event.type == HouseMovement:
                for obj in ALL_Objects.sprites():
                    if obj.name == 'house':
                        if not obj.run_animation:
                            Coin = random.randint(0,1)
                            if Coin:
                                obj.run_animation = True

            elif event.type == CleanBattleField:
                for entity in ALL_Objects:
                    if entity.name == 'Arrow':
                        entity.kill()

            elif event.type == MOUSEBUTTONDOWN:
                if not WaitingEnd:
                    if MovingUnit['on']:
                        MovingUnit['coords'] = pg.mouse.get_pos()
                    elif AttackingUnit['on']:
                        AttackingUnit['target'] = pg.mouse.get_pos()
                        for player in Players_list:
                            for unit in player.UnitsGroup:
                                if unit.rect.collidepoint(pg.mouse.get_pos()):
                                    AttackingUnit['unit'] = unit
                    else:
                        if ActionBars:
                            for unit in Player_inturn.UnitsGroup:
                                if unit.DisplayActionBar:
                                    #ActionBar_Isclick will modify unit.IsAttack and unit.IsMoving
                                    isclick = ActionBar_IsClick(pg.mouse.get_pos(), unit)
                                    if not isclick:
                                        unit.DisplayActionBar = False
                                        ActionBars = False
                        else:
                            for unit in Player_inturn.UnitsGroup:
                                if unit.rect.collidepoint(pg.mouse.get_pos()):
                                    unit.DisplayActionBar = True
                                    ActionBars = True


        pressed_keys = pg.key.get_pressed()
        
        # Displaying Actions Bars of Info Bars
        if ActionBars:
            for unit in Player_inturn.UnitsGroup:
                if unit.DisplayActionBar:
                    DisplayInfo(unit, SCREEN, 1 )
        else:
            # Displaying Info Bars of all units when mouseover + i
            #for Player_ in Players_list:
            #    for unit in Player_.UnitsGroup:
            #        unit.DisplayActionBar = False
            for entity in ALL_SPRITES.sprites():
                if entity.rect.collidepoint(pg.mouse.get_pos()):
                    if pressed_keys[K_i]:
                        DisplayInfo(entity, SCREEN, 6 , info_mode= True)
    


        for obj in ALL_Objects.sprites():
            if obj.run_animation:
                if obj.name == 'tree':
                    obj.animate(backwards=True)
                else:
                    obj.animate()

    
        for unit in Player_inturn.UnitsGroup:
            if unit.IsMoving:
                Player_inturn, ActionBars, WaitingEnd = MovingLoop(Player_inturn, unit, MovingUnit, ActionBars, WaitingEnd, pressed_keys)
            
            elif unit.IsAttacking:
                Player_inturn, ActionBars, WaitingEnd = AttackingLoop(Player_inturn, unit, AttackingUnit, ActionBars, WaitingEnd, pressed_keys)



        # Checking for the winner
        for i_p, player in enumerate(Players_list):
            if len(player.UnitsGroup) == 0:
                if i_p==0:
                    Logger.EndGame([Players_list[i_p].name + ' is the winner!!' , 4])
                else:
                    Logger.EndGame([Players_list[i_p-1].name + ' is the winner!!' , 4])

                
        if WaitingEnd:
            Logger.info([Player_inturn.name + ' is done. Press Enter' , 4])

        # End of the Turn
        if pressed_keys[K_RETURN]:

            # Resetting Number of Actions
            if Player_inturn.TotalActions < Player_inturn.MaxActions:
                Player_inturn.TotalActions +=1
            Player_inturn.NumberOfActions = Player_inturn.TotalActions

            # Resting the Units
            for unit in Player_inturn.UnitsGroup:
                activities = unit.HadMoved + unit.HadAttacked
                unit.resource += 2*(Player_inturn.TotalActions - activities)

                if unit.InHome:
                    unit.resource = unit.full_resource
                    unit.hp += 15

                if unit.resource > unit.full_resource:
                    unit.resource = unit.full_resource
                if unit.hp > unit.full_hp:
                    unit.hp = unit.full_hp

                # Reseting values
                unit.HadMoved = 0
                unit.HadAttacked = 0

            for d in Player_inturn.diamonds.sprites():
                d.kill()
            
            Player_inturn = next(Player_inturn_cycle)
            WaitingEnd = False
            Logger.msg = ['',0]
            clock.tick(4)


        for entity in ALL_Objects:
            SCREEN.blit(entity.surf, entity.rect)

        for entity in ALL_SPRITES:
            SCREEN.blit(entity.surf, entity.rect)

        
        Logger.Print()
        pg.display.flip()
        clock.tick(60)




if __name__ == "__main__":

    # Reading Units Info
    path_to_units_dct = main_dir + '/data/Units.yaml'
    with open(path_to_units_dct, 'r+') as f:
        units_dct = yaml.load(f, Loader=yaml.Loader)

    main()
    pg.quit()







#pg.display.update()








