import pygame
import sys
import random
from settings import screen, WIDTH, clock, cfg, lvl
from assets import play_music, play_sound, img_cloud, img_coin, img_castle, font_main, font_small
from entities import Block, Enemy, Entity, Player, FloatingText
from ui import draw_text, show_message, check_highscores


def run_game():
    play_music('theme.wav')
    player = Player()
    blocks, enemies, coins = [], [], []
    clouds = [(x * 180 + random.randint(-40, 40), random.randint(20, 250)) for x in range(35)]
    floating_texts = []
    spawn_queue = []
    goal = None

    ts = lvl.get('tile_size', 40)

    for r, row in enumerate(lvl.get('map', [])):
        for c, char in enumerate(row):
            x, y = c * ts, r * ts
            if char in ('X', 'B', '?', 'Q', 'T', 'p'):
                blocks.append(Block(x, y, char))
            elif char == 'E':
                enemies.append(Enemy(x, y))
            elif char == 'C':
                coins.append(Entity(x + 10, y + 10, img_coin))
            elif char == 'G':
                goal = Entity(x, y - ts * 3, img_castle)

    cam_x = 0
    running = True
    while running:
        screen.fill((107, 140, 255))
        for cx, cy in clouds:
            screen.blit(img_cloud, (cx - cam_x * 0.3, cy))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w): player.jump()
                if event.key == pygame.K_ESCAPE: running = False

        for b in blocks:
            if hasattr(b, 'update'):
                b.update()

        player.update(blocks, enemies, spawn_queue)

        for s in spawn_queue:
            if s['type'] == 'text':
                floating_texts.append(FloatingText(s['x'], s['y'], s['text'], s.get('color', (255, 255, 255))))
            elif s['type'] == 'goomba':
                enemies.append(Enemy(s['x'], s['y']))
        spawn_queue.clear()

        for e in enemies:
            e.update(blocks, goal)
            if e.alive and player.alive and player.rect.colliderect(e.rect):
                if player.vel_y > 0 and player.rect.bottom < e.rect.centery + 10:
                    e.die()
                    player.vel_y = -10
                    player.score += 100
                    play_sound('stomp.wav')
                    floating_texts.append(FloatingText(e.rect.x, e.rect.y, "+100", (255, 255, 255)))
                else:
                    player.die()

        for c in coins[:]:
            if player.rect.colliderect(c.rect):
                coins.remove(c)
                player.coins += 1
                player.score += 100
                play_sound('coin.wav')
                floating_texts.append(FloatingText(c.rect.x, c.rect.y - 10, "+1", (255, 255, 0)))

        for ft in floating_texts[:]:
            ft.update()
            if ft.timer <= 0: floating_texts.remove(ft)

        if player.rect.x > WIDTH // 2:
            cam_x = player.rect.x - WIDTH // 2

        if goal: screen.blit(goal.image, (goal.rect.x - cam_x, goal.rect.y))
        for b in blocks: screen.blit(b.image, (b.rect.x - cam_x, b.rect.y))
        for c in coins: screen.blit(c.image, (c.rect.x - cam_x, c.rect.y))
        for e in enemies:
            if e.alive or e.timer < 30: screen.blit(e.image, (e.rect.x - cam_x, e.rect.y))
        screen.blit(player.image, (player.rect.x - cam_x, player.rect.y))
        for ft in floating_texts: ft.draw(screen, cam_x)

        draw_text("SCORE", font_small, (255, 255, 255), 50, 10)
        draw_text(f"{player.score:05d}", font_main, (255, 255, 255), 70, 30)
        draw_text("COINS", font_small, (255, 255, 255), 250, 10)
        draw_text(f"x{player.coins:02d}", font_main, (255, 215, 0), 250, 30)
        draw_text("TIME", font_small, (255, 255, 255), WIDTH - 80, 10)
        draw_text(f"{player.time:03d}", font_main, (255, 255, 255), WIDTH - 80, 30)

        if goal and player.rect.colliderect(goal.rect):
            show_message("COURSE CLEAR!", f"FINAL SCORE: {player.score}")
            check_highscores(player.score)
            running = False

        if not player.alive and player.death_timer > 100:
            show_message("GAME OVER")
            check_highscores(player.score)
            running = False

        pygame.display.flip()
        clock.tick(cfg.get('fps', 60))