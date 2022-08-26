import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from itertools import cycle
import pygame as pg
import random
from numpy import linspace, gradient, arctan, pi, RankWarning, poly1d, polyfit, exp, sin, random
from scipy.interpolate import interp1d
import pygame.freetype
import ruamel.yaml as yaml
import operator
import warnings

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
    K_TAB,
    KEYDOWN,
    KEYUP,
    QUIT,
    K_RETURN,
    K_c,
    K_f,
    K_m,
    K_n,
    K_r,
    K_i,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
)

def General_Blit():

    for entity in ALL_OBJECTS:
        #if entity.name == 'Bridge':
        #    pg.draw.rect(SCREEN,color=(250,102,102),rect=entity.rect.inflate(-30,-60))

        SCREEN.blit(entity.surf, entity.rect)
        if 'FruitGroup' in vars(entity):
            for fruit_ in entity.FruitGroup:
                SCREEN.blit(fruit_.surf, fruit_.rect)
        
        #if 'ObstacleGroup' in vars(entity):
        #    if entity.name == 'Rock':
        #        for obt in entity.ObstacleGroup:
        #            pg.draw.rect(SCREEN,color=(255,250,102),rect=obt.rect)


    for entity in ALL_SPRITES:
        SCREEN.blit(entity.surf, entity.rect)
    
    for entity in ALL_OBJECTS:
        if entity.name in ['Arrow','MagicBolt']:
            SCREEN.blit(entity.surf, entity.rect)

def CreateTrajectory(coordsA,coordsB, projectile_name, get_gradient = False):
    ''' 
        Projectile trajectory from A to B
    '''

    A0x = min([coordsB[0], coordsA[0]])
    A0y = min([coordsB[1], coordsA[1]])
    B0x = abs(coordsB[0] - coordsA[0])
    B0y = abs(coordsB[1] - coordsA[1])

    if projectile_name == "Arrow":
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

    elif projectile_name == 'MagicBolt':
        Np = 4
        ExtraPoints = {}
        Dx = coordsB[0] - coordsA[0]
        Dy = coordsB[1] - coordsA[1]

        for k in range(Np):
            yrnd = random.rand()
            xk = coordsA[0] + Dx*(k+1)/(Np+1)
            yk = coordsA[1] + Dy*yrnd
            ExtraPoints[k] = [xk,yk]
            
        xtraj = linspace(min([coordsB[0], coordsA[0]]),max([coordsB[0], coordsA[0]]),80)
        xdata = [coordsA[0],coordsB[0]]
        ydata = [coordsA[1],coordsB[1]]

        for _,elem in ExtraPoints.items():
            xdata.append(elem[0])
            ydata.append(elem[1])

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RankWarning)
            f = poly1d(polyfit(xdata,ydata,4))

        frac = random.randint(8)
        amp = random.randint(150)
        beta = random.rand()*10
        
        if coordsB[0]<coordsA[0]:
            xtraj = xtraj[::-1]

        ytraj = f(xtraj) #+ amp*sin((xtraj-coordsA[0])*frac*pi/Dx)*exp(-beta*(xtraj-coordsA[0]))

    if get_gradient:
        dx = abs(xtraj[1] - xtraj[0])
        dtraj = gradient(ytraj,dx)
        return ytraj, xtraj, dtraj
    else:
        return ytraj, xtraj

def ChangeImage(new_image,size):

    surf = pg.image.load(new_image).convert_alpha()
    surf = pg.transform.scale(surf,(int(size[0]),int(size[1]) ))

    return surf

def ChangeSprite(rect_frames, rect_size0 , sheet , pos, final_size, index):
    rect = pg.Rect(rect_frames[index])
    surf = pg.Surface(rect_size0 ,pg.SRCALPHA)
    surf.blit(sheet, (0, 0), rect)
    surf = pg.transform.scale(surf, (final_size[0], final_size[1]))
    rect = surf.get_rect(center=(pos[0],pos[1]))

    return surf, rect

def DamageCalculation(unit_name, damage):
    ''' 
        return the damage value according to unit and attack type
    '''
    damage_value = 0
    critical = ''


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

def DisplayResources(Players_list, color=None):
    for Player_ in Players_list:

        wood = Player_.resources['wood']
        food = Player_.resources['food']
        rock = Player_.resources['rock']

        resources_str = 'Food={i}/Wood={j}/Rock={k}'.format(i=food,j=wood,k=rock)
        
        if color:
            text, _ = GAME_FONT.render(resources_str, color , size=12)
        else:
            text, _ = GAME_FONT.render(resources_str, (0, 0, 0) , size=12)

        if Player_.name == 'Player A':
            SCREEN.blit(text, (SCREEN_WIDTH*0.01,SCREEN_HEIGHT*0.97))
        elif Player_.name == 'Player B':
            SCREEN.blit(text, (SCREEN_WIDTH*0.76,SCREEN_HEIGHT*0.97))

def DisplayDamage(damage, coords = None):
    yoffset = -10
    xoffset = -10

    if damage[0]>=0:
        if damage[1] == 'critical':
            damage_text, _ = GAME_FONT.render(str(damage[0]), (255,102,102) , size=14)
        else:
            damage_text, _ = GAME_FONT.render(str(damage[0]), (204, 204, 0) , size=12)
    else:
        damage_text, _ = GAME_FONT.render(str(-damage[0]), (102, 255, 102) , size=12)

    damage_sprite = pg.sprite.Sprite()
    damage_sprite.surf = damage_text
    if coords:
        damage_sprite.rect = (coords[0]+xoffset,coords[1]+yoffset)
    else:
        damage_sprite.rect = None

    return damage_sprite

def DisplayInfo(unit, SCREEN, number_images, info_mode=False):
    # Canvas
    # TODO: delete
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

def ExtractingResources(Player, unit, actions_saved=None):
    
    if not actions_saved:
        actions_left = Player.TotalActions - Player.NumberOfActions
        if bool(actions_left - unit.HadWorked):
            worked_object = unit.WorkingObject.sprites()[0]
            worked_object.resource -= worked_object.resource_drain
            unit.HadWorked += 1
            # reducing the stamina of the workers
            unit.resource -= unit.resource_drain
            worked_object.update()

            if unit.resource <= 0:
                unit.resource = 0
                unit.IsWorking = False
                unit.Talk('I need rest...')
                unit.rect_ind = 0
                unit.animation_ind = 0
                unit.ChangeSprite()

            if worked_object.resource <= 0:
                Player.resources[worked_object.resource_name] += worked_object.resource + worked_object.resource_drain
                worked_object.kill()
                unit.IsWorking = False
                unit.Talk('This is over!')
                unit.rect_ind = 0
                unit.animation_ind = 0
                unit.ChangeSprite()
            else:
                Player.resources[worked_object.resource_name] += worked_object.resource_drain

    else:
        if actions_saved >0:
            worked_object = unit.WorkingObject.sprites()[0]
            for _ in range(actions_saved):
                if unit.resource != 0:
                    worked_object.resource -= worked_object.resource_drain
                    unit.HadWorked += 1
                    unit.resource -= unit.resource_drain
                    worked_object.update()

                    if unit.resource <=0:
                        unit.resource = 0
                        unit.IsWorking = False
                        unit.Talk('I need rest...')
                        unit.rect_ind = 0
                        unit.animation_ind = 0
                        unit.ChangeSprite()       

                    if worked_object.resource <= 0:
                        Player.resources[worked_object.resource_name] += worked_object.resource + worked_object.resource_drain
                        worked_object.kill()
                        unit.IsWorking = False
                        unit.Talk('This is over')
                        unit.rect_ind = 0
                        unit.animation_ind = 0
                        unit.ChangeSprite()
                        break
                    else:
                        Player.resources[worked_object.resource_name] += worked_object.resource_drain

def GatheringResources(Player, unit, actions_saved=None):
    
    if not actions_saved:
        actions_left = Player.TotalActions - Player.NumberOfActions
        if bool(actions_left - unit.HadWorked):
            gathered_object = unit.GatheringObject.sprites()[0]
            food_in = gathered_object.FruitGroup.sprites()[0]
            food_gain = random.randint(food_in.hp_gain[0],food_in.hp_gain[1])
            food_in.kill()
            unit.HadWorked += 1
            # reducing the stamina of the workers
            unit.resource -= unit.resource_drain
            # only for rock
            gathered_object.update()

            Player.resources['food'] += food_gain

            if unit.resource <= 0:
                unit.resource = 0
                unit.IsGathering = False
                unit.Talk('I need rest...')
                unit.rect_ind = 0
                unit.animation_ind = 0
                unit.ChangeSprite()
                unit.GatheringObject.empty()

            if len(gathered_object.FruitGroup) == 0:
                unit.IsGathering = False
                unit.Talk('No more to collect!')
                unit.rect_ind = 0
                unit.animation_ind = 0
                unit.ChangeSprite()
                unit.GatheringObject.empty()


    else:
        if actions_saved >0:
            gathered_object = unit.GatheringObject.sprites()[0]
            for _ in range(actions_saved):
                if unit.resource != 0:
                    food_in = gathered_object.FruitGroup.sprites()[0]
                    food_gain = random.randint(food_in.hp_gain[0],food_in.hp_gain[1])
                    food_in.kill()
                    unit.HadWorked += 1
                    # reducing the stamina of the workers
                    unit.resource -= unit.resource_drain
                    # only for rock
                    gathered_object.update()

                    Player.resources['food'] += food_gain

                    if unit.resource <= 0:
                        unit.resource = 0
                        unit.IsGathering = False
                        unit.Talk('I need rest...')
                        unit.rect_ind = 0
                        unit.animation_ind = 0
                        unit.ChangeSprite()
                        unit.GatheringObject.empty()

                    if len(gathered_object.FruitGroup) == 0:
                        unit.IsGathering = False
                        unit.Talk('No more to collect!')
                        unit.rect_ind = 0
                        unit.animation_ind = 0
                        unit.ChangeSprite()
                        unit.GatheringObject.empty()
                        break
 
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

