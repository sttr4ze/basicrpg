import pygame
from config import *
import sys
from sprites import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption("Hero's Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font("Fonts/Pixel Countdown.otf", 30)
        self.bg = pygame.image.load("img/YSa3d.png")
        self.intro_background = pygame.image.load("img/introbackground.png")

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.Group()
        self.attacks = pygame.sprite.Group()

        self.character_spritesheet = Spritesheet('img/character.png')
        self.terrain_spritesheet = Spritesheet('img/terrain.png')
        self.enemy_spritesheet = Spritesheet('img/enemy.png')
        self.attack_spritesheet = Spritesheet('img/attack.png')

        self.kills = 0

        self.death_sound = pygame.mixer.Sound("music/death_music.mp3")
        pygame.mixer.music.load("music/menu_music.mp3")
        self.win_music = pygame.mixer.Sound("music/win_music.mp3")
        self.death_music = pygame.mixer.Sound("music/death_music.mp3")

    def create_tilemap(self):
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):

                x, y = j * TILESIZE, i * TILESIZE

                if column == 'E' and 0 <= x <= WIN_WIDTH and 0 <= y <= WIN_HEIGHT:
                    Enemy(self, x, y)
                elif column == 'B':
                    Block(self, x, y)
                elif column == 'P':
                    self.player = Player(self, x, y)

    def new_game(self):
        pygame.mixer.music.stop()
        self.death_music.stop()

        self.all_sprites.empty()
        self.blocks.empty()
        self.enemies.empty()
        self.attacks.empty()

        self.create_tilemap()

        self.playing = True

        pygame.mixer.music.load("music/game_music.mp3")
        pygame.mixer.music.play(-1)

        self.kills = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    direction = self.player.facing

                    if direction == 'up':
                        Attack(self, self.player.rect.x, self.player.rect.y - TILESIZE, direction)
                    elif direction == 'down':
                        Attack(self, self.player.rect.x, self.player.rect.y + TILESIZE, direction)
                    elif direction == 'left':
                        Attack(self, self.player.rect.x - TILESIZE, self.player.rect.y, direction)
                    elif direction == 'right':
                        Attack(self, self.player.rect.x + TILESIZE, self.player.rect.y, direction)

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.all_sprites.draw(self.screen)
        pygame.display.update()
        self.clock.tick(FPS)

    def run(self):
        while self.playing:
            self.handle_events()
            self.update()
            self.draw()

    def get_player(self):
        for sprite in self.all_sprites:
            if isinstance(sprite, Player):
                return sprite
        return None

    def adjust_camera(self):
        player = self.get_player()

        if player:
            offset_x = WIN_WIDTH // 2 - player.rect.centerx
            offset_y = WIN_HEIGHT // 2 - player.rect.centery

            for sprite in self.all_sprites:
                sprite.rect.x += offset_x
                sprite.rect.y += offset_y

    def update(self):
        self.all_sprites.update()
        self.adjust_camera()
        self.check_victory()

    def game_over(self):
        pygame.mixer.music.stop()
        self.death_music.play()

        self.playing = False
        self.running = False

    def intro_screen(self):
        # Загрузка музыки меню
        pygame.mixer.music.load("music/menu_music.mp3")
        pygame.mixer.music.play(-1)  # Начать зацикленное воспроизведение

        intro = True
        title = self.font.render("Welcome to Hero's Adventure", True, BLACK)
        title_rect = title.get_rect(x=10, y=10)
        play_button = Button(10, 50, 100, 50, 'Play', WHITE, BLACK, 'Play', 32)

        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False
                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()

                if play_button.is_pressed(mouse_pos, mouse_pressed):
                    # Остановите музыку меню при нажатии кнопки "Play"
                    pygame.mixer.music.stop()
                    intro = False

            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def check_victory(self):
        if self.kills >= 3:

            pygame.mixer.music.stop()
            self.win_music.play()

            self.playing = False
            self.running = False

    def game_over_screen(self):
        game_over_bg = pygame.image.load("img/gameover.png")

        restart_button = Button(WIN_WIDTH // 2 - 50, WIN_HEIGHT // 2, 100, 50, 'Again', WHITE, BLACK, 28, fontsize=28)
        exit_button = Button(WIN_WIDTH // 2 - 50, WIN_HEIGHT // 2 + 70, 100, 50, 'Exit', WHITE, BLACK, 28, fontsize=28)

        self.death_music.play()

        game_over = True
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()

                if restart_button.is_pressed(mouse_pos, mouse_pressed):
                    self.death_music.stop()
                    self.new_game()
                    return

                if exit_button.is_pressed(mouse_pos, mouse_pressed):
                    self.running = False
                    return

            self.screen.blit(game_over_bg, (0, 0))
            self.screen.blit(restart_button.image, restart_button.rect)
            self.screen.blit(exit_button.image, exit_button.rect)

            pygame.display.update()
            self.clock.tick(FPS)


g = Game()
g.intro_screen()
g.new_game()

while g.running:
    g.run()
    g.game_over_screen()

pygame.quit()
sys.exit()
