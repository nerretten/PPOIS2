import pygame
import sys
from settings import screen, WIDTH, HEIGHT, clock, load_json, save_json
from assets import font_main, font_small, font_title

def draw_text(text, font, color, x, y, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y) if center else (x, y))
    screen.blit(surf, rect)

def show_message(msg, sub_msg="PRESS ANY KEY"):
    while True:
        screen.fill((0, 0, 0))
        draw_text(msg, font_title, (255, 255, 255), WIDTH // 2, HEIGHT // 2 - 50, True)
        draw_text(sub_msg, font_main, (200, 200, 200), WIDTH // 2, HEIGHT // 2 + 50, True)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return

def highscore_input(score):
    name = ""
    while True:
        screen.fill((0, 0, 0))
        draw_text("NEW HIGH SCORE!", font_title, (255, 215, 0), WIDTH // 2, 150, True)
        draw_text(f"SCORE: {score}", font_main, (255, 255, 255), WIDTH // 2, 230, True)
        draw_text("ENTER NAME:", font_main, (255, 255, 255), WIDTH // 2, 310, True)
        draw_text(name + "_", font_main, (255, 50, 50), WIDTH // 2, 370, True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10 and event.unicode.isalnum():
                        name += event.unicode
        pygame.display.flip()
        clock.tick(60)

def check_highscores(score):
    scores = load_json('highscores.json')
    if not isinstance(scores, list): scores = []
    top_score = scores[0]['score'] if scores else 0
    if score > top_score:
        name = highscore_input(score)
        scores.insert(0, {"name": name, "score": score})
        save_json('highscores.json', scores[:10])