def BuyingLoop(Player, ActionBars):
    '''
        Buying Loop
    '''


    path_to_ss = main_dir + '/data/objects/Book/book_ss.png'
    RC_tup = [2,1]
    sheet , rect_frames = ReadSpriteSheet(path_to_ss , RC_tup , 2)
    # Sprite
    
    book = pg.sprite.Sprite()

    rect_ind = 0
    scale_factor = 3
    rect = pg.Rect(rect_frames[rect_ind])
    rect_size0 = rect.size
    surf = pg.Surface(rect_size0, pg.SRCALPHA)
    surf.blit(sheet, (0, 0), rect)
    surf = pg.transform.scale(surf, (int(rect_size0[0]*scale_factor), int(rect_size0[1]*scale_factor)))
    rect = surf.get_rect(center=(SCREEN_WIDTH*0.5,SCREEN_HEIGHT*0.5))
    book.surf = surf
    book.pos = [SCREEN_WIDTH*0.5,SCREEN_HEIGHT*0.5]
    book.rect = rect
    book.size = surf.get_size()
    book.display_info = None
    CanAfford = True
    catalogue = Catalogue(book)

    while Player.Home.IsBuying:
        Logger.info([Player.name + ' is buying...', 1 ])

        for event in pg.event.get():
            if event.type  == KEYDOWN:
                if event.key in [K_c,K_ESCAPE]:
                    Logger.info([Player.name + ' turn', 1])
                    Player.Home.IsBuying = False
                    Player.Home.DisplayActionBar = False
                    ActionBars = False
                    book.kill()
                    Player.Home.action_updown = [0,0]

                if event.key == K_LEFT:
                    # Change the image
                    rect_ind -= 1
                    if rect_ind <= 0:
                        rect_ind = 0
                    book.display_info = False
                    posx = book.pos[0]
                    posy = book.pos[1]
                
                    rect = pg.Rect(rect_frames[rect_ind])
                    surf = pg.Surface(rect_size0, pg.SRCALPHA)
                    surf.blit(sheet, (0, 0), rect)
                    surf = pg.transform.scale(surf, (book.size[0],book.size[1]))
                    rect = surf.get_rect(center=(posx,posy))
                    book.surf = surf
                    book.rect = rect

                if event.key == K_RIGHT:
                    # Change the image
                    rect_ind += 1
                    if rect_ind >= 1:
                        rect_ind = 1
                    
                    book.display_info = True
                    posx = book.pos[0]*0.95
                    posy = book.pos[1]*0.95

                    rect = pg.Rect(rect_frames[rect_ind])
                    surf = pg.Surface(rect_size0, pg.SRCALPHA)
                    surf.blit(sheet, (0, 0), rect)
                    surf = pg.transform.scale(surf, (book.size[0],book.size[1]))
                    rect = surf.get_rect(center=(posx,posy))
                    book.surf = surf
                    book.rect = rect

            elif event.type == MOUSEBUTTONDOWN:
                if not book.display_info:
                    # Change the image
                    rect_ind +=1
                    if rect_ind >= 1:
                        rect_ind = 1
                    rect = pg.Rect(rect_frames[rect_ind])
                    surf = pg.Surface(rect_size0, pg.SRCALPHA)
                    surf.blit(sheet, (0, 0), rect)
                    surf = pg.transform.scale(surf, (book.size[0],book.size[1]))
                    rect = surf.get_rect(center=(book.pos[0]*0.95,book.pos[1]*0.95))
                    book.surf = surf
                    book.rect = rect
                    # Displaying Catalogue
                    book.display_info = True
                else:
                    for buttom in catalogue.Buttoms:
                        if buttom.rect.collidepoint(pg.mouse.get_pos()):
                            CanAfford = True
                            unit_cost = units_dct[buttom.unit]['Parameters']['cost']
                            # checking if player can afford
                            for res in unit_cost:
                                if Player.resources[res] < unit_cost[res]:
                                    Logger.info(['Cannot afford that unit ' , 1], holdtime = 2)
                                    CanAfford = False
                                    break
                                else:
                                    # Buying
                                    Player.resources[res] -= unit_cost[res]

                            if CanAfford:
                                Logger.info([Player.name + ' has bought an ' + buttom.unit , 1], holdtime = 3)

                                # Adding the new unit
                                position = Player.Home.rect.midbottom
                                NEW_UNIT = Unit(buttom.unit,[position[0],position[1]], Player.name)
                                Player.UnitsGroup.add(NEW_UNIT)
                                ALL_SPRITES.add(NEW_UNIT)

                                Player.Home.IsBuying = False
                                Player.Home.DisplayActionBar = False
                                ActionBars = False
                                book.kill()
                                catalogue.kill()
                                Player.Home.action_updown = [0,0]

                                

        SCREEN.fill((64,64,64))
        DisplayResources([Player], color = (255,255,255))
        SCREEN.blit(book.surf, book.rect)
        if book.display_info:
            for text in catalogue.TextGroup:
                SCREEN.blit(text.surf, text.rect)

        Logger.Print(color = (255,255,255))
        pg.display.flip()


    return Player, ActionBars

def ActionLoop(Player, unit, MovingUnit, AttackingUnit, ActionBars, WaitingEnd, pressed_keys):


    if unit.IsMoving:
        Player, ActionBars, WaitingEnd = MovingLoop(Player, unit, MovingUnit, 
                                            ActionBars, WaitingEnd, pressed_keys)
    
    elif unit.IsAttacking:
        Player, ActionBars, WaitingEnd = AttackingLoop(Player, unit, 
                     AttackingUnit, ActionBars, WaitingEnd, pressed_keys)

    elif unit.IsEating:
        Player, ActionBars, WaitingEnd = EatingLoop(Player, unit, ActionBars, WaitingEnd)

    elif unit.StartWork:
        Player, ActionBars, WaitingEnd = WorkingLoop(Player, unit, ActionBars, WaitingEnd)

    elif unit.IsTalking:
        ActionBars = TalkingLoop(unit, ActionBars)

    elif unit.StartGathering:
        Player, ActionBars, WaitingEnd = GatherLoop(Player, unit, ActionBars, WaitingEnd)

    return Player, ActionBars, WaitingEnd
        
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
        unit.action_updown = [0,0]
        pg.mouse.set_cursor(pg.cursors.arrow)
        MovingUnit['on'] = False
        MovingUnit['coords'] = []

    if MovingUnit['coords']:
        # the unit will try to move
        IsMoved , msg = unit.Move(MovingUnit['coords'])
        if IsMoved:
            Logger.info([Player.name + ' is moving...', 1 ])
            unit.IsMoving = False
            unit.IsWorking = False
            Player.NumberOfActions -= 1
            Player.diamonds.sprites()[Player.NumberOfActions].surf = Player.diamond0_img
            # Checking InHome condition
            if DistanceBetween(unit,Player.Home) < 100:
                unit.InHome = True
            else:
                unit.InHome = False
            if Player.NumberOfActions == 0:
                WaitingEnd = True
            unit.HadMoved += 1
            unit.DisplayActionBar = False
            ActionBars = False
            unit.action_updown = [0,0]
            pg.mouse.set_cursor(pg.cursors.arrow)
            MovingUnit['on'] = False
            MovingUnit['coords'] = []
        else:
            if msg == 'range':
                Logger.info(['Movement longer than Unit\'s range ' , 1], holdtime = 2)
                #unit.Talk('too far!')
                MovingUnit['coords'] = []

            elif msg == 'collision':
                Logger.info(['Cannot move there! ' , 1], holdtime = 2)
                MovingUnit['coords'] = []

            elif msg == 'resource':
                pg.mouse.set_cursor(pg.cursors.arrow)
                unit.IsMoving = False
                Logger.info(['I am tired ... I need some rest! ' , 1], holdtime = 2)
                ActionBars = False
                unit.action_updown = [0,0]
                MovingUnit['on'] = False
                MovingUnit['coords'] = []

        
    return Player, ActionBars, WaitingEnd

def EatingLoop(Player, unit, ActionBars, WaitingEnd):
    '''
        Eating loop using the player and the unit
    '''

    Logger.info([Player.name + ' is eating...', 1 ])

    # the unit will try to eat
    IsFeed , msg = unit.Eat()

    if IsFeed:
        unit.IsEating = False
        unit.IsWorking = False
        Player.NumberOfActions -= 1
        Player.diamonds.sprites()[Player.NumberOfActions].surf = Player.diamond0_img
        Logger.info([Player.name + ' had eaten' , 1], holdtime = 1)
        if Player.NumberOfActions == 0:
            WaitingEnd = True
        
        unit.DisplayActionBar = False
        ActionBars = False
        unit.reset_bar()
        unit.action_updown = [0,0]
    else:
        if msg == 'no_food':
            Logger.info(['No food nearby!' , 1], holdtime = 1)
            ActionBars = False
            unit.IsEating = False
            unit.DisplayActionBar = False
            unit.reset_bar()
            unit.action_updown = [0,0]
        if msg == 'full_hp':
            ActionBars = False
            unit.IsEating = False
            unit.DisplayActionBar = False
            unit.reset_bar()
            unit.action_updown = [0,0]
            unit.Talk('I am not hungry')
            
    return Player, ActionBars, WaitingEnd

def GatherLoop(Player, unit, ActionBars, WaitingEnd):
    '''
        Gather loop using the player and the unit
    '''

    Logger.info([Player.name + ' is gathering food...', 1 ])

    # the unit will try to eat
    IsGathering , msg = unit.Gather()

    if IsGathering:
        unit.IsGathering = True
        unit.StartGathering = False
        unit.IsWorking = False
        Player.NumberOfActions -= 1
        Player.diamonds.sprites()[Player.NumberOfActions].surf = Player.diamond0_img
        if Player.NumberOfActions == 0:
            WaitingEnd = True
        
        unit.DisplayActionBar = False
        ActionBars = False
        unit.reset_bar()
        unit.action_updown = [0,0]
    else:
        if msg == 'no_food':
            Logger.info(['No food nearby!' , 1], holdtime = 1)
            ActionBars = False
            unit.StartGathering = False
            unit.DisplayActionBar = False
            unit.reset_bar()
            unit.action_updown = [0,0]

            
    return Player, ActionBars, WaitingEnd

def WorkingLoop(Player, unit, ActionBars, WaitingEnd):
    '''
        Working loop using the player and the unit
    '''

    #Logger.info([Player.name + ' started a work', 1 ])

    IsWorking , msg = unit.Work()
    
    if IsWorking:
        unit.StartWork = False
        unit.IsWorking = True
        Player.NumberOfActions -= 1
        Player.diamonds.sprites()[Player.NumberOfActions].surf = Player.diamond0_img
        if Player.NumberOfActions == 0:
            WaitingEnd = True
        
        unit.DisplayActionBar = False
        ActionBars = False
        unit.action_updown = [0,0]
    else:
        if msg == 'no_work_source':
            Logger.info(['No work source nearby!' , 1], holdtime = 1)
            ActionBars = False
            unit.StartWork = False
            unit.DisplayActionBar = False
            unit.reset_bar()
            unit.action_updown = [0,0]
            
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
        unit.action_updown = [0,0]
        unit.action_updown == [0,0]
        pg.mouse.set_cursor(pg.cursors.arrow)
        AttackingUnit['on'] = False
        AttackingUnit['target'] = []

    if unit.InHome:
        # Cancel the Attack
        Logger.info(['I cannot fight here!' , 1], holdtime=2)
        unit.IsAttacking = False
        unit.DisplayActionBar = False
        ActionBars = False
        unit.action_updown = [0,0]
        unit.action_updown == [0,0]
        pg.mouse.set_cursor(pg.cursors.arrow)
        AttackingUnit['on'] = False
        AttackingUnit['target'] = []

    if AttackingUnit['target']:

        if AttackingUnit['unit'] == unit:
            # prevent self-attack
            Logger.info(['Cannot attack myself!' , 1], holdtime=2)
            AttackingUnit['target'] = []
            AttackingUnit['unit'] = []
        else:
            # the unit will try to attack
            IsAttack , msg = unit.Attack(AttackingUnit['target'],AttackingUnit['unit'])
            if IsAttack:
                unit.IsAttacking = False
                unit.IsWorking = False
                Player.NumberOfActions -= 1
                Player.diamonds.sprites()[Player.NumberOfActions].surf = Player.diamond0_img

                if Player.NumberOfActions == 0:
                    WaitingEnd = True
                            
                unit.HadAttacked += 1
                unit.DisplayActionBar = False
                ActionBars = False
                unit.action_updown = [0,0]
                pg.mouse.set_cursor(pg.cursors.arrow)
                AttackingUnit['on'] = False
                AttackingUnit['target'] = []
                AttackingUnit['unit'] = []
            else:
                if msg == 'range':
                    Logger.info(['The target is too far away!' , 1], holdtime=2)
                    AttackingUnit['target'] = []
                    AttackingUnit['unit'] = []
                elif msg == 'resource':
                    pg.mouse.set_cursor(pg.cursors.arrow)
                    unit.IsAttacking = False
                    Logger.info(['I am tired ... need some rest! ' , 1], holdtime = 2)
                    ActionBars = False
                    unit.action_updown = [0,0]
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
                    unit.action_updown = [0,0]
                    AttackingUnit['on'] = False
                    AttackingUnit['target'] = []
                    

        
    return Player, ActionBars, WaitingEnd

