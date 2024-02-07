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
    def __init__(self, rect, x, y, idle, run, jump=None, attack=None, rotation=0, hp=10, damage=1, speed=30, lvl=1):
        rect = rect
        self.x = x
        self.y = y
        self.idle = idle
        self.run = run

        self.jump = jump
        self.attack = attack
        self.rotation = rotation
        self.hp = hp
        self.damage = damage
        self.speed = speed
        self.lvl = lvl

        self.animation = [0, *idle]
        self.tick = 0
        self.sprite = 0

    def render(self, canvas, screen, fps):
        if self.animation[0] == 0:
            canvas.blit(self.animation[self.sprite + 1], (0, 0))
            screen.blit(canvas, (0, 0))

            if self.tick < fps:
                self.tick += 1
            else:
                self.tick = 0
            
            if self.tick % int(fps / len(self.animation) - 1) == 0:
                self.sprite += 1
            if self.sprite > 5:
                self.sprite = 0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.size[0], self.size[1])
        if self.type != 'player':
            if not self.centered:
                return pygame.Rect(self.pos[0] // 1, self.pos[1] // 1, self.size[0], self.size[1])
            else:
                return pygame.Rect((self.pos[0] - self.size[0] // 2) // 1, (self.pos[1] - self.size[1] // 2) // 1, self.size[0], self.size[1])
        else:
            if not self.centered:
                return pygame.Rect(self.pos[0] // 1, self.pos[1] // 1, self.size[0], self.size[1])
            else:
                return pygame.Rect((self.pos[0] - self.size[0] // 2) // 1, (self.pos[1] - self.size[1] // 2) // 1, 20, 25)


class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(self)


class Player(Entity):
    def __init__(self, rect, x, y, idle, run=None, jump=None, attack=None, hp=10, damage=1, speed=30, lvl=1):
        super().__init__(rect, x, y, idle, run, jump, attack, hp, damage, speed, lvl)


def main():
    pygame.init()
    width, height = 1000, 500
    canvas = pygame.Surface((width, height))
    screen = pygame.display.set_mode((width, height))
    running = True

    clock = pygame.time.Clock()

    fps = 120

    path = "sprites\\"

    player_spritesheet = Spritesheet(f"{path}knight\Anomaly_anim.png")
    # player_idle = [pygame.transform.scale(player_spritesheet.get_sprite(48 * i + 17, 14, 48, 32), (140, 180)) for i in range(6)]
    player_idle = [pygame.transform.scale(player_spritesheet.get_sprite(48 * i + 17, 14, 14, 18), (56, 72)) for i in range(6)]
    player_attack = [pygame.transform.scale(player_spritesheet.get_sprite(48 * i + 15, 64 + 15, 34, 17), (136, 68)) for i in range(6)]
    player_rect = pygame.Rect(0, 0, 42, 54)
    # print(player_idle)
    # player_idle_1 = pygame.transform.scale(player_idle_1, (128, 128))
    
    player = Player(player_rect, 0, 0, player_idle)
    while running:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        canvas.fill((70, 70, 70))
        # if player_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(canvas, (0, 240, 0), player_rect)
        # canvas.blit(player_idle_1, (0, 0))
        # canvas.blit(f_trainer[index], (16, height - 16))
        # screen.blit(canvas, (0,0))
        player.render(canvas, screen, fps)
        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()