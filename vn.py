import pygame
import json
import os

# --- ИНИЦИАЛИЗАЦИЯ ---
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visual Novel Multi-Lang")
clock = pygame.time.Clock()

FONT_PATH = "your_font_file.ttf"

# --- ЦВЕТА И ШРИФТЫ ---
WHITE, ACCENT = (255, 255, 255), (0, 255, 136)
GRAY_PANEL = (30, 30, 35, 230)

try:
    font_main = pygame.font.Font(FONT_PATH, 28)
    font_name = pygame.font.Font(FONT_PATH, 32)
except:
    print("Шрифт не найден, используем системный")
    font_main = pygame.font.SysFont("Arial", 28)
    font_name = pygame.font.SysFont("Arial", 32, bold=True)

# --- ПЕРЕМЕННЫЕ СОСТОЯНИЯ ---
current_state = "menu"
current_scene_id = "start"
current_text_index = 0
music_volume = 0.5
current_bg = None
current_music_path = ""
cached_images = {}

# --- ЛОКАЛИЗАЦИЯ ---
current_lang = "ru"  # По умолчанию
LANGS = {}

def load_all_languages():
    global LANGS
    for lang in ["ru", "en"]:
        try:
            with open(f"{lang}.json", "r", encoding="utf-8") as f:
                LANGS[lang] = json.load(f)
        except:
            LANGS[lang] = {}

load_all_languages()

# Словарь для элементов интерфейса
UI_TEXT = {
    "ru": {"start": "НОВАЯ ИГРА", "load": "ПРОДОЛЖИТЬ", "vol": "Громкость", "lang": "Язык: RU"},
    "en": {"start": "NEW GAME", "load": "CONTINUE", "vol": "Volume", "lang": "Lang: EN"}
}

# --- СИСТЕМНЫЕ ФУНКЦИИ ---

def save_game():
    data = {
        "scene": current_scene_id, 
        "index": current_text_index, 
        "vol": music_volume, 
        "lang": current_lang
    }
    with open("save.json", "w") as f:
        json.dump(data, f)

def load_game():
    global current_scene_id, current_text_index, music_volume, current_state, current_lang
    if os.path.exists("save.json"):
        with open("save.json", "r") as f:
            data = json.load(f)
            current_scene_id = data.get("scene", "start")
            current_text_index = data.get("index", 0)
            music_volume = data.get("vol", 0.5)
            current_lang = data.get("lang", "ru")
            
        pygame.mixer.music.set_volume(music_volume)
        current_state = "game"
        update_assets()
        return True
    return False

def get_image(path, is_char=False):
    if not path: return None
    if path not in cached_images:
        try:
            img = pygame.image.load(path).convert_alpha()
            if not is_char: img = pygame.transform.scale(img, (WIDTH, HEIGHT))
            cached_images[path] = img
        except: return None
    return cached_images[path]

def update_assets():
    global current_bg, current_music_path
    story = LANGS.get(current_lang, {})
    scene = story.get(current_scene_id)
    if not scene: return
    
    current_bg = get_image(scene.get("background"))
    
    m_path = scene.get("audio")
    if m_path and m_path != current_music_path:
        try:
            pygame.mixer.music.load(m_path)
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(-1)
            current_music_path = m_path
        except: pass

# --- ОТРИСОВКА ---

