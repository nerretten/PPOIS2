import pygame
import sys
from settings import screen, WIDTH, clock, load_json
from assets import font_title, font_main, font_small
from ui import draw_text
from game import run_game


def show_highscores():
    scores = load_json('highscores.json')
    if not isinstance(scores, list): scores = []
    while True:
        screen.fill((0, 0, 0))
        draw_text("TOP PLAYERS", font_title, (255, 215, 0), WIDTH // 2, 80, True)
        for i, s in enumerate(scores[:5]):
            draw_text(f"{i + 1}. {s['name']} - {s['score']}", font_main, (255, 255, 255), WIDTH // 2, 180 + i * 50, True)
        draw_text("PRESS ESC TO BACK", font_small, (150, 150, 150), WIDTH // 2, 500, True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        pygame.display.flip()


def show_help():
    while True:
        screen.fill((0, 0, 0))
        draw_text("HELP / CONTROLS", font_title, (255, 255, 255), WIDTH // 2, 100, True)
        draw_text("ARROWS / WASD - MOVE & JUMP", font_main, (200, 200, 200), WIDTH // 2, 250, True)
        draw_text("STOMP ENEMIES TO KILL", font_main, (200, 200, 200), WIDTH // 2, 310, True)
        draw_text("REACH THE CASTLE TO WIN", font_main, (200, 200, 200), WIDTH // 2, 370, True)
        draw_text("PRESS ESC TO BACK", font_small, (150, 150, 150), WIDTH // 2, 500, True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        pygame.display.flip()


def menu():
    pygame.mixer.music.stop()
    while True:
        screen.fill((0, 0, 0))
        draw_text("SUPER MARIO LAB 3", font_title, (255, 50, 50), WIDTH // 2, 100, True)
        opts = ["1. START GAME", "2. HIGHSCORES", "3. HELP", "4. EXIT"]
        for i, opt in enumerate(opts):
            draw_text(opt, font_main, (255, 255, 255), WIDTH // 2, 220 + i * 60, True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: run_game()
                if event.key == pygame.K_2: show_highscores()
                if event.key == pygame.K_3: show_help()
                if event.key == pygame.K_4:
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    menu()