import pygame
import sqlite3


class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert_alpha()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height))
        sprite.set_colorkey((0, 0, 0))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite


class Entity:
    def __init__(self, rect, x, y, idle, run, 
            attack=None, 
            jump=None, 
            get_damage=None, 
            direction=0, 
            hp=10, 
            damage=1, 
            speed=3, 
            lvl=1,
            entity_type=None):
        rect = rect
        self.x = x
        self.y = y
        self.idle = idle
        self.run = run

        self.attack = attack
        self.jump = jump

        self.direction = direction
        self.hp = hp
        self.damage = damage
        self.speed = speed
        self.lvl = lvl
        self.entity_type = entity_type

        if entity_type == "player":
            self.hp_img = [pygame.transform.scale(pygame.image.load("sprites\gui\hp\hp.png").convert_alpha(), (27, 27)), 
                           pygame.transform.scale(pygame.image.load("sprites\gui\hp\\no_hp.png").convert_alpha(), (27, 27))]

        self.max_hp = hp

        self.jumping = False
        self.grounded = False
        self.velocity_y = 0

        self.animation = [*idle]
        self.tick = 0
        self.sprite = 0

    def render(self, screen, fps, player=None):
        if self.entity_type == "player":
            if self.direction == 0:
                if self.animation == self.attack:
                    screen.blit(self.animation[self.sprite], (screen.get_width() // 2 - self.idle[0].get_width() - 
                                                              self.run[0].get_width() + self.idle[0].get_width(), 
                                                              screen.get_height() // 2 - self.idle[0].get_height()))
                else:
                    screen.blit(self.animation[self.sprite], (screen.get_width() // 2 - self.idle[0].get_width(), 
                                                              screen.get_height() // 2 - self.idle[0].get_height()))
            elif self.direction == 1:
                if self.animation == self.attack:
                    # screen.blit(pygame.transform.flip(self.animation[self.sprite], True, False), 
                    #     (self.x - self.attack[0].get_width() + self.run[0].get_width(), self.y))
                    screen.blit(pygame.transform.flip(self.animation[self.sprite], True, False), 
                                (screen.get_width() // 2 - self.idle[0].get_width() - self.attack[0].get_width() + 
                                 self.run[0].get_width(), screen.get_height() // 2 - self.idle[0].get_height()))
                elif self.animation == self.run:
                    # screen.blit(pygame.transform.flip(self.animation[self.sprite], True, False), 
                    #     (self.x - self.run[0].get_width() + self.idle[0].get_width(), self.y))
                    screen.blit(pygame.transform.flip(self.animation[self.sprite], True, False), 
                                (screen.get_width() // 2 - self.idle[0].get_width() - self.run[0].get_width() + 
                                 self.idle[0].get_width(), screen.get_height() // 2 - self.idle[0].get_height()))
                else:
                    screen.blit(pygame.transform.flip(self.animation[self.sprite], True, False), 
                                (screen.get_width() // 2 - self.idle[0].get_width(), 
                                 screen.get_height() // 2 - self.idle[0].get_height()))
                    
            for i in range(self.hp):
                screen.blit(self.hp_img[0], (screen.get_width() - self.hp_img[0].get_width() - self.max_hp * 24 + i * 24, 6))
            for i in range(self.max_hp - self.hp):
                screen.blit(self.hp_img[1], (screen.get_width() - self.hp_img[0].get_width() - 
                                             self.max_hp * 24 + i * 24 + self.hp * 24, 6))
        else:
            offset = [-player.x + screen.get_width() // 2 - player.idle[0].get_width(),
                      -player.y + screen.get_height() // 2 - player.idle[0].get_height()]
            if self.direction == 0:
                if self.animation == self.attack:
                    screen.blit(self.animation[self.sprite], 
                        (self.x - self.run[0].get_width() + self.idle[0].get_width() + offset[0], self.y + offset[1]))
                else:
                    screen.blit(self.animation[self.sprite], (self.x + offset[0], self.y + offset[1]))
            elif self.direction == 1:
                if self.animation == self.attack:
                    screen.blit(pygame.transform.flip(self.animation[self.sprite], True, False), 
                        (self.x - self.attack[0].get_width() + self.run[0].get_width() + offset[0], self.y + offset[1]))
                elif self.animation == self.run:
                    screen.blit(pygame.transform.flip(self.animation[self.sprite], True, False), 
                        (self.x - self.run[0].get_width() + self.idle[0].get_width() + offset[0], self.y + offset[1]))
                else:
                    screen.blit(pygame.transform.flip(self.animation[self.sprite], True, False), 
                                (self.x + offset[0], self.y + offset[1]))

        if self.tick < fps:
            self.tick += 1
        else:
            self.tick = 0
            
        if self.tick % int(fps / len(self.animation)) == 0:
            self.sprite += 1
        if self.sprite > len(self.animation) - 1:
            if self.animation == self.attack:
                self.animation.clear()
                self.animation.extend(self.idle)
            self.sprite = 0
            

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.animation[0].get_width(), self.animation[0].get_height())


class Map:
    def __init__(self, tilemap):
        self.tilemap = tilemap
        tile_spritesheet = Spritesheet("sprites\environment\Tileset.png")

        self.rock_corner = pygame.transform.rotate(pygame.transform.scale(tile_spritesheet.get_sprite(112, 0, 16, 16), (48, 48)), 270)
        self.rock_middle = pygame.transform.scale(tile_spritesheet.get_sprite(48, 0, 16, 16), (48, 48))

        self.grass_middle = pygame.Surface((48, 48))
        self.grass_middle.set_colorkey((0, 0, 0))
        self.grass_middle.blit(self.rock_middle, (0, 0))
        self.grass_middle.blit(pygame.transform.scale(tile_spritesheet.get_sprite(112, 32, 16, 16), (48, 48)), (0, 0))

        self.rock_slant_l = pygame.transform.scale(tile_spritesheet.get_sprite(0, 0, 16, 16), (48, 48))
        self.rock_slant_r = pygame.transform.scale(tile_spritesheet.get_sprite(32, 0, 16, 16), (48, 48))
        self.rock_slant_bl = pygame.transform.scale(tile_spritesheet.get_sprite(0, 32, 16, 16), (48, 48))
        self.rock_slant_br = pygame.transform.scale(tile_spritesheet.get_sprite(32, 32, 16, 16), (48, 48))

        self.objects = [pygame.transform.flip(self.rock_middle, False, True), self.rock_middle, 
                        pygame.transform.rotate(self.rock_middle, 270), pygame.transform.rotate(self.rock_middle, 90),
                        self.rock_corner, pygame.transform.flip(self.rock_corner, True, False),
                        pygame.transform.flip(self.rock_corner, False, True), pygame.transform.flip(self.rock_corner, True, True), 
                        self.grass_middle, self.rock_slant_l, self.rock_slant_r, self.rock_slant_bl, self.rock_slant_br]

        self.map = list()

    def generate(self):
        x, y = 0, 0
        for i in range(len(self.tilemap)):
            for j in range(len(self.tilemap[i])):
                if self.tilemap[i][j] != 0:
                    self.map.append((pygame.mask.from_surface(self.objects[self.tilemap[i][j] - 1]), 
                                     pygame.Rect(x, y, 48, 48), self.objects[self.tilemap[i][j] - 1]))
                x += 48
            x, y = 0, y + 48
            # x, y = 0, y + 8
                    

    def render(self, canvas, screen, player):
        # l = (screen.get_width() // 48 + 1) * (screen.get_height() // 48 + 1)
        # for i in range(l):
        #     pass
        for i in range(len(self.map)):
            canvas.blit(self.map[i][2], (self.map[i][1].x, self.map[i][1].y))
            # print((self.map[i][1].x, self.map[i][1].y))
        screen.blit(canvas, (-player.x + screen.get_width() // 2 - player.idle[0].get_width(), 
                             -player.y + screen.get_height() // 2 - player.idle[0].get_height()))


class Spiny(Entity):
    def __init__(self, rect, x, y, idle, run, 
            attack=None, 
            jump=None, 
            get_damage=None, 
            direction=0, 
            hp=10, 
            damage=1, 
            speed=0.5, 
            lvl=1):
        self.alive = True
        super().__init__(rect, x, y, idle, run, attack, jump, 
                         get_damage, direction, hp, damage, speed, lvl)
    def walk(self, lvl, player):
        self.grounded = False

        if self.direction == 0:
            zero_frame = pygame.mask.from_surface(self.idle[0])
        else:
            zero_frame = pygame.mask.from_surface(pygame.transform.flip(self.idle[0], True, False))
        
        for i in lvl.map:
            if i[0].overlap(zero_frame, (self.x - i[1].x, self.y + self.velocity_y + 1 - i[1].y)):
                self.grounded = True
                if self.y % 3 != 0:
                    self.y = self.y - self.y % 3
                for j in range(int(self.velocity_y + 0.5)):
                    if not i[0].overlap(zero_frame, (self.x - i[1].x, self.y + 3 - i[1].y)):
                        self.y += 3
                    else:
                        break
                self.velocity_y = 0
            elif i[0].overlap(zero_frame, (self.x - i[1].x, self.y + self.velocity_y - i[1].y)):
                self.velocity_y = 0
        self.y += self.velocity_y

        for i in lvl.map:
            if i[0].overlap(zero_frame, (self.x - self.speed - i[1].x, self.y - i[1].y)):
                self.direction = 0
                # self.x += 80
            elif i[0].overlap(zero_frame, (self.x + self.speed - i[1].x, self.y - i[1].y)):
                self.direction = 1
                # self.x -= 80

        if pygame.mask.from_surface(player.idle[0]).overlap(zero_frame, (self.x - player.x, self.y - player.y)):
            if player.hp > 1 and player.animation != player.attack:
                player.x, player.y = player.checkpoint
                player.hp -= 1

        if player.direction == 0 and pygame.mask.from_surface(player.idle[0]).overlap(zero_frame, 
            (self.x - player.x - 12, self.y - player.y)):
            if player.animation == player.attack:
                self.alive = False
                player.points += 1
        if player.direction == 1 and pygame.mask.from_surface(player.idle[0]).overlap(zero_frame, 
            (self.x - player.x + 12, self.y - player.y)):
            if player.animation == player.attack:
                self.alive = False
                player.points += 1

        # do = -1

        # for i in lvl.map:
        #     if not i[0].overlap(zero_frame, (self.x + zero_frame.to_surface().get_width() - i[1].x, self.y + 1 - i[1].y)) and self.direction == 1:
        #         do = 0
        #         break
        #     elif not i[0].overlap(zero_frame, (self.x - zero_frame.to_surface().get_width() + 80 - i[1].x, self.y + 1 - i[1].y)) and self.direction == 0:
        #         do = 1
        #         break
        #     else:
        #         continue
        
        # if do == 0:
        #     self.direction = 0
        #     self.x += 80
        # elif do == 1:
        #     self.direction = 1
        #     self.x -= 80

        if self.direction == 0:
            self.x += self.speed
        elif self.direction == 1:
            self.x -= self.speed

        if not self.grounded:
            self.velocity_y += 0.5
            self.sprite = 0
            self.animation.clear()
            self.animation.extend(self.idle)

        # self.y -= player.y
        # self.y += player.y
        

class Player(Entity):
    def __init__(self, rect, x, y, idle, run, 
                 attack, jump=None, get_damage=None, 
                 direction=0, 
                 hp=3, 
                 damage=1, 
                 speed=2, 
                 lvl=1,
                 step_size=3,
                 entity_type="player"):
        self.step_size = step_size
        self.jump_cooldown = 0
        self.checkpoint = [x, y]
        self.points = 0
        super().__init__(rect, x, y, idle, run, attack, jump, 
                         get_damage, direction, hp, damage, speed, lvl, entity_type)

    def update(self, lvl):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        
        move_right = True
        move_left = True
        self.grounded = False

        if self.direction == 0:
            zero_frame = pygame.mask.from_surface(self.idle[0])
        else:
            zero_frame = pygame.mask.from_surface(pygame.transform.flip(self.idle[0], True, False))

        for i in lvl.map:
            if i[0].overlap(zero_frame, (self.x - i[1].x, self.y + self.velocity_y + 1 - i[1].y)) and self.velocity_y > -1:
                self.grounded = True
                if self.y % 3 != 0:
                    self.y = self.y - self.y % 3
                for j in range(int(self.velocity_y + 0.5)):
                    if not i[0].overlap(zero_frame, (self.x - i[1].x, self.y + 3 - i[1].y)):
                        self.y += 3
                    else:
                        break
                self.velocity_y = 0
            elif i[0].overlap(zero_frame, (self.x - i[1].x, self.y + self.velocity_y - i[1].y)):
                self.velocity_y = 0
        self.y += self.velocity_y

        for i in lvl.map:
            if i[0].overlap(zero_frame, (self.x - self.speed - i[1].x, self.y - i[1].y)):
                for j in range(self.step_size):
                    do = True
                    for i in lvl.map:
                        if i[0].overlap(zero_frame, (self.x - self.speed - i[1].x, self.y - 3 * (j + 1) - i[1].y)):
                            do = False
                    if do and keys[pygame.K_a]:
                        self.y -= 3 * (j + 1)
                        self.x -= self.speed
                else:
                    move_left = False
            elif i[0].overlap(zero_frame, (self.x + self.speed - i[1].x, self.y - i[1].y)):
                for j in range(self.step_size):
                    do = True
                    for i in lvl.map:
                        if i[0].overlap(zero_frame, (self.x + self.speed - i[1].x, self.y - 3 * (j + 1) - i[1].y)):
                            do = False
                    if do and keys[pygame.K_d]:
                        self.y -= 3 * (j + 1)
                        self.x += self.speed
                else:
                    move_right = False
                    
        if not move_left and not move_right:
            self.y -= 3

        if ((self.direction == 0 and not move_right or self.direction == 1 and not move_left) 
            and self.animation == self.run):
            self.sprite = 0
            self.animation.clear()
            self.animation.extend(self.idle)

        if self.animation != self.attack and self.grounded:
            if (keys[pygame.K_d] and move_right) or (keys[pygame.K_a] and move_left):
                self.animation.clear()
                self.animation.extend(self.run)
            elif ((not keys[pygame.K_d] and not keys[pygame.K_a] and self.animation != self.idle) 
                  or self.animation == self.jump):
                self.sprite = 0
                self.animation.clear()
                self.animation.extend(self.idle)
            if keys[pygame.K_SPACE] and self.jump_cooldown == 0:
                self.sprite = 0
                self.velocity_y = -10
                # self.jumping = True
                self.jump_cooldown = 48
                self.grounded = False
                self.animation.clear()
                self.animation.extend(self.jump)
            if not keys[pygame.K_SPACE]:
                # self.jumping = False
                self.jump_cooldown = 0
            if mouse[0]:
                self.sprite = 0
                self.animation.clear()
                self.animation.extend(self.attack)

        elif not self.grounded:
            self.velocity_y += 0.5
            self.sprite = 0
            self.animation.clear()
            self.animation.extend(self.jump)
                
        if self.animation != self.attack:
            if keys[pygame.K_d] and move_right:
                self.direction = 0
                self.x += self.speed
            elif keys[pygame.K_a] and move_left:
                self.direction = 1
                self.x -= self.speed

        if self.jump_cooldown != 0:
            self.jump_cooldown -= 1
        # self.hp = 1
            

def main():
    # width, height = 960, 480
    width, height = 10000, 10000
    canvas = pygame.Surface((width, height))
    screen = pygame.display.set_mode((960, 480), pygame.RESIZABLE)
    running = True

    clock = pygame.time.Clock()
    fps = 120
    play = False
    path = "sprites\\"
    # lvl_1 = Map([
    #     [5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 6],
    #     [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
    #     [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
    #     [3, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 9, 0, 0, 0, 4],
    #     [3, 12, 13, 0, 10, 11, 0, 0, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 4],
    #     [3, 0, 0, 0, 12, 13, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 4],
    #     [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 0, 0, 0, 4],
    #     [3, 0, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 4],
    #     [3, 0, 12, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 4],
    #     [7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8]
    # ])

    lvl_1 = Map([
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 12, 13, 0, 10, 11, 10, 11, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 12, 13, 12, 13, 0, 0, 0, 9, 0, 0, 0, 0, 9, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 12, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 12, 13, 0, 10, 11, 10, 11, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 12, 13, 12, 13, 0, 0, 0, 9, 0, 0, 0, 0, 9, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 12, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 12, 13, 0, 10, 11, 10, 11, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 12, 13, 12, 13, 0, 0, 0, 9, 0, 0, 0, 0, 9, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 12, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 12, 13, 0, 10, 11, 10, 11, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 12, 13, 12, 13, 0, 0, 0, 9, 0, 0, 0, 0, 9, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 0, 0, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [3, 0, 12, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 4, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 4],
    ])

    # print(len(lvl_1.tilemap), len(lvl_1.tilemap[0]))
    # for i in range(len(lvl_1.tilemap)):
    #     print(len(lvl_1.tilemap[i]))
    lvl_1.generate()

    player_spritesheet = Spritesheet(f"{path}knight\Anomaly_anim.png")
    #* x3 ---->
    player_idle = [pygame.transform.scale(player_spritesheet.get_sprite(48 * i + 17, 14, 14, 18), (42, 54)) for i in range(6)]
    player_attack = [pygame.transform.scale(player_spritesheet.get_sprite(48 * i + 15, 64 + 14, 33, 18), (99, 54)) for i in range(6)]
    player_run = [pygame.transform.scale(player_spritesheet.get_sprite(48 * i + 16, 32 + 14, 16, 18), (48, 54)) for i in range(7)]
    player_jump = [pygame.transform.scale(player_spritesheet.get_sprite(112, 46, 16, 18), (48, 54))]

    spiny_idle_spritesheet = Spritesheet(f"{path}spiny\idle.png")
    spiny_run_spritesheet = Spritesheet(f"{path}spiny\walk.png")
    spine_idle = [pygame.transform.scale(spiny_idle_spritesheet.get_sprite(40 * i + 8, 13, 40, 40), (120, 120)) for i in range(7)]
    spiny_run = [pygame.transform.scale(spiny_run_spritesheet.get_sprite(40 * i, 0, 40, 40), (120, 120)) for i in range(8)]
    player_rect = pygame.Rect(0, 0, 42, 54)
    
    player = Player(player_rect, 96, 48, player_idle, player_run, player_attack, player_jump)
    # player = Player(player_rect, 1488, 912, player_idle, player_run, player_attack, player_jump)
    # 1488, 912

    spiny = Spiny(pygame.Rect(0, 0, 40, 40), 600, 200, spiny_run, spiny_run)

    play_button_rect = pygame.rect.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 - 70, 200, 60)
    pixel_font = pygame.font.Font("fonts\craft.ttf", 24)

    # ! ==>
    canvas.fill((125, 177, 186))

    while running:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not play:
                if event.type == pygame.MOUSEBUTTONDOWN and play_button_rect.collidepoint(event.pos):
                    play = True
                if event.type == pygame.VIDEORESIZE:
                    play_button_rect = pygame.rect.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 - 70, 200, 60)

        if play:
            player.update(lvl_1)
            if spiny.alive:
                spiny.walk(lvl_1, player)

            screen.fill((125, 177, 186))
            lvl_1.render(canvas, screen, player)

            if spiny.alive:
                spiny.render(screen, fps, player)
            player.render(screen, fps)
            screen.blit(pixel_font.render(f"{int(player.points)}", True, (120, 240, 120)), (20, 10))
            screen.blit(pixel_font.render(f"{int(clock.get_fps())}", True, (250, 177, 186)), (40, 10))
        else:
            screen.fill((125, 177, 186))
            pygame.draw.rect(screen, (200, 200, 200), play_button_rect)
            screen.blit(pygame.font.Font("fonts\craft.ttf", 32).render("Play", True, (50, 77, 86)), (screen.get_width() // 2 - 36, screen.get_height() // 2 - 54))
            screen.blit(pixel_font.render(f"{int(clock.get_fps())}", True, (250, 177, 186)), (20, 10))

        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()