def draw_menu():
    screen.fill((10, 15, 25))
    ui = UI_TEXT[current_lang]
    
    btn_start = pygame.Rect(WIDTH//2 - 150, 200, 300, 60)
    btn_load = pygame.Rect(WIDTH//2 - 150, 280, 300, 60)
    btn_lang = pygame.Rect(WIDTH//2 - 150, 360, 300, 60)
    slider_rect = pygame.Rect(WIDTH//2 - 150, 500, 300, 10)
    
    # Кнопки
    menu_btns = [(btn_start, ui["start"]), (btn_load, ui["load"]), (btn_lang, ui["lang"])]
    for b, text in menu_btns:
        pygame.draw.rect(screen, (50, 55, 80), b, border_radius=10)
        txt = font_main.render(text, True, WHITE)
        screen.blit(txt, (b.centerx - txt.get_width()//2, b.centery - txt.get_height()//2))
    
    # Громкость
    pygame.draw.rect(screen, (100, 100, 100), slider_rect)
    pygame.draw.rect(screen, ACCENT, (slider_rect.x, slider_rect.y, 300 * music_volume, 10))
    vol_label = font_main.render(f"{ui['vol']}: {int(music_volume*100)}%", True, WHITE)
    screen.blit(vol_label, (WIDTH//2 - vol_label.get_width()//2, 460))
    
    return btn_start, btn_load, btn_lang, slider_rect

def draw_text_multiline(surface, text, pos, width, font, color):
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] < width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))

    # Отрисовываем каждую строку
    x, y = pos
    for line in lines:
        line_surf = font.render(line, True, color)
        surface.blit(line_surf, (x, y))
        y += font.get_linesize() # Смещаемся вниз на высоту строки

def draw_game():
    story = LANGS.get(current_lang, {})
    scene = story.get(current_scene_id)
    if not scene: return []
    
    # 1. Фон
    if current_bg: 
        screen.blit(current_bg, (0, 0))
    else: 
        screen.fill((20, 20, 20))

    # 2. Персонажи (улучшенное позиционирование)
    char_list = scene.get("chars", [])
    if char_list:
        n = len(char_list)
        # Рассчитываем позиции, чтобы герои стояли симметрично
        section_w = WIDTH // (n + 1)
        for i, path in enumerate(char_list):
            img = get_image(path, True)
            if img:
                scale_h = 600
                scale_w = int(img.get_width() * (scale_h / img.get_height()))
                img = pygame.transform.scale(img, (scale_w, scale_h))
                # Центрируем каждого персонажа в его "секции"
                pos_x = section_w * (i + 1) - (scale_w // 2)
                screen.blit(img, (pos_x, HEIGHT - 650))

    # 3. Диалоговое окно
    diag_rect = pygame.Rect(50, HEIGHT - 220, WIDTH - 100, 180)
    # Создаем полупрозрачную подложку
    surf = pygame.Surface((diag_rect.width, diag_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(surf, GRAY_PANEL, (0, 0, diag_rect.width, diag_rect.height), border_radius=20)
    screen.blit(surf, (diag_rect.x, diag_rect.y))
    
    current_line = scene["text"][current_text_index]
    
    # Имя героя (используем font_name)
    name_label = font_name.render(current_line["name"], True, ACCENT)
    screen.blit(name_label, (diag_rect.x + 30, diag_rect.y + 15))
    
    # Текст реплики (используем font_main и многострочность)
    text_area_width = diag_rect.width - 60
    draw_text_multiline(
        screen, 
        current_line["text"], 
        (diag_rect.x + 30, diag_rect.y + 65), 
        text_area_width, 
        font_main,    %
        WHITE
    )

    # 4. Кнопки выбора
    buttons = []
    if "choice" in current_line:
        choices = current_line["choice"][0]
        # Рассчитываем ширину кнопок в зависимости от их количества
        btn_w = 320
        gap = 20
        for i, (next_id, c_text) in enumerate(choices.items()):
            # Размещаем кнопки в ряд под текстом
            b_rect = pygame.Rect(diag_rect.x + 30 + (i * (btn_w + gap)), diag_rect.y + 115, btn_w, 45)
            
            # Эффект при наведении (опционально, если mouse_pos доступен глобально)
            color = (80, 85, 110) if b_rect.collidepoint(pygame.mouse.get_pos()) else (60, 65, 90)
            
            pygame.draw.rect(screen, color, b_rect, border_radius=10)
            pygame.draw.rect(screen, ACCENT, b_rect, width=2, border_radius=10)
            
            # Текст на кнопке (тоже кастомным шрифтом)
            bt = font_main.render(c_text, True, WHITE)
            screen.blit(bt, (b_rect.centerx - bt.get_width()//2, b_rect.centery - bt.get_height()//2))
            
            buttons.append((b_rect, next_id))
            
    return buttons

# --- ГЛАВНЫЙ ЦИКЛ ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    if current_state == "menu":
        btn_start, btn_load, btn_lang, slider_bg = draw_menu()
    else:
        game_btns = draw_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_state == "menu":
                if btn_start.collidepoint(mouse_pos):
                    current_scene_id, current_text_index, current_state = "start", 0, "game"
                    update_assets()
                elif btn_load.collidepoint(mouse_pos):
                    load_game()
                elif btn_lang.collidepoint(mouse_pos):
                    # Переключение RU <-> EN
                    current_lang = "en" if current_lang == "ru" else "ru"
                elif slider_bg.collidepoint(mouse_pos):
                    music_volume = (mouse_pos[0] - slider_bg.x) / slider_bg.width
                    pygame.mixer.music.set_volume(music_volume)

            elif current_state == "game":
                if game_btns:
                    for b_rect, next_id in game_btns:
                        if b_rect.collidepoint(mouse_pos):
                            current_scene_id, current_text_index = next_id, 0
                            update_assets()
                            save_game()
                else:
                    story = LANGS.get(current_lang, {})
                    if current_text_index < len(story[current_scene_id]["text"]) - 1:
                        current_text_index += 1
                        save_game()
                    else:
                        current_state = "menu"

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