def TalkingLoop(unit, ActionBars):
    '''
        Talking loop
    '''

    unit.Talk('hello')
    unit.IsTalking = False
    unit.DisplayActionBar = False
    ActionBars = False
    unit.reset_bar()
    unit.action_updown = [0,0]
        
    return ActionBars

class Player():
    def __init__(self , name ):

        self.name = name
        
        self.resources = {
            'wood': 25,
            'food': 25,
            'rock': 10
        }

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
                d.HasBar = False
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
        self.Player_name = player_name
        self.pos = pos
        self.offsets = self.data['Image']['offsets']

        if 'A' in player_name:
            self.type = self.data['types'][0]
        else:
            self.type = self.data['types'][1]

        # Image
        self.scale_factor = self.data['Image']['scale_factor']

        if 'gender' in self.data:
            coin = random.randint(0,2)
            if coin > 0:
                self.type += 'M'
                self.scale_factor = self.scale_factor[0]
            else:
                self.type += 'F'
                self.scale_factor = self.scale_factor[1]
        
        self.number_of_sprites = self.data['Image']['number_of_sprites']
        self.movement_sprites = [self.data['Image']['movement_sprites'], self.data['Image']['movement_sprites']]
        
        if 'working_sprites' in self.data['Image']:
            self.working_sprites = [self.data['Image']['working_sprites'],self.data['Image']['working_sprites']]
        if 'gathering_sprites' in self.data['Image']:
            self.gathering_sprites = [self.data['Image']['gathering_sprites'],self.data['Image']['gathering_sprites']]
        if 'attack_sprites' in self.data['Image']:
            self.attack_sprites = [self.data['Image']['attack_sprites'],self.data['Image']['attack_sprites']]
        

        self.RC_tup = self.data['Image']['RowColumn_tup']
        self.SPI = 5
        self.animation_ind = 0

        # Parameters
        self.action_updown = [0,0]
        self.actions_cycle_base = []
        for k in range(int((len(self.data['Parameters']['actions']) +1)/2)):
            if 2*k+1 == len(self.data['Parameters']['actions']):
                self.actions_cycle_base.append([self.data['Parameters']['actions'][2*k] , ''])
            else:
                self.actions_cycle_base.append([self.data['Parameters']['actions'][2*k] , self.data['Parameters']['actions'][2*k+1]])

        self.actions_cycle = cycle(self.actions_cycle_base)
        self.actions_lst = next(self.actions_cycle)
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
        rect = pg.Rect(self.rect_frames[self.rect_ind])
        self.rect_size0 = rect.size
        surf = pg.Surface(self.rect_size0, pg.SRCALPHA)
        surf.blit(self.sheet, (0, 0), rect)

        self.surf = pg.transform.scale(surf, (int(self.rect_size0[0]*self.scale_factor), int(self.rect_size0[1]*self.scale_factor)))
        self.rect = self.surf.get_rect(center=(self.pos[0],self.pos[1]))
        self.size = self.surf.get_size()

        # Worked objects group
        if 'Work' in self.data['Parameters']['actions']:
            self.WorkingObject = pg.sprite.Group()
            self.work_direction = None

        if 'Gather' in self.data['Parameters']['actions']:
            self.GatheringObject = pg.sprite.Group()
            self.gather_direction = None
        

        # Info related
        self.phrase = []
        self.HasBar = True
        self.DisplayActionBar = False
        self.ActionBar = None
        self.ActionBar_buttoms = {'Up': [] , 'Down': []}
        self.ActionBarPage = 0
        self.InHome = False
        self.IsAttacking = False
        self.IsEating = False
        self.IsWorking = False
        self.StartWork = False
        self.IsTalking = False
        self.StartGathering = False
        self.IsGathering = False

        # Move
        self.IsMoving = False
        self.OnMoving = False
        self.MovingInfo = {'coords': [], 'sprites': None, 'horizontal': [], 'vertical': [], 'right/left': None }

        self.HadMoved = 0
        self.HadAttacked = 0
        self.HadWorked = 0

        # Feet
        self.feet = pg.sprite.Sprite()
        if 'feet' in self.data['Image']['offsets']:
            [a,b,sa,sb,ss] = self.data['Image']['offsets']['feet']
        else:
            [a,b,sa,sb,ss] = [10,10,10,10,10]
        self.feet.rect = pg.Rect((self.rect.centerx + a,self.rect.centery + b,sa,sb))
        self.feet.dir = 'right'
        self.feet.shift = ss
        
        # Damage and Healing text
        self.weapon = None
        self.damage_text = None
        self.healing_text = None
        self.damage_duration = 0
        self.healing_duration = 0
        
    def assign_action(self, action):

        self.IsMoving = False
        self.IsAttacking = False
        self.IsEating = False
        self.IsTalking = False
        self.StartWork = False
        self.StartGathering = False
        
        if action == 'Move':
            self.IsMoving = True
        elif action == 'Attack':
            self.IsAttacking = True
        elif action == 'Eat':
            self.IsEating = True
        elif action == 'Gather':
            self.StartGathering = True
        elif action == 'Talk':
            self.IsTalking = True
        elif action == 'Work':
            self.StartWork = True

    def ChangeSprite(self):
        rect = pg.Rect(self.rect_frames[self.rect_ind])
        surf = pg.Surface(self.rect_size0 ,pg.SRCALPHA)
        surf.blit(self.sheet, (0, 0), rect)
        self.surf = pg.transform.scale(surf, (self.size[0], self.size[1]))
        
    def reset_bar(self):
        self.actions_cycle = cycle(self.actions_cycle_base)
        self.actions_lst = next(self.actions_cycle)

    def Move(self, coords, forced = False):

        distance = ((coords[0] - self.rect.centerx)**2 + (coords[1] - self.rect.centery)**2)**(0.5)
        moving = False
        objects_with_obs = []
        for obj in ALL_OBJECTS:
            if 'ObstacleGroup' in vars(obj):
                objects_with_obs.append(obj)

        if forced:
            moving = True

        if self.resource-self.resource_drain <= 0 and not moving:
            return moving , 'resource'
        
        if distance > self.mov_range and not moving:
            # displacement higher than unit range!
            return moving , 'range'
        else:
            moving = True

        for obj in objects_with_obs:
            for elem in obj.ObstacleGroup:
                if elem.rect.collidepoint(coords):
                    return False, 'collision'

        if moving:
            msg = ''
            displacement_x = int(coords[0]) - self.rect.centerx
            displacement_y = int(coords[1]) - self.rect.centery
            
            self.MovingInfo['coords'] = [int(coords[0]),int(coords[1])]

            if displacement_x >0:
                self.MovingInfo['right/left'] = 'right'
                self.MovingInfo['sprites'] = [1, self.movement_sprites[0]]
                self.MovingInfo['h_dir'] = 1
                if self.feet.dir == 'left':
                    self.feet.rect.move_ip(-self.feet.shift,0)
                    self.feet.dir = 'right'

            else:
                self.MovingInfo['right/left'] = 'left'
                self.MovingInfo['sprites'] = [self.movement_sprites[0] + 1, sum(self.movement_sprites)]
                self.MovingInfo['h_dir'] = -1
                if self.feet.dir == 'right':
                    self.feet.rect.move_ip(self.feet.shift,0)
                    self.feet.dir = 'left'


            if displacement_y > 0:
                self.MovingInfo['v_dir'] = 1
            else:
                self.MovingInfo['v_dir'] = -1


            self.OnMoving = True
            self.animation_ind = 0
            self.resource -= self.resource_drain

            return moving , msg

    def Attack(self,coords,target_unit):
        if 'Ranged' in self.attacks_types:
            return self.Range_Attack(coords, target_unit, 'Arrow')
        elif 'Melee' in self.attacks_types:
            return self.Melee_Attack(coords, target_unit)
        if 'Magic' in self.attacks_types:
            return self.Range_Attack(coords, target_unit, 'MagicBolt')

    def Range_Attack(self, coords, target_unit, projectile_name):

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
            Projectile  = Weapon(projectile_name, self.pos, coords)
            IsShoted = True
            range_check = [ar > distance for ar in ranges]
            range_ind = range_check.index(True)   #Finding the first True
            damage = self.attacks[range_ind]['damage']
            att_accuracy = self.attacks[range_ind]['accuracy']
            
            if att_accuracy <= (100-accuracy):
                IsShoted = False

            if not IsShoted:
                if projectile_name == 'Arrow':
                    #Failed coords
                    nexp = random.randint(0,10)
                    x_rand = coords[0] + (-1)**nexp*random.randint(int(0.1*coords[0]),int(0.2*coords[0]))
                    y_rand = coords[1] + (-1)**nexp*random.randint(int(0.1*coords[1]),int(0.2*coords[1]))
                    coords = [x_rand,y_rand]
                elif projectile_name == 'MagicBolt':
                    Projectile.kill()
                    return False, 'accuracy'

            damage_value, critical = DamageCalculation(self.name, damage)
            ytraj , xtraj, dtraj = CreateTrajectory(Projectile.pos,coords, projectile_name, get_gradient=True)

            d_x = coords[0] - Projectile.pos[0]

            if d_x<0:
                if self.rect_ind == 0:
                    self.rect_ind = self.movement_sprites[0]
                    self.ChangeSprite()
            elif d_x>0:
                if self.rect_ind == self.movement_sprites[0]:
                    self.rect_ind = 0
                    self.ChangeSprite()

            # Attack Animation
            if d_x>=0:
                animate_mode = 'Attack-Right'
            else:
                animate_mode = 'Attack-Left'

            Dt = 12 # Milisecond
            if animate_mode == 'Attack-Right':
                initial_frame = sum(self.movement_sprites)
            else:
                initial_frame = sum(self.movement_sprites) + self.attack_sprites[0]

            initial_rect_ind = self.rect_ind

            for frame in range(self.attack_sprites[0]):
                self.rect_ind = initial_frame + frame
                self.ChangeSprite()
                SCREEN.fill(SCREEN_COLOR)
                pg.draw.line(SCREEN,color=(0,0,0),start_pos=(0,LINE_DOWN),end_pos=(SCREEN_WIDTH,LINE_DOWN),width=2)
                Logger.info()
                General_Blit()                
                pg.display.flip()
                clock.tick(Dt)

            # initializing the arrow
            ALL_OBJECTS.add(Projectile)
            self.weapon = Projectile                      
            self.resource -= self.resource_drain
            # Restoring unit frame
            self.rect_ind = initial_rect_ind
            self.ChangeSprite()

            Projectile.Trajectory['xtraj'] = xtraj
            Projectile.Trajectory['ytraj'] = ytraj
            Projectile.Trajectory['dtraj'] = dtraj
            Projectile.IsShoted = IsShoted
            Projectile.run_animation = True

            # setting the projectile in the initial position
            theta = arctan(-dtraj[0])*180/pi
            Projectile.rect_ind = int((theta-Projectile.angle0)*Projectile.number_of_sprites/Projectile.angle_range)
            Projectile.rect.center = (xtraj[0] + Projectile.traj_offset[0], \
                ytraj[0] + Projectile.traj_offset[1])
            Projectile.ChangeSprite()

            if target_unit:
                Projectile.TargetUnit = target_unit

            if not IsShoted:
                return False, 'accuracy'
            else:
                Projectile.msg = [damage_value,critical]
                if not target_unit:
                    self.damage_text = DisplayDamage([damage_value,critical])
                else:
                    self.damage_text = DisplayDamage([damage_value,critical],target_unit.rect.midtop)
                    target_unit.hp -= damage_value
                    if target_unit.hp < 0:
                        target_unit.Died()

                    if critical == 'critical':
                        Logger.info(['Critical hit!', 1], holdtime = 2)
                
                return True, [damage_value,critical]

    def Melee_Attack(self, coords, target_unit):

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
            IsDone = True
            damage = self.attacks[0]['damage']
            att_accuracy = self.attacks[0]['accuracy']
            
            if att_accuracy <= (100-accuracy):
                IsDone = False

            if not IsDone:
                #Failed coords
                nexp = random.randint(0,10)
                x_rand = coords[0] + (-1)**nexp*random.randint(int(0.1*coords[0]),int(0.15*coords[0]))
                y_rand = coords[1] + (-1)**nexp*random.randint(int(0.1*coords[1]),int(0.15*coords[1]))
                coords = [x_rand,y_rand]

            damage_value, critical = DamageCalculation(self.name, damage)
            d_x = coords[0] - self.pos[0]

            if d_x<0:
                if self.rect_ind == 0:
                    self.rect_ind = self.movement_sprites[0]
                    self.ChangeSprite()
                initial_frame = sum(self.movement_sprites) + self.attack_sprites[0]

            else:
                if self.rect_ind == self.movement_sprites[0]:
                    self.rect_ind = 0
                    self.ChangeSprite()

                initial_frame = sum(self.movement_sprites)


            Dt = 12 # Milisecond
            initial_rect_ind = self.rect_ind

            for frame in range(self.attack_sprites[0]):
                self.rect_ind = initial_frame + frame
                self.ChangeSprite()
                
                SCREEN.fill(SCREEN_COLOR)
                pg.draw.line(SCREEN,color=(0,0,0),start_pos=(0,LINE_DOWN),end_pos=(SCREEN_WIDTH,LINE_DOWN),width=2)
                Logger.info()

                General_Blit()                

                pg.display.flip()
                clock.tick(Dt)

                     
            self.resource -= self.resource_drain
            # Restoring unit frame
            self.rect_ind = initial_rect_ind
            self.ChangeSprite()

            if not IsDone:
                return False, 'accuracy'
            else:
                if not target_unit:
                    self.damage_text = DisplayDamage([damage_value,critical])
                else:
                    self.damage_text = DisplayDamage([damage_value,critical],target_unit.rect.midtop,)
                    # inflicting damage into the target
                    target_unit.hp -= damage_value
                    if target_unit.hp < 0:
                        target_unit.Died()

                return True, [damage_value,critical]

    def Eat(self):

        if self.hp == self.full_hp:
            return False, 'full_hp'

        circle = pg.sprite.Sprite()
        #circle_draw = pg.draw.circle(SCREEN,color=(255,102,102),center=(self.rect.centerx,self.rect.centery),
        #             radius=self.mov_range,width=2)
        
        circle.rect = self.rect
        circle.radius = self.mov_range*0.6

        # Looking for food in the mov range
        # Fruits
        Fruits_nearby = []
        mean_hp_gains = []
        for object_ in ALL_OBJECTS.sprites():
            if 'FruitGroup' in vars(object_):
                for fruit_ in object_.FruitGroup:
                    #S  = pg.sprite.spritecollide(circle, object_.FruitGroup, True, pg.sprite.collide_circle())
                    if pg.sprite.collide_circle(circle,fruit_):
                        Fruits_nearby.append(fruit_)
                        mean_hp_gains.append(sum(fruit_.hp_gain)/2)
        
        if not Fruits_nearby:
            return False , 'no_food'


        food = Fruits_nearby[mean_hp_gains.index(max(mean_hp_gains))]
        coords = [food.rect.centerx,food.rect.centery]
        move, msg = self.Move(coords, forced=True)
        # FIXME: i need some structure to wait till the movement is finished!
        #self.IsMoving = True

        # healing
        hp_gain = random.randint(food.hp_gain[0],food.hp_gain[1])
        self.hp += hp_gain
        if self.hp > self.full_hp:
            self.hp = self.full_hp
        

        self.healing_text = DisplayDamage([self.rect.centerx,self.rect.centery],[-hp_gain,msg])
        self.Talk('yummy')
        food.kill()

        return True , ''

    def Gather(self):

        circle = pg.sprite.Sprite()        
        circle.rect = self.rect
        circle.radius = self.mov_range*0.6

        # Looking for food in the mov range
        # Fruits
        source_nearby = []
        distance = []

        for object_ in ALL_OBJECTS.sprites():
            if 'FruitGroup' in vars(object_):
                if len(object_.FruitGroup.sprites()) > 0:
                    if pg.sprite.collide_circle(circle, object_):
                        source_nearby.append(object_)
                        distance.append(DistanceBetween(self,object_))

        if not source_nearby:
            return False , 'no_food'

        gather_source = source_nearby[distance.index(min(distance))]
        direction_right = (gather_source.rect.centerx - self.rect.centerx) > 0

        if direction_right:
            coords = tuple(map(operator.add, gather_source.rect.bottomleft, gather_source.rect.midbottom))
            self.work_direction = 'right'
        else:
            coords = tuple(map(operator.add, gather_source.rect.bottomright, gather_source.rect.midbottom))
            self.work_direction = 'left'
        

        coords = [coords[0]*0.5,coords[1]*0.5]

        self.Move(coords, forced=True)
        self.Talk('let\'s work!')
        self.GatheringObject.add(gather_source)

        return True , ''

    def Work(self):

        # Fetch a work source
        circle = pg.sprite.Sprite()
        circle.rect = self.rect
        circle.radius = self.mov_range*0.6

        # Looking for food in the mov range
        # Fruits
        source_nearby = []
        distance_between = []
        for object_ in ALL_OBJECTS.sprites():
            if 'resource' in vars(object_):
                if pg.sprite.collide_circle(circle,object_):
                    source_nearby.append(object_)
                    distance_between.append(DistanceBetween(self,object_))
        

        if not source_nearby:
            return False , 'no_work_source'

        work_source = source_nearby[distance_between.index(min(distance_between))]
        direction_right = (work_source.rect.centerx - self.rect.centerx) > 0

        if direction_right:
            coords = tuple(map(operator.add, work_source.rect.bottomleft, work_source.rect.midbottom))
            self.work_direction = 'right'
        else:
            coords = tuple(map(operator.add, work_source.rect.bottomright, work_source.rect.midbottom))
            self.work_direction = 'left'
        
        coords = [coords[0]*0.5,coords[1]*0.5]
        
        self.Move(coords, forced = True)
        self.Talk('let\'s work!')
        self.WorkingObject.add(work_source)

        return True , ''

    def Talk(self, msg):
        self.phrase = msg
        ALL_CHATS.add(Bar(self,mode='chat'))

    def Died(self):
        
        sheet , rect_frames = ReadSpriteSheet(main_dir + '/data/characters/Archer/Archer01_died_ss.png' , [2,2] , 4)
        if self.rect_ind==0:
            rect = pg.Rect(rect_frames[0])
        else:
            rect = pg.Rect(rect_frames[2])
        rect_size0 = rect.size
        surf = pg.Surface(rect_size0, pg.SRCALPHA)
        surf.blit(sheet, (0, 0), rect)
        
        rect = surf.get_rect(center=(self.pos[0],self.pos[1]))
        surf = pg.transform.scale(surf, (int(rect_size0[0]*self.scale_factor), int(rect_size0[1]*self.scale_factor)))
        
        corpse = pg.sprite.Sprite()
        corpse.surf = surf
        corpse.rect = rect
        corpse.name = 'corpse'
        corpse.HasBar = None
        corpse.run_animation = False
        ALL_OBJECTS.add(corpse)

        self.kill()

    def animate(self, mode):

        run_animation = True

        if mode == 'Work':
            if self.work_direction == 'right':
                initial_frame = sum(self.movement_sprites)
                last_frame = sum(self.movement_sprites) + self.working_sprites[0]
            elif self.work_direction == 'left':
                initial_frame = sum(self.movement_sprites) + self.working_sprites[0]
                last_frame = sum(self.movement_sprites) + sum(self.working_sprites)
            else:
                raise Exception(self.self.work_direction,'not recognized')

        elif mode == 'Gather':
            if self.work_direction == 'right':
                initial_frame = sum(self.movement_sprites) + sum(self.working_sprites)
                last_frame = sum(self.movement_sprites) + sum(self.working_sprites) + self.gathering_sprites[0]
            elif self.work_direction == 'left':
                initial_frame = sum(self.movement_sprites) + sum(self.working_sprites) + self.gathering_sprites[0]
                last_frame = sum(self.movement_sprites) + sum(self.working_sprites) + sum(self.gathering_sprites)
            else:
                raise Exception(self.self.work_direction,'not recognized')


        elif mode == 'Move':
            initial_frame = self.MovingInfo['sprites'][0]
            last_frame = self.MovingInfo['sprites'][1]
            collide = False
            on_bridge = False
            objects_with_obs = []

            for obj in ALL_OBJECTS:
                if 'ObstacleGroup' in vars(obj):
                    objects_with_obs.append(obj)
                if obj.name == 'Bridge':
                    if pg.sprite.collide_rect(self.feet,obj.bridge_reduced):
                        on_bridge = True
            
            
            if abs(self.pos[0] - self.MovingInfo['coords'][0])>2 and (self.MovingInfo['h_dir']!=0):
                self.rect.move_ip(self.speed*self.MovingInfo['h_dir'],0)
                self.feet.rect.move_ip(self.speed*self.MovingInfo['h_dir'],0)
                self.pos[0] += self.speed*self.MovingInfo['h_dir']
                if self.animation_ind >22 and not on_bridge:
                    for obj in objects_with_obs:
                        for elem in obj.ObstacleGroup:
                            if pg.sprite.collide_rect(self.feet,elem):
                                self.MovingInfo['h_dir'] = 0
                                collide = True
                                break
            else:
                self.MovingInfo['h_dir'] = 0

            if abs(self.pos[1] - self.MovingInfo['coords'][1])>2 and (self.MovingInfo['v_dir']!=0):
                self.rect.move_ip(0,self.speed*self.MovingInfo['v_dir'])
                self.feet.rect.move_ip(0,self.speed*self.MovingInfo['v_dir'])
                self.pos[1] += self.speed*self.MovingInfo['v_dir']
                if self.animation_ind >22 and not on_bridge:
                    for obj in objects_with_obs:
                        for elem in obj.ObstacleGroup:
                            if pg.sprite.collide_rect(self.feet,elem):
                                self.MovingInfo['v_dir'] = 0
                                collide = True
                                break
            else:
                self.MovingInfo['v_dir'] = 0
            
            if self.MovingInfo['h_dir'] == 0 and self.MovingInfo['v_dir'] == 0:
                # Ending the movement
                run_animation = False
                self.OnMoving = False
                if self.MovingInfo['right/left'] == 'right':
                    self.rect_ind = 0
                else:
                    self.rect_ind = self.movement_sprites[0]
                
                self.MovingInfo['sprites'] = []
                self.animation_ind = 0
                self.ChangeSprite()
                
                # move away from the collided object if any
                n = 0
                while collide and n<2:
                    self.rect.move_ip(-self.speed*10,0)
                    self.pos[0] -= self.speed*10
                    self.feet.rect.move_ip(-self.speed*10,0)
                    n += 1
                    for obj in ALL_OBJECTS:
                        if obj.name == 'River':
                            if not pg.sprite.collide_rect(self.feet,obj):
                                collide = False
                                break

                # Keep player on the SCREEN
                if self.rect.left < 0:
                    self.rect.left = 0
                if self.rect.right > SCREEN_WIDTH:
                    self.rect.right = SCREEN_WIDTH  
                if self.rect.top <= LINE_UP:
                    self.rect.top = LINE_UP
                if self.rect.bottom >= LINE_DOWN:
                    self.rect.bottom = LINE_DOWN
                
                Logger.info([self.Player_name + ' had moved' , 1], holdtime = 2)
            
        if run_animation:
            if self.animation_ind == 0:
                self.rect_ind = initial_frame

            self.animation_ind += 1

            if self.animation_ind%self.SPI == 0:
                self.ChangeSprite()
                self.rect_ind += 1

                if self.rect_ind == last_frame:
                    self.animation_ind = 0

