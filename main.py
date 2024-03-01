import pygame


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
            self.hp_img = [
                pygame.transform.scale(pygame.image.load("sprites\gui\hp\hp.png").convert_alpha(), (27, 27)),
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

                    screen.blit(pygame.transform.flip(self.animation[self.sprite], True, False),
                                (screen.get_width() // 2 - self.idle[0].get_width() - self.attack[0].get_width() +
                                 self.run[0].get_width(), screen.get_height() // 2 - self.idle[0].get_height()))
                elif self.animation == self.run:
                    screen.blit(pygame.transform.flip(self.animation[self.sprite], True, False),
                                (screen.get_width() // 2 - self.idle[0].get_width() - self.run[0].get_width() +
                                 self.idle[0].get_width(), screen.get_height() // 2 - self.idle[0].get_height()))
                else:
                    screen.blit(pygame.transform.flip(self.animation[self.sprite], True, False),
                                (screen.get_width() // 2 - self.idle[0].get_width(),
                                 screen.get_height() // 2 - self.idle[0].get_height()))

            for i in range(self.hp):
                screen.blit(self.hp_img[0], (screen.get_width() - self.hp_img[0].get_width() -
                                             self.max_hp * 24 + i * 24, 6))
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

        self.rock_1100 = pygame.transform.scale(tile_spritesheet.get_sprite(48, 0, 16, 16), (48, 48))
        self.rock_0011 = pygame.transform.scale(tile_spritesheet.get_sprite(16, 32, 16, 16), (48, 48))
        self.slant_0100 = pygame.transform.scale(tile_spritesheet.get_sprite(32, 0, 16, 16), (48, 48))
        self.slant_0001 = pygame.transform.scale(tile_spritesheet.get_sprite(32, 32, 16, 16), (48, 48))

        self.slant_0110 = pygame.transform.scale(tile_spritesheet.get_sprite(32, 16, 16, 16), (48, 48))
        self.slant_1111 = pygame.transform.scale(tile_spritesheet.get_sprite(16, 16, 16, 16), (48, 48))

        self.grass_1100 = pygame.Surface((48, 48))
        self.grass_1100.set_colorkey((0, 0, 0))
        self.grass_1100.blit(self.rock_1100, (0, 0))
        self.grass_1100.blit(pygame.transform.scale(tile_spritesheet.get_sprite(112, 32, 16, 16), (48, 48)), (0, 0))

        self.grass_1011 = pygame.Surface((48, 48))
        self.grass_1011.set_colorkey((0, 0, 0))
        self.grass_1011.blit(self.slant_0100, (0, 0))
        self.grass_1011.blit(pygame.transform.scale(tile_spritesheet.get_sprite(96, 32, 16, 16), (48, 48)), (0, 0))

        self.grass_0000 = pygame.Surface((48, 48))
        self.grass_0000.set_colorkey((0, 0, 0))
        self.grass_0000.blit(pygame.transform.scale(tile_spritesheet.get_sprite(112, 32, 16, 16), (48, 48)), (0, 0))

        self.grass_0100 = pygame.Surface((48, 48))
        self.grass_0100.set_colorkey((0, 0, 0))
        self.grass_0100.blit(self.slant_0100, (0, 0))
        self.grass_0100.blit(pygame.transform.scale(tile_spritesheet.get_sprite(144, 32, 16, 16), (48, 48)), (0, 0))

        self.objects = [self.rock_1100, self.slant_0100, self.slant_0001, self.rock_0011,
                        self.grass_1100, self.grass_1011, self.grass_0000, self.grass_0100,
                        self.slant_0110, self.slant_1111]

        self.map = list()

    def generate(self):
        x, y = 0, 0
        for i in range(len(self.tilemap)):
            for j in range(len(self.tilemap[i])):
                if self.tilemap[i][j] != 0:
                    tt = str(self.tilemap[i][j])
                    if len(tt) > 1:
                        if tt[0] == "1":
                            tile = pygame.transform.flip(self.objects[int(tt[1:len(tt)]) - 1], True, False)
                        elif tt[0] == "2":
                            tile = pygame.transform.flip(self.objects[int(tt[1:len(tt)]) - 1], False, True)
                    else:
                        tile = self.objects[int(tt[0]) - 1]
                    self.map.append((pygame.mask.from_surface(tile), pygame.Rect(x, y, 48, 48), tile))
                x += 48
            x, y = 0, y + 48


    def render(self, canvas, screen, player):
        for i in range(len(self.map)):
            canvas.blit(self.map[i][2], (self.map[i][1].x, self.map[i][1].y))
        screen.blit(canvas, (-player.x + screen.get_width() // 2 - player.idle[0].get_width(),
                             -player.y + screen.get_height() // 2 - player.idle[0].get_height()))


class Level:
    def __init__(self, lvl_map, coords, portal_coords):
        self.map = lvl_map

        self.enemies = list()
        path = "sprites\\"

        for i in coords:
            spiny_run_spritesheet = Spritesheet(f"{path}spiny\walk.png")
            spiny_run = [pygame.transform.scale(
                spiny_run_spritesheet.get_sprite(40 * i, 0, 40, 40), (120, 120)) for i in range(8)]
            self.enemies.append(Spiny(pygame.Rect(0, 0, 40, 40), i[0], i[1], spiny_run, spiny_run))

        portal_spritesheet = Spritesheet(f"{path}environment\portal.png")
        self.portal_sprite = pygame.transform.scale(portal_spritesheet.get_sprite(0, 0, 64, 64), (192, 192))
        self.portal_coords = portal_coords

    def render(self, canvas, screen, player, fps):
        offset = [-player.x + screen.get_width() // 2 - player.idle[0].get_width(),
                  -player.y + screen.get_height() // 2 - player.idle[0].get_height()]

        self.map.render(canvas, screen, player)
        for i in self.enemies:
            if i.alive:
                i.walk(self.map, player)
                i.render(screen, fps, player)
        screen.blit(self.portal_sprite, (self.portal_coords[0] + offset[0],
                    self.portal_coords[1] + offset[1]))


class Spiny(Entity):
    def __init__(self, rect, x, y, idle, run,
            attack=None,
            jump=None,
            get_damage=None,
            direction=0,
            hp=10,
            damage=1,
            speed=0.5,
            lvl=1,
            distance=500):
        self.alive = True
        self.start_pos = [x, y]
        self.distance = distance
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
            elif i[0].overlap(zero_frame, (self.x + self.speed - i[1].x, self.y - i[1].y)):
                self.direction = 1

        if pygame.mask.from_surface(player.idle[0]).overlap(zero_frame, (self.x - player.x, self.y - player.y)):
            if player.hp > 1 and player.animation != player.attack:
                player.x, player.y = player.checkpoint
                player.hp -= 1
            elif player.hp < 2:
                self.hp = 0
                player.state = 2

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

        if self.direction == 0 and self.x + self.speed <= self.start_pos[0] + self.speed * self.distance:
            self.x += self.speed
        elif self.direction == 1 and self.x + self.speed >= self.start_pos[0]:
            self.x -= self.speed
        else:
            self.direction = 1 if self.direction == 0 else 0

        if not self.grounded:
            self.velocity_y += 0.5
            self.sprite = 0
            self.animation.clear()
            self.animation.extend(self.idle)


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
        self.state = 0
        super().__init__(rect, x, y, idle, run, attack, jump,
                         get_damage, direction, hp, damage, speed, lvl, entity_type)

    def update(self, lvl, cur_level):
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
            if (i[0].overlap(zero_frame, (self.x - i[1].x, self.y + self.velocity_y + 1 - i[1].y))
                    and self.velocity_y > -1):
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
                self.jump_cooldown = 64
                self.grounded = False
                self.animation.clear()
                self.animation.extend(self.jump)
            if not keys[pygame.K_SPACE]:
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

        if self.y > 3000 and self.hp > 1:
            self.hp -= 1
            self.x, self.y = self.checkpoint
        elif self.y > 3000 and self.hp < 2:
            self.hp = 0
            self.state = 2

        portal_mask = pygame.mask.from_surface(cur_level.portal_sprite)

        if portal_mask.overlap(zero_frame, (self.x - cur_level.portal_coords[0],
                                            self.y - cur_level.portal_coords[1])):
            self.state = 1


def main():
    width, height = 4800, 4800
    canvas = pygame.Surface((width, height))
    screen = pygame.display.set_mode((960, 480), pygame.RESIZABLE)
    running = True

    clock = pygame.time.Clock()
    fps = 120
    play = False
    menu = False
    path = "sprites\\"

    lvl1_map = Map([
        [0], [0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         108, 8, 0, 108, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [108, 5, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 108, 5, 5, 8, 0, 103, 3, 0, 103, 3, 0, 108, 8],
        [109, 10, 9, 102, 6, 7, 7, 7, 7, 7, 7, 7, 106, 2, 0, 109, 10, 10, 9, 0, 0, 0, 0, 0, 0, 0, 103, 3],
        [103, 4, 3, 103, 3, 0, 0, 0, 0, 0, 0, 0, 103, 3, 0, 109, 10,
         10, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 108, 5, 5, 5, 5, 5, 8],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 103, 4, 4, 3, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 109, 10, 10, 10, 10, 10, 9, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 103, 4, 4, 4, 4, 4, 3, 0, 0, 0, 0]
    ])

    lvl2_map = Map([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 102, 2, 0, 0, 108, 5, 5, 5, 5, 5, 8],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 103, 3, 0, 0, 109, 10, 10, 10, 10, 10, 9, 108, 5, 8],
        [0, 0, 0, 0, 0, 0, 0, 0, 102, 2, 0, 0, 102, 2, 0, 0, 0, 0, 0, 103, 4, 4, 4, 4, 4, 3, 103, 4, 3],
        [108, 5, 8, 0, 0, 0, 102, 2, 103, 3, 0, 0, 103, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 108, 5, 8],
        [109, 10, 9, 102, 2, 0, 103, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 103, 4, 3],
        [103, 4, 3, 103, 3]
    ])

    lvl1_map.generate()
    lvl2_map.generate()

    player_spritesheet = Spritesheet(f"{path}knight\Anomaly_anim.png")
    #* x3 ---->
    player_idle = [pygame.transform.scale(
        player_spritesheet.get_sprite(48 * i + 17, 14, 14, 18), (42, 54)) for i in range(6)]
    player_attack = [pygame.transform.scale(
        player_spritesheet.get_sprite(48 * i + 15, 64 + 14, 33, 18), (99, 54)) for i in range(6)]
    player_run = [pygame.transform.scale(
        player_spritesheet.get_sprite(48 * i + 16, 32 + 14, 16, 18), (48, 54)) for i in range(7)]
    player_jump = [pygame.transform.scale(player_spritesheet.get_sprite(112, 46, 16, 18), (48, 54))]

    player_rect = pygame.Rect(0, 0, 42, 54)
    player = Player(player_rect, 96, 48, player_idle, player_run, player_attack, player_jump)

    play_button_rect = pygame.rect.Rect(screen.get_width() // 2 - 100,
                                        screen.get_height() // 2 - 70, 200, 60)
    menu_button_rect = pygame.rect.Rect(screen.get_width() // 2 - 200 + 50,
                                        screen.get_height() // 2 - 300 + 480, 300, 60)
    retry_button_rect = pygame.rect.Rect(screen.get_width() // 2 - 200 + 50,
                                         screen.get_height() // 2 - 400 + 480, 300, 60)

    lvl1_button_rect = pygame.rect.Rect(screen.get_width() // 2 - 200 + 50,
                                        screen.get_height() // 2 - 400 + 300, 300, 60)
    lvl2_button_rect = pygame.rect.Rect(screen.get_width() // 2 - 200 + 50,
                                        screen.get_height() // 2 - 300 + 300, 300, 60)
    pixel_font = pygame.font.Font("fonts\craft.ttf", 24)

    # ! ==>
    canvas.fill((125, 177, 186))

    lvl1 = Level(lvl1_map, [[200, 0]], [1536, 96])
    lvl2 = Level(lvl2_map, [[900, -144]], [1488, 0])
    levels = [lvl1, lvl2]
    cur_lvl = None

    while running:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not menu:
                if event.type == pygame.MOUSEBUTTONDOWN and play_button_rect.collidepoint(event.pos):
                    menu = True
            elif not play:
                if event.type == pygame.MOUSEBUTTONDOWN and lvl1_button_rect.collidepoint(event.pos):
                    play = True
                    cur_lvl = 0
                    player.points = 0
                    canvas.fill((125, 177, 186))
                elif event.type == pygame.MOUSEBUTTONDOWN and lvl2_button_rect.collidepoint(event.pos):
                    play = True
                    cur_lvl = 1
                    player.points = 0
                    canvas.fill((125, 177, 186))
            if player.state == 1 or player.state == 2:
                if event.type == pygame.MOUSEBUTTONDOWN and menu_button_rect.collidepoint(event.pos):
                    play = False
                    for i in levels[cur_lvl].enemies:
                        i.alive = True
                    player.hp = player.max_hp
                    player.state = 0
                    player.x, player.y = player.checkpoint
            if player.state == 2:
                if event.type == pygame.MOUSEBUTTONDOWN and retry_button_rect.collidepoint(event.pos):
                    play = False
                    for i in levels[cur_lvl].enemies:
                        i.alive = True
                    player.hp = player.max_hp
                    player.state = 0
                    player.x, player.y = player.checkpoint
            if event.type == pygame.VIDEORESIZE:
                play_button_rect = pygame.rect.Rect(screen.get_width() // 2 - 100,
                                                    screen.get_height() // 2 - 70, 200, 60)
                menu_button_rect = pygame.rect.Rect(screen.get_width() // 2 - 200 + 50,
                                                    screen.get_height() // 2 - 300 + 480, 300, 60)
                retry_button_rect = pygame.rect.Rect(screen.get_width() // 2 - 200 + 50,
                                                     screen.get_height() // 2 - 400 + 480, 300, 60)

                lvl1_button_rect = pygame.rect.Rect(screen.get_width() // 2 - 200 + 50,
                                                    screen.get_height() // 2 - 400 + 300, 300, 60)
                lvl2_button_rect = pygame.rect.Rect(screen.get_width() // 2 - 200 + 50,
                                                    screen.get_height() // 2 - 300 + 300, 300, 60)

        if play and player.state == 0:
            player.update(levels[cur_lvl].map, levels[cur_lvl])

            screen.fill((125, 177, 186))
            levels[cur_lvl].render(canvas, screen, player, fps)
            player.render(screen, fps)
            screen.blit(pixel_font.render(f"{int(player.points)}", True, (120, 240, 120)), (20, 10))
        elif player.state == 1:
            play = False
            pygame.draw.rect(screen, (125, 177, 186), pygame.rect.Rect(0, 0, screen.get_width(),
                                                                       screen.get_height()))
            pygame.draw.rect(screen, (100, 100, 100), pygame.rect.Rect(
                screen.get_width() // 2 - 200, screen.get_height() // 2 - 300, 400, 600))
            pygame.draw.rect(screen, (10, 10, 10), pygame.rect.Rect(
                screen.get_width() // 2 - 203, screen.get_height() // 2 - 303, 406, 606), 3)
            killed = 0
            for i in levels[cur_lvl].enemies:
                if not i.alive:
                    killed += 1

            screen.blit(pygame.font.Font("fonts\craft.ttf", 64).render("Scores:", True, (250, 250, 250)),
                        (screen.get_width() // 2 - 200 + 20, screen.get_height() // 2 - 300 + 20))
            screen.blit(pygame.font.Font("fonts\craft.ttf", 32).render(f"Monsters killed: "
                        f"{killed}/{len(lvl1.enemies)}", True, (250, 250, 250)),
                        (screen.get_width() // 2 - 200 + 20, screen.get_height() // 2 - 300 + 120))
            screen.blit(pygame.font.Font("fonts\craft.ttf", 32).render(f"Damage received: "
                        f"{player.max_hp - player.hp}/{player.max_hp}", True, (250, 250, 250)),
                        (screen.get_width() // 2 - 200 + 20, screen.get_height() // 2 - 300 + 180))
            screen.blit(pygame.font.Font("fonts\craft.ttf", 48).render(f"Total: {killed + player.hp}", True,
                        (250, 250, 250)), (screen.get_width() // 2 - 200 + 20, screen.get_height() // 2 - 300 + 340))

            pygame.draw.rect(screen, (200, 200, 200), menu_button_rect)
            screen.blit(pygame.font.Font("fonts\craft.ttf", 48).render("Menu", True, (50, 77, 86)),
                        (screen.get_width() // 2 - 200 + 140, screen.get_height() // 2 - 300 + 490))
        elif player.state == 2:
            pygame.draw.rect(screen, (125, 177, 186), pygame.rect.Rect(0, 0, screen.get_width(), screen.get_height()))
            pygame.draw.rect(screen, (100, 100, 100), pygame.rect.Rect(
                screen.get_width() // 2 - 200, screen.get_height() // 2 - 300, 400, 600))
            pygame.draw.rect(screen, (10, 10, 10), pygame.rect.Rect(
                screen.get_width() // 2 - 203, screen.get_height() // 2 - 303, 406, 606), 3)

            screen.blit(pygame.font.Font("fonts\craft.ttf", 48).render("you lose :(", True, (50, 77, 86)),
                        (screen.get_width() // 2 - 250 + 120, screen.get_height() // 2 - 300 + 200))

            pygame.draw.rect(screen, (200, 200, 200), retry_button_rect)
            pygame.draw.rect(screen, (200, 200, 200), menu_button_rect)
            screen.blit(pygame.font.Font("fonts\craft.ttf", 48).render("Retry", True, (50, 77, 86)),
                        (screen.get_width() // 2 - 200 + 140, screen.get_height() // 2 - 400 + 490))
            screen.blit(pygame.font.Font("fonts\craft.ttf", 48).render("Menu", True, (50, 77, 86)),
                        (screen.get_width() // 2 - 200 + 140, screen.get_height() // 2 - 300 + 490))
        elif menu:
            screen.fill((125, 177, 186))
            pygame.draw.rect(screen, (200, 200, 200), lvl1_button_rect)
            pygame.draw.rect(screen, (200, 200, 200), lvl2_button_rect)
            screen.blit(pygame.font.Font("fonts\craft.ttf", 48).render("lvl 1", True, (50, 77, 86)),
                        (screen.get_width() // 2 - 200 + 140, screen.get_height() // 2 - 400 + 310))
            screen.blit(pygame.font.Font("fonts\craft.ttf", 48).render("lvl 2", True, (50, 77, 86)),
                        (screen.get_width() // 2 - 200 + 140, screen.get_height() // 2 - 300 + 310))
        else:
            screen.fill((125, 177, 186))
            pygame.draw.rect(screen, (200, 200, 200), play_button_rect)
            screen.blit(pygame.font.Font("fonts\craft.ttf", 32).render("Play", True, (50, 77, 86)),
                        (screen.get_width() // 2 - 36, screen.get_height() // 2 - 54))

        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()