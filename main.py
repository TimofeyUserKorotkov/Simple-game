import pygame
import sqlite3





class Entity:
    def __init__(self, sprite, x, y, hp=10, damage=1, speed=30, lvl=1):
        self.x = x
        self.y = y
        self.hp = hp
        self.damage = damage
        self.speed = speed
        self.lvl = lvl

        self.animation = list()
        self.sprite = 0

        if type(sprite) != str:
            self.animation.extend(sprite)
        else:
            self.animation = sprite

    def render(self, screen):
        pass


class GameObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


class Player(Entity):
    def __init__(self):
        pass


def main():
    run = True
    while run:
        pass


if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()