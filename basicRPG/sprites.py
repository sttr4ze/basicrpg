import pygame
from config import *
import math
import random


class Spritesheet:
    def __init__(self, file):
        try:
            self.sheet = pygame.image.load(file).convert()
        except pygame.error as e:
            print(f"Error loading file '{file}': {e}")
            raise

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height))
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return sprite


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__(game.all_sprites)
        self.game = game
        self._layer = PLAYER_LAYER

        self.x_change, self.y_change = 0, 0
        self.facing = 'down'
        self.animation_loop = 0

        self.image = self.game.character_spritesheet.get_sprite(3, 2, 32, 32)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

        self.down_animations = [
            self.game.character_spritesheet.get_sprite(3, 2, 32, 32),
            self.game.character_spritesheet.get_sprite(35, 2, 32, 32),
            self.game.character_spritesheet.get_sprite(68, 2, 32, 32)
        ]
        self.up_animations = [
            self.game.character_spritesheet.get_sprite(3, 34, 32, 32),
            self.game.character_spritesheet.get_sprite(35, 34, 32, 32),
            self.game.character_spritesheet.get_sprite(68, 34, 32, 32)
        ]
        self.left_animations = [
            self.game.character_spritesheet.get_sprite(3, 98, 32, 32),
            self.game.character_spritesheet.get_sprite(35, 98, 32, 32),
            self.game.character_spritesheet.get_sprite(68, 98, 32, 32)
        ]
        self.right_animations = [
            self.game.character_spritesheet.get_sprite(3, 66, 32, 32),
            self.game.character_spritesheet.get_sprite(35, 66, 32, 32),
            self.game.character_spritesheet.get_sprite(68, 66, 32, 32)
        ]

    def update(self):
        self.handle_movement()
        self.animate()
        self.handle_collisions()
        self.collide_enemy()

    def handle_movement(self):
        keys = pygame.key.get_pressed()
        self.x_change, self.y_change = 0, 0

        if keys[pygame.K_LEFT]:
            for sprite in self.game.all_sprites:
                sprite.rect.x += PLAYER_SPEED
            self.x_change = -PLAYER_SPEED
            self.facing = 'left'
        if keys[pygame.K_RIGHT]:
            for sprite in self.game.all_sprites:
                sprite.rect.x -= PLAYER_SPEED
            self.x_change = PLAYER_SPEED
            self.facing = 'right'
        if keys[pygame.K_UP]:
            for sprite in self.game.all_sprites:
                sprite.rect.y += PLAYER_SPEED
            self.y_change = -PLAYER_SPEED
            self.facing = 'up'
        if keys[pygame.K_DOWN]:
            for sprite in self.game.all_sprites:
                sprite.rect.y -= PLAYER_SPEED
            self.y_change = PLAYER_SPEED
            self.facing = 'down'

    def collide_enemy(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            self.kill()
            self.game.playing = False
            print("Game Over")

            self.game.death_sound.play()

            pygame.mixer.music.stop()

    def animate(self):
        if self.facing == 'down':
            self.image = self.down_animations[int(self.animation_loop)]
        elif self.facing == 'up':
            self.image = self.up_animations[int(self.animation_loop)]
        elif self.facing == 'left':
            self.image = self.left_animations[int(self.animation_loop)]
        elif self.facing == 'right':
            self.image = self.right_animations[int(self.animation_loop)]

        self.animation_loop += 0.1
        if self.animation_loop >= len(self.down_animations):
            self.animation_loop = 0

    def handle_collisions(self):
        self.rect.x += self.x_change
        if pygame.sprite.spritecollide(self, self.game.blocks, False):
            self.rect.x -= self.x_change

        self.rect.y += self.y_change
        if pygame.sprite.spritecollide(self, self.game.blocks, False):
            self.rect.y -= self.y_change


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__(game.all_sprites, game.enemies)
        self.game = game
        self._layer = ENEMY_LAYER

        self.rect = pygame.Rect(x, y, TILESIZE, TILESIZE)
        self.image = self.game.enemy_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK)

        self.rect.x = x
        self.rect.y = y

        self.left_animations = [
            self.game.enemy_spritesheet.get_sprite(3, 98, 32, 32),
            self.game.enemy_spritesheet.get_sprite(35, 98, 32, 32),
            self.game.enemy_spritesheet.get_sprite(68, 98, 32, 32)
        ]
        self.right_animations = [
            self.game.enemy_spritesheet.get_sprite(3, 66, 32, 32),
            self.game.enemy_spritesheet.get_sprite(35, 66, 32, 32),
            self.game.enemy_spritesheet.get_sprite(68, 66, 32, 32)
        ]

        self.facing = random.choice(['left', 'right'])
        self.animation_loop = 0
        self.movement_loop = 0
        self.max_travel = random.randint(7, 30)

    def update(self):
        self.handle_movement()
        self.animate()
        self.update_position()

    def handle_movement(self):
        if self.facing == 'left':
            self.x_change = -ENEMY_SPEED
            self.movement_loop -= 1
            if self.movement_loop <= -self.max_travel:
                self.facing = 'right'
        else:
            self.x_change = ENEMY_SPEED
            self.movement_loop += 1
            if self.movement_loop >= self.max_travel:
                self.facing = 'left'

    def animate(self):
        if self.facing == 'left':
            self.image = self.left_animations[int(self.animation_loop)]
        elif self.facing == 'right':
            self.image = self.right_animations[int(self.animation_loop)]

        self.animation_loop += 0.1
        if self.animation_loop >= len(self.left_animations):
            self.animation_loop = 0

    def update_position(self):
        self.rect.x += self.x_change