class Weapon(pg.sprite.Sprite):
    def __init__(self , name , pos, coords=[]):
        super(Weapon, self).__init__()

        if name == 'Arrow':
            self.name = 'Arrow'
            self.speed = 10
            self.SPI = 2
            self.offset = [0,-8]
            self.traj_offset = [0,0]
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
                

            self.scale_factor = 0.9
            self.angle0 = -90
            self.angle_range = 180
            self.rect_ind = 0
            rect = pg.Rect(self.rect_frames[self.rect_ind])
            self.rect_size0 = rect.size
            surf = pg.Surface(self.rect_size0, pg.SRCALPHA)
            surf.blit(self.sheet, (0, 0), rect)
            self.rect = surf.get_rect(center=(self.pos[0],self.pos[1]))
            size = surf.get_size()
            self.surf = pg.transform.scale(surf, (int(size[0]*self.scale_factor), int(size[1]*self.scale_factor)))
            self.size = self.surf.get_size()
            self.Trajectory = {'xtraj': None , 'ytraj': None, 'dtraj': None}
            self.duration = 90
            self.time_on_ground = 0
            self.msg = None
            self.TargetUnit = None
        
        elif name == 'MagicBolt':
            self.name = 'MagicBolt'
            self.speed = 40
            self.SPI = 2
            self.offset = [40,0]
            self.traj_offset = [60,60]
            self.target = coords
            self.pos = [pos[0]+self.offset[0], pos[1]+self.offset[1]]
            self.RC_tup = [6,7]
            self.number_of_sprites = 41

            if (coords[0] - self.pos[0])>0:
                self.sheet , self.rect_frames = ReadSpriteSheet(main_dir + '/data/characters/Wizard/' + name + '01_ss.png' , 
                             self.RC_tup , self.number_of_sprites)
            else:
                self.sheet , self.rect_frames = ReadSpriteSheet(main_dir + '/data/characters/Wizard/' + name + '02_ss.png' , 
                             self.RC_tup , self.number_of_sprites)
                

            self.scale_factor = 0.3
            self.angle0 = -90
            self.angle_range = 180
            self.rect_ind = 0
            rect = pg.Rect(self.rect_frames[self.rect_ind])
            self.rect_size0 = rect.size
            surf = pg.Surface(self.rect_size0, pg.SRCALPHA)
            surf.blit(self.sheet, (0, 0), rect)
            self.rect = surf.get_rect(center=(self.pos[0],self.pos[1]))
            size = surf.get_size()
            self.surf = pg.transform.scale(surf, (int(size[0]*self.scale_factor), int(size[1]*self.scale_factor)))
            self.size = self.surf.get_size()
            self.Trajectory = {'xtraj': None , 'ytraj': None, 'dtraj': None}
            self.msg = None
            self.TargetUnit = None
            self.duration = 1
            self.time_on_ground = 0
        

        self.damage_text = None
        self.damage_duration = 0
        self.animation_ind = 0
        self.HasBar = False
        self.run_animation = False
        self.IsShoted = False
    
    def ChangeSprite(self):
        rect = pg.Rect(self.rect_frames[self.rect_ind])
        surf = pg.Surface(self.rect_size0 ,pg.SRCALPHA)
        surf.blit(self.sheet, (0, 0), rect)
        self.surf = pg.transform.scale(surf, (self.size[0], self.size[1]))

    def animate(self):

        run_animation = True

        if self.animation_ind == len(self.Trajectory['xtraj']):
            # Ending the movement
            run_animation = False
            
            if self.name == 'Arrow':
                if abs(arctan(-self.Trajectory['dtraj'][self.animation_ind-1])*180/pi) < 15:
                    # Keeping the arrow vertical when landed it
                    self.rect_ind = random.randint(0,5)
                    self.ChangeSprite()

            self.Trajectory = {'xtraj': None , 'ytraj': None, 'dtraj': None}     
            self.animation_ind = 0
            self.run_animation = False
            self.time_on_ground = clock.get_time()
            self.damage_duration = self.time_on_ground
            

        if run_animation:

            xtraj = self.Trajectory['xtraj']
            ytraj = self.Trajectory['ytraj']
            dtraj = self.Trajectory['dtraj']
            

            if self.animation_ind%self.SPI == 0:
                theta = arctan(-dtraj[self.animation_ind])*180/pi
                if not self.IsShoted:
                    theta += random.randint(-15,15)
                    if abs(int(theta-self.angle0)) >= 180:
                        theta = arctan(-dtraj[self.animation_ind])*180/pi

                self.rect_ind = int((theta-self.angle0)*self.number_of_sprites/self.angle_range)
                self.rect.center = (xtraj[self.animation_ind] + self.traj_offset[0], \
                    ytraj[self.animation_ind] + self.traj_offset[1])
                self.ChangeSprite()
            

            self.animation_ind += 1

