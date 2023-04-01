import pygame
from pygame.locals import *
from pygame import mixer
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

# screen size
WIDTH = 600
HEIGHT = 936
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')


# define font
font = pygame.font.SysFont('Comic Sans', 60)
# define color
white = (255, 255, 255)


# game variables

ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

hit_sound = True
die_sound = True
point_sound = True


# load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(HEIGHT / 2)
    score = 0
    return score


# bird \/


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying == True:
            # gravity
            self.vel += 0.5  # <--- gravity force
            if self.vel > 8:
                self.vel = 8  # <---- vel will increase infinitly if we don't set a ceil value to it
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if game_over == False:
            # jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10  # <---- heigh of bird's jump

                # wing sound
                jump_sound = mixer.Sound('sound/sfx_wing.wav')
                jump_sound.play()

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # rotate bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -45)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()

        # position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap) / 2]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap) / 2]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(HEIGHT / 2))
bird_group.add(flappy)

# create restart button instance
button = Button(WIDTH // 2 - 50, HEIGHT // 2 - 100, button_img)  # <---- where the button is going to be


run = True
while run:

    clock.tick(fps)

    screen.blit(bg, (0, 0))  # blit means to draw an image on the screen

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    # draw the ground
    screen.blit(ground_img, (ground_scroll, 768))

    # check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and pass_pipe == False:
            pass_pipe = True

        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
                point_sound = mixer.Sound('sound/sfx_point.wav')
                point_sound.play()


    draw_text(str(score), font, white, int(WIDTH) / 2, 20)

    # look for colision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
        if hit_sound:
            hit_sound = mixer.Sound('sound/sfx_hit.wav')
            hit_sound.play()
            hit_sound = False
        if die_sound:
            die_sound = mixer.Sound('sound/sfx_die.wav')
            die_sound.play()
            die_sound = False

    # check if bird has hit the ground
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False
        if hit_sound:
            hit_sound = mixer.Sound('sound/sfx_hit.wav')
            hit_sound.play()
            hit_sound = False
        if die_sound:
            die_sound = mixer.Sound('sound/sfx_die.wav')
            die_sound.play()
            die_sound = False

    if game_over == False and flying == True:

        # generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-150, 150)
            btm_pipe = Pipe(WIDTH, int(HEIGHT / 2) + pipe_height, -1)
            top_pipe = Pipe(WIDTH, int(HEIGHT / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()

    # check for game over and reset
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()
            hit_sound = True
            die_sound = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    pygame.display.update()

pygame.quit()
