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
            lvl=1):
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

        self.jumping = False
        self.grounded = False
        self.velocity_y = 0

        self.animation = [*idle]
        self.tick = 0
        self.sprite = 0

    def render(self, canvas, screen, fps):
        if self.direction == 0:
            if self.animation == self.attack:
                canvas.blit(self.animation[self.sprite], 
                    (self.x - self.run[0].get_width() + self.idle[0].get_width(), self.y))
            else:
                canvas.blit(self.animation[self.sprite], (self.x, self.y))
        elif self.direction == 1:
            if self.animation == self.attack:
                canvas.blit(pygame.transform.flip(self.animation[self.sprite], True, False), 
                    (self.x - self.attack[0].get_width() + self.run[0].get_width(), self.y))
            elif self.animation == self.run:
                canvas.blit(pygame.transform.flip(self.animation[self.sprite], True, False), 
                    (self.x - self.run[0].get_width() + self.idle[0].get_width(), self.y))
            else:
                canvas.blit(pygame.transform.flip(self.animation[self.sprite], True, False), (self.x, self.y))
        
        screen.blit(canvas, (0, 0))

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
        
        # for i in range(len(self.objects)):
        #     self.objects[i] = pygame.mask.from_surface(self.objects[i])

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
                    

    def render(self, canvas, screen):
        for i in range(len(self.map)):
            canvas.blit(self.map[i][2], (self.map[i][1].x, self.map[i][1].y))
        screen.blit(canvas, (0, 0))


class Player(Entity):
    def __init__(self, rect, x, y, idle, run, 
                 attack, jump=None, get_damage=None, 
                 direction=0, 
                 hp=10, 
                 damage=1, 
                 speed=2, 
                 lvl=1,
                 step_size=3):
        self.step_size = step_size
        super().__init__(rect, x, y, idle, run, attack, jump, 
                         get_damage, direction, hp, damage, speed, lvl)

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
                # print(1)
            elif i[0].overlap(zero_frame, (self.x - i[1].x, self.y + self.velocity_y - i[1].y)):
                self.velocity_y = 0
            # elif i[0].overlap(pygame.mask.from_surface(self.idle[0]), (self.x - i[1].x, self.y + self.velocity_y - i[1].y)):
            #     # self.velocity_y = 0
            #     self.y = self.y - self.y % 3
            #     for j in range(int(self.velocity_y + 0.5)):
            #         if (not i[0].overlap(pygame.mask.from_surface(self.idle[0]), (self.x - i[1].x, self.y - 3 - i[1].y)) 
            #             and self.velocity_y % 3 == 0):
            #             self.y -= 3
            #         elif self.velocity_y % 3 != 0:
            #             self.y -= self.velocity_y % 3
            #         else:
            #             break
                # self.velocity_y = 0
            # elif i[0].overlap(pygame.mask.from_surface(self.idle[0]), (self.x - i[1].x, self.y - self.velocity_y - i[1].y)):
            #     if self.y % 3 != 0:
            #         self.y = self.y + 3 - self.y % 3
            #     for j in range(int(self.velocity_y - self.velocity_y % 3)):
            #         if not i[0].overlap(pygame.mask.from_surface(self.idle[0]), (self.x - i[1].x, self.y - 3 - i[1].y)):
            #             self.y -= 3
            #         else:
            #             break
                # self.velocity_y = 0
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
                # for j in range(int(self.velocity_y + 0.5)):
                #     if not i[0].overlap(pygame.mask.from_surface(self.idle[0]), (self.x + 3 - i[1].x, self.y - i[1].y)):
                #         self.x += 3
                #     else:
                #         break
                    
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
            # elif i[0].overlap(pygame.mask.from_surface(self.idle[0]), (self.x + self.speed - i[1].x, self.y - i[1].y)):
            #     # move_right = False
            #     for j in range(self.step_size):
            #         if (not i[0].overlap(pygame.mask.from_surface(self.idle[0]), (self.x + self.speed - i[1].x, self.y - 3 * (j + 1) - i[1].y))
            #             and keys[pygame.K_d]):
            #             self.y -= 3 * (j + 1)
            #             self.x += self.speed
            #     else:
            #         move_right = False
                # for j in range(int(self.velocity_y + 0.5)):
                #     if not i[0].overlap(pygame.mask.from_surface(self.idle[0]), (self.x - 3 - i[1].x, self.y - i[1].y)):
                #         self.x -= 3
                #     else:
                #         break
                    
        if not move_left and not move_right:
            self.y -= 3


        # for i in lvl.map:
        #     if i[1].colliderect(self.x, self.y + self.velocity_y + 1, 
        #                         self.idle[0].get_width(), self.animation[0].get_height()) and self.velocity_y > -1:
        #         self.velocity_y = 0
        #         self.grounded = True
        #         self.y = i[1].y - self.animation[0].get_height()
        #     elif i[1].colliderect(self.x, self.y + self.velocity_y, 
        #                         self.idle[0].get_width(), self.animation[0].get_height()):
        #         self.velocity_y = 0
        #         self.y = i[1].y + i[1].height
        # self.y += self.velocity_y

        # for i in lvl.map:
        #     if i[1].colliderect(self.x - self.speed, self.y, self.idle[0].get_width(), 
        #                         self.animation[0].get_height()):
        #         move_left = False
        #         self.x = i[1].x + i[1].width
        #     elif i[1].colliderect(self.x + self.speed, self.y, self.idle[0].get_width(), 
        #                           self.animation[0].get_height()):
        #         move_right = False
        #         self.x = i[1].x - self.idle[0].get_width()

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
            if keys[pygame.K_SPACE]:
                self.sprite = 0
                self.velocity_y = -10
                self.jumping = True
                self.grounded = False
                self.animation.clear()
                self.animation.extend(self.jump)
            if not keys[pygame.K_SPACE]:
                self.jumping = False
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
            

