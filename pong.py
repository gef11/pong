import pygame
import pygame_gui
import sys
import random

# ширина и высота окна (можно поменять)
WIDTH = 800
HEIGHT = 600

# черный цвет для фона и серый для текста и полоски по середине
BLACK = (0, 0, 0)
GRAY = (170, 170, 170)


# класс для загрузки изображений
class Sprite(pygame.sprite.Sprite):
    def __init__(self, path, x, y):
        super().__init__()
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(center=(x, y))


class Player(Sprite):
    def __init__(self, path, x, y, speed):
        super().__init__(path, x, y)
        self.speed = speed
        self.pos = 0

    def update(self, ball_group):
        self.rect.y += self.pos
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT


class Ball(Sprite):
    def __init__(self, path, x, y, speed, paddles, screen, font, mixer):
        super().__init__(path, x, y)
        self.speed_x = speed * random.choice((-1, 1))
        self.speed_y = speed * random.choice((-1, 1))
        self.paddles = paddles
        self.active = False
        self.score_time = 0
        self.screen = screen
        self.font = font
        self.mixer = mixer

    def update(self):
        if self.active:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y

            if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
                self.mixer.play(0)
                self.speed_y *= -1

            if pygame.sprite.spritecollide(self, self.paddles, False):
                self.mixer.play(0)
                collision_paddle = pygame.sprite.spritecollide(
                    self, self.paddles, False)[0].rect
                if abs(self.rect.right - collision_paddle.left) < 10 and self.speed_x > 0:
                    self.speed_x *= -1
                if abs(self.rect.left - collision_paddle.right) < 10 and self.speed_x < 0:
                    self.speed_x *= -1
                if abs(self.rect.top - collision_paddle.bottom) < 10 and self.speed_y < 0:
                    self.rect.top = collision_paddle.bottom
                    self.speed_y *= -1
                if abs(self.rect.bottom - collision_paddle.top) < 10 and self.speed_y > 0:
                    self.rect.bottom = collision_paddle.top
                    self.speed_y *= -1
        else:
            self.restart_counter()

    def reset_ball(self):
        self.mixer.play(1)
        self.active = False
        self.speed_x *= random.choice((-1, 1))
        self.speed_y *= random.choice((-1, 1))
        self.score_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)

    def restart_counter(self):
        current_time = pygame.time.get_ticks()
        countdown_number = 3

        if current_time - self.score_time <= 700:
            countdown_number = 3
        if 700 < current_time - self.score_time <= 1400:
            countdown_number = 2
        if 1400 < current_time - self.score_time <= 2100:
            countdown_number = 1
        if current_time - self.score_time >= 2100:
            self.active = True

        time_counter = self.font.render(str(countdown_number), True, GRAY)
        time_counter_rect = time_counter.get_rect(
            center=(WIDTH / 2, HEIGHT / 2 + 50))
        pygame.draw.rect(self.screen, BLACK, time_counter_rect)
        self.screen.blit(time_counter, time_counter_rect)


class Opponent(Sprite):
    def __init__(self, path, x, y, speed):
        super().__init__(path, x, y)
        self.speed = speed

    def update(self, ball_group):
        if self.rect.top < ball_group.sprite.rect.y:
            self.rect.y += self.speed
        if self.rect.bottom > ball_group.sprite.rect.y:
            self.rect.y -= self.speed
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT


# класс для запуска игры
class Pong:
    def __init__(self, ball_group, paddles, screen, font, pausemenu, mixer):
        self.player_score = 0
        self.opponent_score = 0
        self.ball_group = ball_group
        self.paddles = paddles
        self.screen = screen
        self.font = font
        self.pausemenu = pausemenu
        self.mixer = mixer

    def run(self):
        self.paddles.draw(self.screen)
        self.ball_group.draw(self.screen)

        self.paddles.update(self.ball_group)
        self.ball_group.update()
        self.reset_ball()
        self.draw_score()

    def reset_ball(self):
        if self.ball_group.sprite.rect.right >= WIDTH:
            self.opponent_score += 1
            self.ball_group.sprite.reset_ball()
        if self.ball_group.sprite.rect.left <= 0:
            self.player_score += 1
            self.ball_group.sprite.reset_ball()

    def draw_score(self):
        player_score = self.font.render(str(self.player_score), True, GRAY)
        opponent_score = self.font.render(
            str(self.opponent_score), True, GRAY)

        player_score_rect = player_score.get_rect(
            midleft=(WIDTH / 2 + 40, HEIGHT / 2))
        opponent_score_rect = opponent_score.get_rect(
            midright=(WIDTH / 2 - 40, HEIGHT / 2))

        self.screen.blit(player_score, player_score_rect)
        self.screen.blit(opponent_score, opponent_score_rect)

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        player.pos -= player.speed
                    if event.key == pygame.K_DOWN:
                        player.pos += player.speed
                    if event.key == pygame.K_ESCAPE:
                        self.pausemenu.pause()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        player.pos += player.speed
                    if event.key == pygame.K_DOWN:
                        player.pos -= player.speed

            screen.fill(BLACK)
            pygame.draw.rect(screen, GRAY, middle_strip)

            pong.run()

            pygame.display.flip()
            clock.tick(60)