class Bar(pg.sprite.Sprite):
    def __init__(self, unit, mode = None):
        super(Bar, self).__init__()

        self.path = main_dir + '/data/objects/info/'
        self.unit_for = unit

        if not mode:
            self.mode = 'bar'
        else:
            self.mode = mode

        if self.mode == 'info':
            self.RC_tup = [2,3]
            self.scale_factor = 0.7
            if 'offsets' in vars(unit):
                self.x_offset = unit.offsets['bar'][0]
                self.y_offset = unit.offsets['bar'][1]
            else:
                self.x_offset = 60
                self.y_offset = 2
            self.number_images = 6
            if type(unit).__name__ == 'Unit':
                image_name = 'info01_ss.png'
                self.sheet , self.rect_frames = ReadSpriteSheet(self.path + image_name  , self.RC_tup, self.number_images)
                if unit.resource == 0:
                    rect = pg.Rect(self.rect_frames[5])
                else:
                    ind = -(-self.number_images*unit.resource//unit.full_resource)
                    rect = pg.Rect(self.rect_frames[self.number_images-ind])

                self.surf = pg.Surface(rect.size,pg.SRCALPHA)
                self.surf.blit(self.sheet, (0, 0), rect)
                #self.surf.set_colorkey((0,0,0), RLEACCEL)
            elif type(unit).__name__ == 'Object':
                image_name = 'info02.png'
                self.scale_factor = 0.5
                self.surf = pg.image.load(self.path + image_name ).convert_alpha()

        elif self.mode == 'bar':
            self.scale_factor = 0.7
            if 'offsets' in vars(unit):
                self.x_offset = unit.offsets['bar'][0]
                self.y_offset = unit.offsets['bar'][1]
            else:
                self.x_offset = 60
                self.y_offset = 2
            image_name = 'info03.png'
            self.surf = pg.image.load(self.path + image_name ).convert_alpha()

        elif self.mode == 'chat':
            image_name = 'chat.png'
            self.duration = 1000        # duration in milisecond
            self.initial_t = clock.get_time()
            self.current_t = self.initial_t
            self.RC_tup = [1,2]
            self.scale_factor = 1.5
            self.number_images = 2
            self.x_offset = 30
            self.y_offset = -20
            self.sheet , self.rect_frames = ReadSpriteSheet(self.path + image_name  , self.RC_tup, self.number_images)
            if unit.rect_ind == 0:
                rect = pg.Rect(self.rect_frames[0])
            else:
                rect = pg.Rect(self.rect_frames[1])
            
            self.surf = pg.Surface(rect.size,pg.SRCALPHA)
            self.surf.blit(self.sheet, (0, 0), rect)
            self.surf.set_colorkey((0,0,0), RLEACCEL)
            

        self.size0 = self.surf.get_size()
        self.rect = self.surf.get_rect()
        self.rect.x = unit.rect.x + self.x_offset
        self.rect.y = unit.rect.y + self.y_offset
        self.surf = pg.transform.scale(self.surf,(int(self.size0[0]*self.scale_factor),int(self.size0[1]*self.scale_factor) ))
        self.size = self.surf.get_size()
        self.TextGroup = pg.sprite.Group()

        if self.mode == 'info':
            if type(unit).__name__ == 'Unit':
                # Hp info
                hp_text, _ = GAME_FONT.render(str(unit.hp) + '/' + str(unit.full_hp), (0, 0, 0) , size=12)
                hp_sprite = pg.sprite.Sprite()
                hp_sprite.surf = hp_text
                hp_sprite.rect = (self.rect.x + self.size[0]*0.38, self.rect.y+ self.size[1]*0.23)
                self.TextGroup.add(hp_sprite)
                # Name info
                name_text, _ = GAME_FONT.render(unit.name, (0, 0, 0) , size=16)
                size_unit = unit.size
                name_sprite = pg.sprite.Sprite()
                name_sprite.surf = name_text
                name_offsets = unit.offsets['name']
                name_sprite.rect = (unit.rect.x + name_offsets[0],unit.rect.y + name_offsets[1])
                self.TextGroup.add(name_sprite)
                # Resource Info
                resource_text, _ = GAME_FONT.render(unit.resource_name, (0, 0, 0) , size=12)
                resource_name_sprite = pg.sprite.Sprite()
                resource_name_sprite.surf = resource_text
                resource_name_sprite.rect = (self.rect.x + self.size[0]*0.25, self.rect.y+ self.size[1]*0.5)
                self.TextGroup.add(resource_name_sprite)
            elif type(unit).__name__ == 'Object':
                name_text, _ = GAME_FONT.render(unit.name, (0, 0, 0) , size=12)
                text_name_sprite = pg.sprite.Sprite()
                text_name_sprite.surf = name_text
                text_name_sprite.rect = (unit.rect.x + 79, unit.rect.y + 10)
                self.TextGroup.add(text_name_sprite)
                # Resource info
                res_text, _ = GAME_FONT.render(str(unit.resource) + '/' + str(unit.full_resource), (0, 0, 0) , size=10)
                res_sprite = pg.sprite.Sprite()
                res_sprite.surf = res_text
                res_sprite.rect = (unit.rect.x + 75, unit.rect.y+30)
                self.TextGroup.add(res_sprite)

        elif self.mode == 'bar':
            up_text, _ = GAME_FONT.render(unit.actions_lst[0], (0, 0, 0) , size=12)
            down_text, _ = GAME_FONT.render(unit.actions_lst[1], (0, 0, 0) , size=12)
            self.text_x = self.rect.x + self.size[0]*0.2
            self.text_upy = self.rect.y + self.size[1]*(0.44-0.25)
            self.text_dwny = self.rect.y + self.size[1]*(0.44+0.25)
            Text_up = pg.sprite.Sprite()
            Text_down = pg.sprite.Sprite()
            Text_up.surf = up_text ; Text_up.rect = (self.text_x,self.text_upy)
            Text_down.surf = down_text; Text_down.rect = (self.text_x,self.text_dwny)
            self.TextGroup.add(Text_up)
            self.TextGroup.add(Text_down)
            # Name Text
            name_text, _ = GAME_FONT.render(unit.name, (0, 0, 0) , size=16)
            size_unit = unit.size
            name_sprite = pg.sprite.Sprite()
            name_sprite.surf = name_text
            if 'offsets' in vars(unit):
                name_offsets = unit.offsets['name']

            if unit.name == 'House':
                name_sprite.rect = (unit.rect.bottomleft[0]+ size_unit[0]*0.15,unit.rect.midbottom[1])
            else:
                name_sprite.rect = (unit.rect.x + name_offsets[0],unit.rect.y + name_offsets[1])


            self.TextGroup.add(name_sprite)

        elif self.mode == 'chat':
            #surface.get_width()
            #surface.get_height()
            text, _ = GAME_FONT.render(unit.phrase, (0, 0, 0) , size=12)
            size_unit = unit.size
            chat_sprite = pg.sprite.Sprite()
            chat_sprite.surf = text
            chat_sprite.rect = (self.rect.centerx-20, self.rect.centery-5)
            self.TextGroup.add(chat_sprite)
            
    def get_buttoms(self):

        Movex = self.rect.x + self.size[0]*0.2
        Movey = self.rect.y + self.size[1]*(0.44-0.25)
        Attackx = self.rect.x + self.size[0]*0.2
        Attacky = self.rect.y + self.size[1]*(0.44+0.25)
        
        buttoms = {}
        buttoms['Up'] = [Movex, Movey, self.size[0],self.size[1]*0.5]
        buttoms['Down'] = [Attackx, Attacky, self.size[0],self.size[1]*0.5]
        

        return buttoms
    
    def is_click(self, mouse_pos, unit):
        '''
            if there is a click in the Action Bar buttoms
        '''

        xoffset = 40
        yoffset_D = 8
        yoffset_U = 0
        xshift = 6
        yshift = -6

        if unit.name == 'House':
            xoffset = 35
            yoffset_U = 6.3
            yoffset_D = 8
            xshift = 6
            yshift = -6.4

        isclick = False

        B_move = unit.ActionBar_buttoms['Up']
        B_move_rx = (B_move[0] + B_move[2]*0.5 - (B_move[0] - B_move[2]*0.5) - xshift )*0.5
        B_move_x0 =  B_move[0]
        B_move_ry = (B_move[1] + B_move[3]*0.5 - (B_move[1] - B_move[3]*0.5) - yshift )*0.5
        B_move_y0 =  B_move[1]
        B_attack_y0 = unit.ActionBar_buttoms['Down'][1]

        #print(mouse_pos[0], B_move_x0 + xoffset ,B_move_x0 + xoffset - B_move_rx*0.5, B_move_x0 + xoffset + B_move_rx*0.5 , B_move_rx )
        #print(mouse_pos[1], B_move_y0 + yoffset_U ,B_move_y0 + yoffset_U - B_move_ry*0.5, B_move_y0 + yoffset_U + B_move_ry*0.5 , B_move_ry )
        #print(abs(mouse_pos[0] - (B_move_x0 + xoffset)) < B_move_rx)
        #print(abs(mouse_pos[1] - (B_move_y0 + yoffset_U)) < B_move_ry)


        if abs(mouse_pos[0] - (B_move_x0 + xoffset)) < B_move_rx :
            if abs(mouse_pos[1] - (B_move_y0 + yoffset_U)) < B_move_ry :
                if unit.name != 'House':
                    unit.assign_action(unit.actions_lst[0])
                else:
                    unit.IsBuying = True
                unit.action_updown = [1,0]
                isclick = True
                image_name = 'info04.png'
                self.surf  = ChangeImage(self.path + image_name, self.size)
                return isclick
        

        if abs(mouse_pos[0] - (B_move_x0 + xoffset)) < B_move_rx :
            if abs(mouse_pos[1] - (B_attack_y0 + yoffset_D)) < B_move_ry :
                if unit.name != 'House':
                    unit.assign_action(unit.actions_lst[1])
                else:
                    unit.IsUpgrading = True
                unit.action_updown = [0,1]
                isclick = True
                image_name = 'info05.png'
                self.surf  = ChangeImage(self.path + image_name, self.size)
                return isclick
        
    def change_action_text(self, unit):
        if self.mode != 'bar':
            pass
        else:
            self.TextGroup.empty()

            up_text, _ = GAME_FONT.render(unit.actions_lst[0], (0, 0, 0) , size=12)
            down_text, _ = GAME_FONT.render(unit.actions_lst[1], (0, 0, 0) , size=12)
            Text_up = pg.sprite.Sprite()
            Text_down = pg.sprite.Sprite()
            Text_up.surf = up_text ; Text_up.rect = (self.text_x,self.text_upy)
            Text_down.surf = down_text; Text_down.rect = (self.text_x,self.text_dwny)
            self.TextGroup.add(Text_up)
            self.TextGroup.add(Text_down)
            # Name Text
            name_text, _ = GAME_FONT.render(unit.name, (0, 0, 0) , size=16)
            size_unit = unit.size
            name_sprite = pg.sprite.Sprite()
            name_sprite.surf = name_text
            name_sprite.rect = (unit.rect.x - size_unit[0]*0.35,unit.rect.y - size_unit[1]*0.28)
            self.TextGroup.add(name_sprite)

class Object(pg.sprite.Sprite):
    def __init__(self , name , pos , player_name=None):
        super(Object, self).__init__()

        self.pos = pos
        self.data = obj_dct[name]
        self.name = name
        if player_name:
            self.player_name = player_name

        # Image
        self.scale_factor = self.data['Image']['scale_factor']
        self.number_of_sprites = self.data['Image']['number_of_sprites']
        self.RC_tup = self.data['Image']['RowColumn_tup']
        self.path_to_ss = main_dir + self.data['path']
        self.SPI = self.data['Image']['SpritesPerIter']

        if len(self.data['types'])>1 and player_name:
            types = self.data['types']
            if 'A' in player_name: 
                self.path_to_ss = self.path_to_ss.format(i=types[0])
            elif 'B' in player_name:
                self.path_to_ss = self.path_to_ss.format(i=types[1])

        # Sprite
        self.sheet , self.rect_frames = ReadSpriteSheet(self.path_to_ss, self.RC_tup , self.number_of_sprites )
        rect = pg.Rect(self.rect_frames[0])
        self.rect_size0 = rect.size
        self.rect_ind = 0
        surf = pg.Surface(self.rect_size0, pg.SRCALPHA)
        #surf.set_colorkey((0,0,0), RLEACCEL)
        surf.blit(self.sheet, (0, 0), rect)

        self.surf = pg.transform.scale(surf, (int(self.rect_size0[0]*self.scale_factor), int(self.rect_size0[1]*self.scale_factor)))
        self.rect = self.surf.get_rect(center=(self.pos[0],self.pos[1]))
        self.size = self.surf.get_size()

        # Home Action Bar
        if self.name == 'House':
            self.action_updown = [0,0]
            self.actions_cycle_base = []
            for k in range(int((len(self.data['actions']) +1)/2)):
                if 2*k+1 == len(self.data['actions']):
                    self.actions_cycle_base.append([self.data['actions'][2*k] , ''])
                else:
                    self.actions_cycle_base.append([self.data['actions'][2*k] , self.data['actions'][2*k+1]])

            self.actions_cycle = cycle(self.actions_cycle_base)
            self.actions_lst = next(self.actions_cycle)
            self.ActionBar_buttoms = {'Up': [] , 'Down': []}
            self.ActionBar = None
            self.IsBuying = False
            self.IsUpgrading = False


        if self.name == 'Bridge':
            self.bridge_reduced = pg.sprite.Sprite()
            self.bridge_reduced.rect = self.rect.inflate((-30,-60))

        # Resources
        self.HasBar = None
        if 'Resources' in self.data:
            self.resource_name = self.data['Resources']['resource']
            self.full_resource = self.data['Resources']['full_resource']
            self.resource = self.full_resource
            self.resource_drain = self.data['Resources']['resource_drain']
            self.HasBar = True

        if 'Fruit' in self.data:
            self.FruitGroup = pg.sprite.Group()
            self.fruit_capacity = self.data['Fruit']['capacity']

        if 'Obstacles' in self.data:
            self.ObstacleGroup = pg.sprite.Group()
            for r_ in self.data['Obstacles']:
                obstacle = pg.sprite.Sprite()
                obstacle.rect = pg.Rect((\
                    self.rect.centerx + r_[0], \
                    self.rect.centery + r_[1], \
                    r_[2], \
                    r_[3]))
                self.ObstacleGroup.add(obstacle)

        # video
        self.run_animation = False
        self.DisplayActionBar = False
        self.animation_ind = 0 

    def ChangeSprite(self):
        rect = pg.Rect(self.rect_frames[self.rect_ind])
        surf = pg.Surface(self.rect_size0 ,pg.SRCALPHA)
        surf.blit(self.sheet, (0, 0), rect)
        self.surf = pg.transform.scale(surf, (self.size[0], self.size[1]))

    def animate(self, backwards = False):
        self.animation_ind += 1
        if self.animation_ind%self.SPI == 0:
            self.rect_ind +=1
            self.surf, self.rect = ChangeSprite(self.rect_frames, self.rect_size0 , 
                            self.sheet , self.pos, self.size, self.rect_ind)

            if self.rect_ind+1  == self.number_of_sprites:
                self.rect_ind = 0
                self.animation_ind = 0
                self.run_animation = False
                if backwards:
                    self.rect_frames.reverse()
                else:
                    self.surf, self.rect = ChangeSprite(self.rect_frames, self.rect_size0 , 
                                    self.sheet , self.pos, self.size, self.rect_ind)
    
    def grown_fruit(self):
        if len(self.FruitGroup.sprites()) >= (self.fruit_capacity ):
            pass
        else:
            fruit =  pg.sprite.Sprite()
            fruit.name = self.data['Fruit']['name']
            
            RC_tup = obj_dct['Food'][fruit.name]['RC_tup']
            scale_factor = obj_dct['Food'][fruit.name]['scale_factor']
            number_of_sprites = obj_dct['Food'][fruit.name]['number_of_sprites']


            path_to_ss = main_dir + obj_dct['Food'][fruit.name]['path']
            sheet , rect_frames = ReadSpriteSheet(path_to_ss , RC_tup , number_of_sprites)
            
            if number_of_sprites == 1:
                rect_ind = 0
            else:
                rect_ind = random.randint(0,number_of_sprites-1)
            
            rect = pg.Rect(rect_frames[rect_ind])
            rect_size0 = rect.size
            surf = pg.Surface(rect_size0, pg.SRCALPHA)
            surf.blit(sheet, (0, 0), rect)

            surf = pg.transform.scale(surf, (int(rect_size0[0]*scale_factor), int(rect_size0[1]*scale_factor)))

            fruit.surf = surf
            fruit.hp_gain = obj_dct['Food'][fruit.name]['hp_gain']
            f_yrandom = random.randint(0,100)
            f_xrandom = random.randint(0,100)
            offset = self.data['Fruit']['offset']
            yfr = self.rect.centery + offset[1]  + (f_yrandom-50)*(self.size[1]*0.36)/100
            xfr = self.rect.centerx + offset[0] + (f_xrandom-50)*(self.size[0]*0.5)/100
            fruit.rect = fruit.surf.get_rect(center=(xfr,yfr))

            if len(self.FruitGroup.sprites()) == 0:
                self.FruitGroup.add(fruit)
            else:
                collide = True
                NF = len(self.FruitGroup.sprites())
                tries = 50
                while collide:
                    ncheck = 0
                    for fruit_ in self.FruitGroup.sprites():
                        if abs(xfr-fruit_.rect.centerx)>6 and abs(yfr-fruit_.rect.centery)>7:
                            ncheck += 1
                        else:
                            f_yrandom = random.randint(0,100)
                            f_xrandom = random.randint(0,100)
                            yfr = self.rect.centery + offset[1] + (f_yrandom-50)*(self.size[1]*0.36)/100
                            xfr = self.rect.centerx + offset[0] + (f_xrandom-50)*(self.size[0]*0.5)/100
                            fruit.rect = fruit.surf.get_rect(center=(xfr,yfr))
                    
                    if ncheck == NF or tries == 0 :
                        collide = False
                    
                    tries -= 1
                
                fruit.rect = fruit.surf.get_rect(center=(xfr,yfr))
                self.FruitGroup.add(fruit)

    def update(self):
        if self.name == 'Rock':
            status = -(-self.number_of_sprites*self.resource//self.full_resource)
            self.rect_ind = self.number_of_sprites - status
            if self.rect_ind >= self.number_of_sprites:
                self.kill()
            else:
                self.ChangeSprite()

class Catalogue(pg.sprite.Sprite):
    def __init__(self, book):
        super(Catalogue, self).__init__()

        self.TextGroup = pg.sprite.Group()
        self.Buttoms = pg.sprite.Group()
        self.page_pos = []


        for i in range(2):
            for k in range(2):
                self.page_pos.append([book.rect.width*(0.25+i*0.44)+book.rect.x,book.rect.height*(0.25+k*0.32)+book.rect.y])


        self.name_lst = []
        self.full_hp_lst = []

        # Text
        for pos, unit in zip(self.page_pos, units_dct):
            # Name         
            text01 = units_dct[unit]['name']
            self.name_lst.append(text01)
            xoffset = -190
            yoffset = -40
            text, _ = GAME_FONT.render(text01, (0, 0, 0) , size=20)
            name_sprite = pg.sprite.Sprite()
            name_sprite.surf = text
            name_sprite.rect = [pos[0]+xoffset , pos[1] + yoffset]
            self.TextGroup.add(name_sprite)

            # Hp
            text02 = units_dct[unit]['Parameters']['full_hp']
            self.full_hp_lst.append(text02)
            xoffset = -20
            yoffset = -10
            text, _ = GAME_FONT.render('HP:' + str(text02), (0, 0, 0) , size=14)
            sprite = pg.sprite.Sprite()
            sprite.surf = text
            sprite.rect = [pos[0]+xoffset , pos[1] + yoffset]
            self.TextGroup.add(sprite)
            
            # Mov range
            text03 = units_dct[unit]['Parameters']['mov_range']
            self.full_hp_lst.append(text03)
            xoffset = -20
            yoffset = 10
            text, _ = GAME_FONT.render('Mv range:' + str(text03), (0, 0, 0) , size=14)
            sprite = pg.sprite.Sprite()
            sprite.surf = text
            sprite.rect = [pos[0]+xoffset , pos[1] + yoffset]
            self.TextGroup.add(sprite)

            # Attacks
            xoffset = -20
            yoffset = 30
            text, _ = GAME_FONT.render('Attacks:', (0, 0, 0) , size=14)
            sprite = pg.sprite.Sprite()
            sprite.surf = text
            sprite.rect = [pos[0]+xoffset , pos[1] + yoffset]
            self.TextGroup.add(sprite)

            for k, attack in enumerate(units_dct[unit]['Parameters']['attack_types']):
                for l, types_ in enumerate(units_dct[unit]['Parameters']['attack_types'][attack].keys()):
                    # Attacks types
                    if 'heal' in units_dct[unit]['Parameters']['attack_types'][attack][types_]:
                        damage = units_dct[unit]['Parameters']['attack_types'][attack][types_]['heal']
                    else:
                        damage = units_dct[unit]['Parameters']['attack_types'][attack][types_]['damage']
                    xoffset = -10
                    yoffset = 50 + l*20 + k*20
                    text, _ = GAME_FONT.render(types_ + ':' + str(damage[0]) + '-' + str(damage[1]), (0, 0, 0) , size=12)
                    sprite = pg.sprite.Sprite()
                    sprite.surf = text
                    sprite.rect = [pos[0]+xoffset , pos[1] + yoffset]
                    self.TextGroup.add(sprite)

            # Cost
            xoffset = -20
            yoffset = 95
            text, _ = GAME_FONT.render('Cost:', (0, 0, 0) , size=14)
            sprite = pg.sprite.Sprite()
            sprite.surf = text
            sprite.rect = [pos[0]+xoffset , pos[1] + yoffset]
            self.TextGroup.add(sprite)

            for k, cost in enumerate(units_dct[unit]['Parameters']['cost']):
                xoffset = 0
                yoffset = 115 + k*15
                text, _ = GAME_FONT.render(cost + ':' + str(units_dct[unit]['Parameters']['cost'][cost]) , (0, 0, 0) , size=12)
                sprite = pg.sprite.Sprite()
                sprite.surf = text
                sprite.rect = [pos[0]+xoffset , pos[1] + yoffset]
                self.TextGroup.add(sprite)

        # Images
        for pos, unit in zip(self.page_pos, units_dct):
            if unit in ['Archer','Villager','Knight']:
                xoffset = -160
                yoffset = 15

                gender = ''
                if 'gender' in units_dct[unit]:
                    gender = 'M'
                path_to_ss = main_dir + units_dct[unit]['path'] + unit + units_dct[unit]['types'][0] +gender + '_ss.png'
                RC_tup = units_dct[unit]['Image']['RowColumn_tup']
                sheet , rect_frames = ReadSpriteSheet(path_to_ss , RC_tup , units_dct[unit]['Image']['number_of_sprites'])
                rect_ind = 0

                scale_factor = units_dct[unit]['Image']['scale_factor']
                
                if type(scale_factor) == list:
                    scale_factor = 1.4*scale_factor[0]
                else:
                    scale_factor = 1.4*scale_factor

                rect = pg.Rect(rect_frames[rect_ind])
                rect_size0 = rect.size
                surf = pg.Surface(rect_size0, pg.SRCALPHA)
                surf.blit(sheet, (0, 0), rect)
                surf = pg.transform.scale(surf, (int(rect_size0[0]*scale_factor), int(rect_size0[1]*scale_factor)))
                
                sprite = pg.sprite.Sprite()
                sprite.surf = surf
                sprite.rect = [pos[0]+xoffset , pos[1] + yoffset]
                self.TextGroup.add(sprite)

        # Buttoms
        for pos, unit in zip(self.page_pos, units_dct):
            xoffset = -120
            yoffset = 150
            scale_factor = 0.35
            image_name = main_dir + '/data/objects/info/info02.png'
            surf = pg.image.load(image_name).convert_alpha()
            size = surf.get_size()
            surf = pg.transform.scale(surf,(int(size[0]*scale_factor),int(size[1]*scale_factor) ))
            sprite = pg.sprite.Sprite()
            sprite.surf = surf
            rect = surf.get_rect(center=(pos[0]+xoffset, pos[1] + yoffset))
            sprite.rect = rect
            sprite.unit = unit

            self.TextGroup.add(sprite)
            self.Buttoms.add(sprite)

            text, _ = GAME_FONT.render('Buy', (0, 0, 0) , size=14)
            text_sprite = pg.sprite.Sprite()
            text_sprite.surf = text
            text_sprite.rect = [sprite.rect.centerx-20,sprite.rect.centery-5]
            self.TextGroup.add(text_sprite)
            
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

    def Print(self, color = None):
        if color:
            text, rect = GAME_FONT.render(self.msg[0], color , size= self.fontsize)
        else:
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
GAME_FONT = pygame.freetype.Font('./data/fonts/PressStartRegular-ay8E.ttf', 32 )
GAME_FONT.origin = True
clock = pg.time.Clock()
SCREEN = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
ALL_SPRITES = pg.sprite.Group()
ALL_OBJECTS = pg.sprite.Group()
ALL_BOXES = pg.sprite.Group()
ALL_CHATS = pg.sprite.Group()
Logger = Log(SCREEN , mode = 'global')
pg.display.set_caption('strawberry bf')
Pixel2Mts = 1.7/70
Players_list = []

#pg.mixer.music.load(main_dir + '/data/music/littleroot.ogg')
pg.mixer.music.load(main_dir + '/data/music/shield.ogg')
pg.mixer.music.play(-1)


def main():
    #### Players
    Player_A = Player('Player A')
    Player_B = Player('Player B')
    Player_inturn_cycle = cycle([Player_A, Player_B])
    Player_inturn = next(Player_inturn_cycle)
    Players_list.append(Player_A)
    Players_list.append(Player_B)
    
    ####
    
    # Create a custom event for adding a new enemy
    MOVETREES = pg.USEREVENT + 1
    pg.time.set_timer(MOVETREES, 5000)
    CleanBattleField = pg.USEREVENT + 3
    pg.time.set_timer(CleanBattleField, 15000)
    HouseMovement = pg.USEREVENT + 4
    pg.time.set_timer(HouseMovement, 10000)
    Grow_Fruit = pg.USEREVENT + 5
    pg.time.set_timer(Grow_Fruit, 2500)
    RiverMovement = pg.USEREVENT + 6
    pg.time.set_timer(RiverMovement, 2000)
    
    
    # Add units to players
    Player_A.UnitsGroup.add(Unit('Archer',[300,700], Player_A.name))
    Player_A.UnitsGroup.add(Unit('Villager',[400,500], Player_A.name))
    Player_A.UnitsGroup.add(Unit('Knight',[230,700], Player_A.name))
    Player_A.UnitsGroup.add(Unit('Wizard',[730,200], Player_A.name))
    #Player_A.UnitsGroup.add(Unit('Priest',[650,250], Player_A.name))

    Player_B.UnitsGroup.add(Unit('Villager',[1400,400], Player_B.name))
    Player_B.UnitsGroup.add(Unit('Archer',[1600,250], Player_B.name))
    
    Player_B.UnitsGroup.add(Unit('Knight',[1300,820], Player_B.name))
    #Player_B.UnitsGroup.add(Unit('Wizard',[1000,420], Player_B.name))

    # Objects
    ALL_OBJECTS.add(Object('Sky',[900,0]))
    ALL_OBJECTS.add(Object('River',[830,520]))
    ALL_OBJECTS.add(Object('Bridge',[820,565]))
    

    ALL_OBJECTS.add(Object('Rock',[350,500]))
    ALL_OBJECTS.add(Object('Rock',[930,720]))
    ALL_OBJECTS.add(Object('Rock',[990,740]))
    ALL_OBJECTS.add(Object('Rock',[1250,172]))
    ALL_OBJECTS.add(Object('Rock',[230,150]))
    ALL_OBJECTS.add(Object('Rock',[200,170]))
    
    ALL_OBJECTS.add(Object('Tree',[80,500]))
    ALL_OBJECTS.add(Object('Tree',[80,300]))
    ALL_OBJECTS.add(Object('Tree',[1500,150]))
    ALL_OBJECTS.add(Object('Bush',[200,830]))
    ALL_OBJECTS.add(Object('Bush',[430,740]))
    ALL_OBJECTS.add(Object('Bush',[1230,810]))
    ALL_OBJECTS.add(Object('Bush',[1400,220]))
    
    
    # Houses
    Player_A.Home = Object('House',[120,700], Player_A.name)
    Player_B.Home = Object('House',[1600,150], Player_B.name)

    ALL_OBJECTS.add(Player_A.Home)
    ALL_OBJECTS.add(Player_B.Home)


    for Player_ in Players_list:
        for sprites_ in Player_.UnitsGroup.sprites():
            ALL_SPRITES.add(sprites_)
            
    # Main loop
    running = True
    ActionBars = False
    UnitOnAction = False
    WaitingEnd = False
    MovingUnit = {'on': False , 'coords' : []}
    AttackingUnit = {'on': False , 'target' : [], 'unit':[]}


    while running:

        SCREEN.fill(SCREEN_COLOR)
        pg.draw.line(SCREEN,color=(0,0,0),start_pos=(0,LINE_DOWN),end_pos=(SCREEN_WIDTH,LINE_DOWN),width=2)
        
        Logger.info([Player_inturn.name + ' turn', 1])
        Player_inturn.DisplayDiamonds()
        DisplayResources(Players_list)

        # Look at every event in the queue
        for event in pg.event.get():
            if event.type  == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                
                elif event.key == K_n:
                    for unit in Player_inturn.UnitsGroup:
                        if unit.DisplayActionBar and ActionBars:
                            unit.actions_lst = next(unit.actions_cycle)
                            unit.ActionBar.change_action_text(unit)
                            unit.action_updown = [0,0]
                            unit.assign_action('none')
                            MovingUnit['on'] = False
                            AttackingUnit['on'] = False
                            pg.mouse.set_cursor(pg.cursors.arrow)

                elif event.key == K_TAB:
                    num_sprites = len(Player_inturn.UnitsGroup.sprites())
                    if num_sprites>1:
                        SPRITES = Player_inturn.UnitsGroup.sprites()
                        num_sprites_c = cycle(linspace(0,num_sprites-1,num_sprites,dtype=int))
                        n_sprite = next(num_sprites_c)

                        for _ in range(num_sprites):
                            if ALL_BOXES.has(SPRITES[n_sprite].ActionBar):
                                k_old = n_sprite
                                n_sprite = next(num_sprites_c)
                                k_new = n_sprite
                            else:
                                n_sprite = next(num_sprites_c)

                            
                        SPRITES[k_old].DisplayActionBar = False
                        SPRITES[k_old].ActionBar.kill()
                        SPRITES[k_new].DisplayActionBar = True                                
                
            if event.type  == KEYUP:
                    if event.key == K_i:
                        ALL_BOXES.empty()
                        ActionBars = False

            elif event.type == QUIT:
                running = False

            elif event.type == MOVETREES:
                for obj in ALL_OBJECTS.sprites():
                    if obj.name == 'Tree':
                        coint = random.randint(0,10)
                        if coin < 5:
                            if not obj.run_animation:
                                obj.run_animation = True
                    elif obj.name == 'Bush':
                        coin = random.randint(0,10)
                        if coin < 4:
                            if not obj.run_animation:
                                obj.run_animation = True

            elif event.type == Grow_Fruit:
                for obj in ALL_OBJECTS.sprites():
                    if obj.name == 'Tree':
                        coin = random.randint(0,100)
                        if coin < 5:
                            obj.grown_fruit()
                    elif obj.name == 'Bush':
                        coin = random.randint(0,10)
                        if coin < 8:
                            obj.grown_fruit()

            elif event.type == HouseMovement:
                for obj in ALL_OBJECTS.sprites():
                    if obj.name == 'House':
                        if not obj.run_animation:
                            Coin = random.randint(0,1)
                            if Coin:
                                obj.run_animation = True

            elif event.type == RiverMovement:
                for obj in ALL_OBJECTS.sprites():
                    if obj.name == 'River':
                        obj.run_animation = True

            elif event.type == CleanBattleField:
                for entity in ALL_OBJECTS:
                    if entity.name  == 'Arrow':
                        entity.time_on_ground += clock.get_time()
                        if entity.time_on_ground >= entity.duration:
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
                        for unit in Player_inturn.UnitsGroup:
                            for abar in ALL_BOXES.sprites():
                                if unit.DisplayActionBar and unit.ActionBar:
                                    isclick = abar.is_click(pg.mouse.get_pos(), unit)
                                    if not isclick:
                                        ALL_BOXES.empty()
                                        unit.reset_bar()
                                        unit.action_updown = [0,0]
                                        unit.DisplayActionBar = False
                                        ActionBars = False
                                    else:
                                        break
                            if not ALL_BOXES.has():
                                if unit.rect.collidepoint(pg.mouse.get_pos()):
                                    unit.DisplayActionBar = True
                                    ActionBars = True
                        
                        if not ALL_BOXES.has() and not ActionBars:
                            if Player_inturn.Home.rect.collidepoint(pg.mouse.get_pos()):
                                Player_inturn.Home.DisplayActionBar = True
                                ActionBars = True
                                break
                        if Player_inturn.Home.DisplayActionBar and ActionBars:
                            abar = Player_inturn.Home.ActionBar
                            isclick = abar.is_click(pg.mouse.get_pos(), Player_inturn.Home)
                            if not isclick:
                                ALL_BOXES.empty()
                                Player_inturn.Home.action_updown = [0,0]
                                Player_inturn.Home.DisplayActionBar = False
                                ActionBars = False


        pressed_keys = pg.key.get_pressed()
        
        # Displaying Actions Bars or Info Bars
        if ActionBars:
            for unit in Player_inturn.UnitsGroup:
                if unit.DisplayActionBar:
                    if len(ALL_BOXES.sprites()) == 0:
                        Action_bar = Bar(unit)
                        ALL_BOXES.add(Action_bar)   
                        unit.ActionBar_buttoms = Action_bar.get_buttoms()
                        unit.ActionBar = Action_bar
            if Player_inturn.Home.DisplayActionBar:
                if len(ALL_BOXES.sprites()) == 0:
                    Action_bar = Bar(Player_inturn.Home)
                    ALL_BOXES.add(Action_bar)   
                    Player_inturn.Home.ActionBar_buttoms = Action_bar.get_buttoms()
                    Player_inturn.Home.ActionBar = Action_bar

        else:
            for entity in ALL_SPRITES.sprites():
                if entity.HasBar:
                    if entity.rect.collidepoint(pg.mouse.get_pos()):
                        if pressed_keys[K_i]:
                            ActionBars = True
                            ALL_BOXES.add(Bar(entity, mode='info'))
            
            for entity in ALL_OBJECTS.sprites():
                if entity.HasBar:
                    if entity.rect.collidepoint(pg.mouse.get_pos()):
                        if pressed_keys[K_i]:
                            ActionBars = True
                            ALL_BOXES.add(Bar(entity, mode='info'))
    
        # Animating Objects
        for obj in ALL_OBJECTS.sprites():
            if obj.run_animation:
                if obj.name == 'Tree':
                    obj.animate(backwards=True)
                else:
                    obj.animate()

        for unit in Player_inturn.UnitsGroup:

            Player_inturn, ActionBars, WaitingEnd = ActionLoop(Player_inturn, unit, 
                         MovingUnit, AttackingUnit, ActionBars, WaitingEnd, pressed_keys)

            # Deliver Resources
            if unit.IsWorking:
                ExtractingResources(Player_inturn, unit)
            elif unit.IsGathering:
                GatheringResources(Player_inturn, unit)

            if not ActionBars:
                ALL_BOXES.empty()


        # Runing animations of units if need it
        UnitOnAction_lst = []
        for sprite in ALL_SPRITES:
            if type(sprite).__name__ == 'Unit':
                UnitOnAction_lst.append(sprite.OnMoving)
                if sprite.OnMoving:
                    sprite.animate(mode = 'Move')
                elif sprite.IsWorking and not sprite.OnMoving:
                    sprite.animate(mode = 'Work')
                elif sprite.IsGathering and not sprite.OnMoving:
                    sprite.animate(mode = 'Gather')

        if any(UnitOnAction_lst):
            UnitOnAction = True
        else:
            UnitOnAction = False

                    
        # Buying or Upgrading
        if Player_inturn.Home.IsBuying:
            Player_inturn, ActionBars = BuyingLoop(Player_inturn, ActionBars) 

        # Checking for the winner
        for i_p, player in enumerate(Players_list):
            if len(player.UnitsGroup) == 0:
                if i_p==0:
                    Logger.EndGame([Players_list[i_p].name + ' is the winner!!' , 4])
                else:
                    Logger.EndGame([Players_list[i_p-1].name + ' is the winner!!' , 4])
                
        if WaitingEnd and not UnitOnAction:
            Logger.info([Player_inturn.name + ' is done. Press Enter' , 4])

        # End of the Turn
        if pressed_keys[K_RETURN]:

            # Resting the Units
            for unit in Player_inturn.UnitsGroup:
                actions_saved = Player_inturn.NumberOfActions
                
                # Delivering Resources
                if unit.IsWorking:
                    ExtractingResources(Player_inturn, unit, actions_saved)
                elif unit.IsGathering:
                    GatheringResources(Player_inturn, unit, actions_saved)



                activities = unit.HadMoved + unit.HadAttacked + unit.HadWorked
                unit.resource += 2*(Player_inturn.TotalActions - activities)

                if unit.InHome:
                    unit.resource = unit.full_resource
                    unit.hp += 15

                if unit.resource > unit.full_resource:
                    unit.resource = unit.full_resource
                if unit.hp > unit.full_hp:
                    unit.hp = unit.full_hp

                # Reseting values
                unit.HadWorked = 0
                unit.HadMoved = 0
                unit.HadAttacked = 0

            for d in Player_inturn.diamonds.sprites():
                d.kill()


            # Resetting Number of Actions
            if Player_inturn.TotalActions < Player_inturn.MaxActions:
                Player_inturn.TotalActions +=1
            Player_inturn.NumberOfActions = Player_inturn.TotalActions


            Player_inturn = next(Player_inturn_cycle)
            WaitingEnd = False
            Logger.msg = ['',0]
            clock.tick(4)

        General_Blit()

        for entity in ALL_BOXES:
            SCREEN.blit(entity.surf, entity.rect)
            for text_ in entity.TextGroup.sprites():
                SCREEN.blit(text_.surf, text_.rect)

        for entity in ALL_CHATS:
            entity.current_t += clock.get_time()
            if entity.current_t - entity.initial_t < entity.duration:
                SCREEN.blit(entity.surf, entity.rect)
                for text_ in entity.TextGroup.sprites():
                    SCREEN.blit(text_.surf, text_.rect)
            else:
                entity.kill()

        for unit in ALL_SPRITES:
            if type(unit).__name__ == 'Unit':
                # showing damage
                if unit.damage_text and not unit.IsAttacking:
                    display = True
                    if unit.weapon and unit.weapon.run_animation:
                        display = False
                    if display:
                        unit.damage_duration += clock.get_time()
                        if unit.damage_duration > 500:
                            unit.damage_text.kill()
                            unit.damage_text = None
                            unit.damage_duration = 0
                            if unit.weapon:
                                if unit.weapon.name == 'MagicBolt':
                                    unit.weapon.kill()
                        else:
                            if unit.damage_text.rect:
                                SCREEN.blit(unit.damage_text.surf, unit.damage_text.rect)
                # showing healing
                if unit.healing_text and not unit.IsEating:
                    unit.healing_duration += clock.get_time()
                    if unit.healing_duration > 500:
                        unit.healing_text.kill()
                        unit.healing_text = None
                        unit.healing_duration = 0
                    else:
                        SCREEN.blit(unit.healing_text.surf, unit.healing_text.rect)

            


        Logger.Print()
        pg.display.flip()


        clock.tick(60)




if __name__ == "__main__":

    # Reading Units Info
    path_to_units_dct = main_dir + '/data/Units.yaml'
    path_to_obj_dct = main_dir + '/data/Objects.yaml'
    
    with open(path_to_units_dct, 'r+') as f:
        units_dct = yaml.load(f, Loader=yaml.Loader)
    with open(path_to_obj_dct, 'r+') as f:
        obj_dct = yaml.load(f, Loader=yaml.Loader)

    main()
    pg.quit()



#pg.display.update()









