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
            rotation=0, 
            hp=10, 
            damage=1, 
            speed=30, 
            lvl=1):
        rect = rect
        self.x = x
        self.y = y
        self.idle = idle
        self.run = run

        self.attack = attack

        self.rotation = rotation
        self.hp = hp
        self.damage = damage
        self.speed = speed
        self.lvl = lvl

        self.grounded = True

        self.animation = [*idle]
        self.tick = 0
        self.sprite = 0

    def render(self, canvas, screen, fps):
        if self.rotation == 0:
            if self.animation == self.attack:
                canvas.blit(self.animation[self.sprite], 
                    (self.x - self.run[0].get_width() + self.idle[0].get_width(), self.y))
            else:
                canvas.blit(self.animation[self.sprite], (self.x, self.y))
        elif self.rotation == 1:
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

        self.objects = [pygame.transform.flip(self.rock_middle, False, True), self.rock_middle, 
                        pygame.transform.rotate(self.rock_middle, 270), pygame.transform.rotate(self.rock_middle, 90),
                        self.rock_corner, pygame.transform.flip(self.rock_corner, True, False),
                        pygame.transform.flip(self.rock_corner, False, True), pygame.transform.flip(self.rock_corner, True, True), 
                        self.grass_middle]

        self.map = list()

    def generate(self):
        x, y = 0, 0
        for i in range(1, len(self.tilemap) + 1):
            if self.tilemap[i - 1] != 0:
                self.map.append((self.objects[self.tilemap[i - 1] - 1], pygame.Rect(x, y, 48, 48)))
                # print(self.tilemap[i - 1])
                if i % 10 == 0 and i != 0:
                    x, y = 0, y + 48
                else:
                    x += 48
            else:
                if i % 10 == 0 and i != 0:
                    x, y = 0, y + 48
                else:
                    x += 48
                    

    def render(self, canvas, screen):
        for i in range(len(self.map)):
            canvas.blit(self.map[i][0], (self.map[i][1].x, self.map[i][1].y))
        screen.blit(canvas, (0, 0))


class Player(Entity):
    def __init__(self, rect, x, y, idle, run, 
                 attack, jump, get_damage=None, 
                 rotation=0, 
                 hp=10, 
                 damage=1, 
                 speed=30, 
                 lvl=1):
        super().__init__(rect, x, y, idle, run, attack, jump, 
                         get_damage, rotation, hp, damage, speed, lvl)

    def update(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        if self.animation != self.attack and self.grounded:
            if keys[pygame.K_d]:
                self.rotation = 0
                self.animation.clear()
                self.animation.extend(self.run)
            elif keys[pygame.K_a]:
                self.rotation = 1
                self.animation.clear()
                self.animation.extend(self.run)
            elif not keys[pygame.K_d] and not keys[pygame.K_a] and self.animation != self.idle:
                self.sprite = 0
                self.animation.clear()
                self.animation.extend(self.idle)
            if mouse[0]:
                self.sprite = 0
                self.animation.clear()
                self.animation.extend(self.attack)
        elif not self.grounded:
            pass
            

def main():
    # pygame.init()
    width, height = 1000, 500
    canvas = pygame.Surface((width, height))
    screen = pygame.display.set_mode((width, height))
    running = True

    clock = pygame.time.Clock()

    fps = 60


    path = "sprites\\"

    lvl_1 = Map([
        [5, 1, 1, 1, 1, 1, 1, 1, 1, 6],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 4],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 4],
        [3, 9, 9, 9, 9, 9, 9, 9, 9, 4],
        [7, 2, 2, 2, 2, 2, 2, 2, 2, 8]
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
    
    player = Player(player_rect, 100, 100, player_idle, player_run, player_attack, player_jump)
    while running:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # if player.rect.colliderect()
        player.update()

        canvas.fill((125, 177, 186))
        lvl_1.render(canvas, screen)
            # if player_rect.collidepoint(pygame.mouse.get_pos()):
        # pygame.draw.rect(canvas, (0, 240, 0), player_rect)
            # canvas.blit(player_idle_1, (0, 0))
            # canvas.blit(f_trainer[index], (16, height - 16))
            # screen.blit(canvas, (0,0))
        player.render(canvas, screen, fps)
        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()