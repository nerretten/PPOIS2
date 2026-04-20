import json
import pygame

pygame.init()
pygame.mixer.init()

def load_json(name):
    try:
        with open(name, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_json(name, data):
    with open(name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Загрузка конфигурации (с безопасными значениями по умолчанию на случай отсутствия файла)
cfg_data = load_json('config.json')
cfg = cfg_data if isinstance(cfg_data, dict) else {
    'screen_width': 800, 'screen_height': 600, 'fps': 60,
    'physics': {'acceleration': 0.5, 'friction': 0.2, 'max_speed': 5, 'jump_power': 12, 'gravity': 0.5, 'enemy_speed': 2}
}

lvl_data = load_json('level.json')
lvl = lvl_data if isinstance(lvl_data, dict) else {'tile_size': 40, 'map': []}

WIDTH, HEIGHT = cfg.get('screen_width', 800), cfg.get('screen_height', 600)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Bros - Lab 3")
clock = pygame.time.Clock()