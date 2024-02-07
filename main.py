import pygame
import sqlite3


class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert()

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


class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(self)


class Player(Entity):
    def __init__(self, rect, x, y, idle, run, 
                 attack, jump, get_damage, 
                 rotation=0, 
                 hp=10, 
                 damage=1, 
                 speed=30, 
                 lvl=1):
        super().__init__(rect, x, y, idle, run, attack, jump, 
                         get_damage, rotation, hp, damage, speed, lvl)

    def update(self, event):
        if self.animation != self.attack and self.grounded:
            if event.type == pygame.KEYDOWN:
                self.sprite = 0
                if event.key == pygame.K_d:
                    self.rotation = 0
                    self.animation.clear()
                    self.animation.extend(self.run)
                elif event.key == pygame.K_a:
                    self.rotation = 1
                    self.animation.clear()
                    self.animation.extend(self.run)
            elif event.type == pygame.KEYUP:
                self.sprite = 0
                if event.key == pygame.K_d or event.key == pygame.K_a:
                    self.animation.clear()
                    self.animation.extend(self.idle)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.sprite = 0
                if event.button == 1:
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

            player.update(event)

        canvas.fill((125, 177, 186))
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