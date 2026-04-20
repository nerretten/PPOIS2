import pygame
from settings import screen

def get_font(size):
    try:
        return pygame.font.Font('assets/font.ttf', size)
    except:
        return pygame.font.SysFont("Courier", size, bold=True)

font_main = get_font(28)
font_small = get_font(18)
font_title = get_font(50)

def get_img(path, size, color=(255, 0, 0)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill(color)
        return surf

def load_pipe_parts(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        scaled = pygame.transform.scale(img, (size[0], size[1] * 2))
        top = scaled.subsurface((0, 0, size[0], size[1]))
        body = scaled.subsurface((0, size[1], size[0], size[1]))
        return top, body
    except:
        top = pygame.Surface(size)
        top.fill((0, 200, 0))
        body = pygame.Surface(size)
        body.fill((0, 150, 0))
        return top, body

# Загрузка изображений
img_mario = get_img('assets/mario.png', (30, 40), (255, 50, 50))
img_mario_jump = get_img('assets/mario_jump.png', (30, 40), (255, 100, 100))
img_goomba = get_img('assets/goomba.png', (34, 34), (150, 75, 0))
img_goomba_dead = get_img('assets/goomba_dead.png', (34, 15), (100, 50, 0))
img_block_brick = get_img('assets/brick.png', (40, 40), (180, 80, 40))
img_block_q = get_img('assets/question.png', (40, 40), (255, 200, 0))
img_block_empty = get_img('assets/empty.png', (40, 40), (100, 100, 100))
img_ground = get_img('assets/ground.png', (40, 40), (139, 69, 19))
img_coin = get_img('assets/coin.png', (25, 25), (255, 255, 0))
img_castle = get_img('assets/castle.png', (120, 160), (50, 50, 50))
img_pipe_top, img_pipe_body = load_pipe_parts('assets/pipe.png', (40, 40))
img_cloud = get_img('assets/clouds.png', (90, 45), (255, 255, 255))

def play_sound(name):
    try:
        snd = pygame.mixer.Sound(f'assets/{name}')
        if name == 'jump.wav':
            snd.set_volume(0.25)
        if name == 'coin.wav':
            snd.set_volume(1.2)
        snd.play()
    except:
        pass

def play_music(name):
    try:
        pygame.mixer.music.load(f'assets/{name}')
        pygame.mixer.music.play(-1)
    except:
        pass