class PauseMenu:
    def __init__(self, screen, manager, font):
        self.screen = screen
        self.manager = manager
        self.font = font

    def pause(self):
        self.manager.clear_and_reset()
        resume_rect = pygame.Rect(30, 200, 150, 40)
        resume_rect.center = (400, 150)

        exit_rect = pygame.Rect(30, 200, 150, 40)
        exit_rect.center = (400, 200)

        pause_text = self.font.render('Игра на паузе', True, (255, 0, 0))
        pause_text_rect = pause_text.get_rect(center=(400, 100))

        pause_background = pygame.Surface((300, 170))
        pause_background.fill((150, 150, 170))
        pause_background_rect = pause_background.get_rect(center=(400, 150))

        resume_button = pygame_gui.elements.UIButton(
            relative_rect=resume_rect,
            text='Продолжить игру',
            manager=self.manager
        )

        exit_button = pygame_gui.elements.UIButton(
            relative_rect=exit_rect,
            text='Выйти из игры',
            manager=self.manager
        )
        pause = True
        while pause:
            time_delta = clock.tick(60) / 1000
#            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pause = False
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == resume_button:
                        pause = False
                    if event.ui_element == exit_button:
                        pygame.quit()
                        sys.exit()
                self.manager.process_events(event)

            self.screen.blit(pause_background, pause_background_rect)
            self.screen.blit(pause_text, pause_text_rect)

            self.manager.update(time_delta)
            self.manager.draw_ui(self.screen)
            pygame.display.flip()


class Mixer:
    def __init__(self, *paths):
        self.sounds = []
        self.enabled = True
        for i in paths:
            self.sounds.append(pygame.mixer.Sound(i))

    def play(self, index):
        if self.enabled:
            self.sounds[index].play()

    def toggle(self):
        self.enabled = not self.enabled

    def get_enabled(self):
        return self.enabled


if __name__ == "__main__":
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()

    mixer = Mixer('ball.ogg', 'goal.ogg')
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Pong')

    font = pygame.font.Font(None, 32)
    middle_strip = pygame.Rect(WIDTH / 2 - 2, 0, 4, HEIGHT)

    player = Player('Paddle.png', WIDTH - 20, HEIGHT / 2, 5)
    opponent = Opponent('Paddle.png', 20, WIDTH / 2, 5)
    paddles = pygame.sprite.Group()
    paddles.add(player)
    paddles.add(opponent)

    ball = Ball('Ball.png', WIDTH / 2, HEIGHT / 2, 4, paddles, screen, font, mixer)
    ball_group = pygame.sprite.GroupSingle()
    ball_group.add(ball)

    # инициализация GUI
    manager = pygame_gui.UIManager((WIDTH, HEIGHT))
    start_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((350, 215), (150, 40)),
        text='Начать игру',
        manager=manager
    )
    mixer_toggle_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((350, 275), (150, 40)),
        text='Выключить звук',
        manager=manager
    )
    exit_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((350, 335), (150, 40)),
        text='Выйти из игры',
        manager=manager
    )

    pausemenu = PauseMenu(screen, pygame_gui.UIManager((WIDTH, HEIGHT)), font)

    pong = Pong(ball_group, paddles, screen, font, pausemenu, mixer)

    while True:
        time_delta = clock.tick(60) / 1000
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                # определение конкретной нажатой кнопки
                if event.ui_element == start_button:
                    pong.main_loop()
                if event.ui_element == mixer_toggle_button:
                    mixer.toggle()
                    if mixer.get_enabled():
                        mixer_toggle_button.set_text('Выключить звук')
                    else:
                        mixer_toggle_button.set_text('Включить звук')
                if event.ui_element == exit_button:
                    pygame.quit()
                    sys.exit()

            # подключение менеджера GUI к обработке событий
            manager.process_events(event)

        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()