class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__(game.all_sprites, game.blocks)
        self.game = game
        self._layer = BLOCK_LAYER

        self.image = self.game.terrain_spritesheet.get_sprite(960, 448, 32, 32)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__(game.all_sprites)
        self.game = game
        self._layer = GROUND_LAYER

        self.image = self.game.terrain_spritesheet.get_sprite(960, 448, 32, 32)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Button:
    def __init__(self, x, y, width, height, text, fg, bg, content, fontsize):
        self.font = pygame.font.Font("Fonts/Pixel Countdown.otf", 30)
        self.content = content

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.fg = fg
        self.bg = bg

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()

        self.rect.x = self.x
        self.rect.y = self.y

        self.text = self.font.render(text, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.width/2, self.height/2))
        self.image.blit(self.text, self.text_rect)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False
        return False

class Attack(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites, game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.direction = direction

        self.image = self.game.attack_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.move()  # Вызов метода move
        self.collide()

    def move(self):

        if self.direction == 'up':
            self.rect.y -= PLAYER_SPEED
        elif self.direction == 'down':
            self.rect.y += PLAYER_SPEED
        elif self.direction == 'left':
            self.rect.x -= PLAYER_SPEED
        elif self.direction == 'right':
            self.rect.x += PLAYER_SPEED

        if self.rect.x < 0 or self.rect.x > WIN_WIDTH or self.rect.y < 0 or self.rect.y > WIN_HEIGHT:
            self.kill()

    def collide(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, True)
        if hits:
            self.game.kills += 1
            self.kill()


    def animate(self):
        direction = self.game.player.facing

        right_animations = [self.game.attack_spritesheet.get_sprite(0, 64, self.width, self.height),
                            self.game.attack_spritesheet.get_sprite(32, 64, self.width, self.height),
                            self.game.attack_spritesheet.get_sprite(64, 64, self.width, self.height),
                            self.game.attack_spritesheet.get_sprite(96, 64, self.width, self.height),
                            self.game.attack_spritesheet.get_sprite(128, 64, self.width, self.height)]

        down_animations = [self.game.attack_spritesheet.get_sprite(0, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(32, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(64, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(96, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(128, 32, self.width, self.height)]

        left_animations = [self.game.attack_spritesheet.get_sprite(0, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(32, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(64, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(96, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(128, 96, self.width, self.height)]

        up_animations = [self.game.attack_spritesheet.get_sprite(0, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(32, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(64, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(96, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(128, 0, self.width, self.height)]
        if direction == 'up':
            self.image = up_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

        if direction == 'down':
            self.image = down_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

        if direction == 'left':
            self.image = left_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

        if direction == 'right':
            self.image = right_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()