def main():
    # pygame.init()
    width, height = 960, 480
    canvas = pygame.Surface((width, height))
    screen = pygame.display.set_mode((width, height))
    running = True

    clock = pygame.time.Clock()

    fps = 120

    bullet = pygame.Surface((18, 24))
    bullet.fill((255, 0, 0))
    bullet_mask = pygame.mask.from_surface(bullet)

    path = "sprites\\"

    lvl_1 = Map([
        [5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 6],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
        [3, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 9, 0, 0, 0, 4],
        [3, 12, 13, 0, 10, 11, 0, 0, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 4],
        [3, 0, 0, 0, 12, 13, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 0, 0, 0, 4],
        [3, 0, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 4],
        [3, 0, 12, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 4],
        [7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8]
    ])

    lvl_1.generate()

    player_spritesheet = Spritesheet(f"{path}knight\Anomaly_anim.png")
    # player_idle = [pygame.transform.scale(player_spritesheet.get_sprite(48 * i + 17, 14, 48, 32), (140, 180)) for i in range(6)]
    #* x3 ---->
    player_idle = [pygame.transform.scale(player_spritesheet.get_sprite(48 * i + 17, 14, 14, 18), (42, 54)) for i in range(6)]
    player_attack = [pygame.transform.scale(player_spritesheet.get_sprite(48 * i + 15, 64 + 14, 33, 18), (99, 54)) for i in range(6)]
    player_run = [pygame.transform.scale(player_spritesheet.get_sprite(48 * i + 16, 32 + 14, 16, 18), (48, 54)) for i in range(7)]
    player_jump = [pygame.transform.scale(player_spritesheet.get_sprite(112, 46, 16, 18), (48, 54))]


    player_rect = pygame.Rect(0, 0, 42, 54)
    # print(player_idle)
    # player_idle_1 = pygame.transform.scale(player_idle_1, (128, 128))
    
    player = Player(player_rect, 96, 48, player_idle, player_run, player_attack, player_jump)

    # player_mask = pygame.mask.from_surface(pygame.transform.scale(player_spritesheet.get_sprite(0 + 17, 14, 14, 18), (42, 54)))
    player_mask = pygame.mask.from_surface(player.idle[0])
    # player_img = player_mask.to_surface()

    while running:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # if player.rect.colliderect()
        player.update(lvl_1)

        pos = pygame.mouse.get_pos()

        if player_mask.overlap(bullet_mask, (pos[0] - player.x, pos[1] - player.y)):
            bullet.fill((0, 255, 0))
        else:
            bullet.fill((255, 0, 0))

        canvas.fill((125, 177, 186))
        lvl_1.render(canvas, screen)
            # if player_rect.collidepoint(pygame.mouse.get_pos()):
        # pygame.draw.rect(canvas, (0, 240, 0), player_rect)
            # canvas.blit(player_idle_1, (0, 0))
            # canvas.blit(f_trainer[index], (16, height - 16))
            # screen.blit(canvas, (0,0))
        player.render(canvas, screen, fps)
        screen.blit(pygame.font.SysFont(None, 24).render(f"{int(clock.get_fps())}", True, (250, 177, 186)), (20, 10))

        # screen.blit(player_img, (0, 0))


        # screen.blit(bullet, pos)
        

        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()