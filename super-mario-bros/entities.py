import pygame
from settings import cfg, HEIGHT
from assets import *
from ui import draw_text


class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.timer = 40

    def update(self):
        self.y -= 1.5
        self.timer -= 1

    def draw(self, surface, cam_x):
        draw_text(self.text, font_small, self.color, self.x - cam_x, self.y)


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect(topleft=(x, y))


class Block(Entity):
    def __init__(self, x, y, type_char):
        img = img_ground
        if type_char == 'B':
            img = img_block_brick
        elif type_char in ('?', 'Q'):
            img = img_block_q
        elif type_char == 'T':
            img = img_pipe_top
        elif type_char == 'p':
            img = img_pipe_body
        super().__init__(x, y, img)
        self.type = type_char
        self.hit = False

        self.base_y = y
        self.vel_y = 0

    def update(self):
        if self.vel_y != 0 or self.rect.y != self.base_y:
            self.rect.y += self.vel_y
            self.vel_y += 1

            if self.rect.y >= self.base_y:
                self.rect.y = self.base_y
                self.vel_y = 0

    def on_hit(self):
        if self.vel_y == 0 and self.type not in ('T', 'p'):
            self.vel_y = -5

        if self.type in ('?', 'Q') and not self.hit:
            self.hit = True
            self.image = img_block_empty
            return self.type
        return None


class Player(Entity):
    def __init__(self):
        super().__init__(100, 100, img_mario)
        self.vel_x = 0
        self.vel_y = 0
        self.accel = cfg['physics']['acceleration']
        self.friction = cfg['physics']['friction']
        self.max_speed = cfg['physics']['max_speed']
        self.jump_p = cfg['physics']['jump_power']
        self.grav = cfg['physics']['gravity']
        self.score = 0
        self.coins = 0
        self.time = 400
        self.frame_count = 0
        self.alive = True
        self.on_ground = False
        self.death_timer = 0
        self.facing_right = True

    def update(self, blocks, enemies, spawn_queue):
        if not self.alive:
            self.vel_y += self.grav
            self.rect.y += self.vel_y
            self.death_timer += 1
            return
        self.frame_count += 1
        if self.frame_count >= cfg.get('fps', 60):
            self.frame_count = 0
            if self.time > 0:
                self.time -= 1
            else:
                self.die()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x -= self.accel
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x += self.accel
            self.facing_right = True
        else:
            if self.vel_x > 0:
                self.vel_x -= self.friction
            elif self.vel_x < 0:
                self.vel_x += self.friction
            if abs(self.vel_x) < self.friction: self.vel_x = 0
        self.vel_x = max(-self.max_speed, min(self.vel_x, self.max_speed))
        self.rect.x += self.vel_x
        self.check_collision(blocks, 'x', spawn_queue)
        self.vel_y += self.grav
        self.rect.y += self.vel_y
        self.check_collision(blocks, 'y', spawn_queue)
        current_img = img_mario if self.on_ground else img_mario_jump
        if not self.facing_right:
            self.image = pygame.transform.flip(current_img, True, False)
        else:
            self.image = current_img
        if self.rect.y > HEIGHT: self.die()

    def check_collision(self, blocks, axis, spawn_queue):
        self.on_ground = False
        for b in blocks:
            if self.rect.colliderect(b.rect):
                if axis == 'x':
                    if self.vel_x > 0: self.rect.right = b.rect.left
                    if self.vel_x < 0: self.rect.left = b.rect.right
                    self.vel_x = 0
                else:
                    if self.vel_y > 0:
                        self.rect.bottom = b.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                    if self.vel_y < 0:
                        self.rect.top = b.rect.bottom
                        self.vel_y = 0
                        hit_result = b.on_hit()
                        if hit_result == '?':
                            self.coins += 1
                            self.score += 100
                            play_sound('coin.wav')
                            spawn_queue.append({'type': 'text', 'text': '+1', 'x': b.rect.x + 10, 'y': b.rect.top - 20, 'color': (255, 255, 0)})
                        elif hit_result == 'Q':
                            spawn_queue.append({'type': 'goomba', 'x': b.rect.x, 'y': b.rect.top - 34})

    def jump(self):
        if self.on_ground and self.alive:
            self.vel_y = -self.jump_p
            play_sound('jump.wav')

    def die(self):
        if self.alive:
            self.alive = False
            self.vel_y = -15
            pygame.mixer.music.stop()
            play_sound('death.wav')


class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, img_goomba)
        self.speed = cfg['physics']['enemy_speed']
        self.alive = True
        self.timer = 0
        self.vel_y = 0

    def update(self, blocks, goal=None):
        if not self.alive:
            self.timer += 1
            return
        self.vel_y += cfg['physics']['gravity']
        self.rect.y += self.vel_y
        for b in blocks:
            if self.rect.colliderect(b.rect):
                if self.vel_y > 0:
                    self.rect.bottom = b.rect.top
                    self.vel_y = 0
        self.rect.x += self.speed
        hit_wall = False
        for b in blocks:
            if self.rect.colliderect(b.rect):
                hit_wall = True
                break
        if goal and self.rect.colliderect(goal.rect):
            hit_wall = True
        if self.rect.x < 0:
            hit_wall = True
        if hit_wall:
            self.speed *= -1
            self.rect.x += self.speed
        if self.rect.y > HEIGHT:
            self.die()

    def die(self):
        self.alive = False
        self.image = img_goomba_dead
        self.rect.y += 19