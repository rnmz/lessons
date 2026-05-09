import pygame
import json
import os

# --- ИНИЦИАЛИЗАЦИЯ ---
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visual Novel")
clock = pygame.time.Clock()

# --- ЦВЕТА И ШРИФТЫ ---
WHITE, ACCENT = (255, 255, 255), (0, 255, 136)
GRAY_PANEL = (30, 30, 35, 230)
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

# Загрузка сюжета
try:
    with open("ru.json", "r", encoding="utf-8") as f:
        STORY = json.load(f)
except:
    STORY = {}

# --- СИСТЕМНЫЕ ФУНКЦИИ ---

def save_game():
    data = {"scene": current_scene_id, "index": current_text_index, "vol": music_volume}
    with open("save.json", "w") as f:
        json.dump(data, f)

def load_game():
    global current_scene_id, current_text_index, music_volume, current_state
    if os.path.exists("save.json"):
        with open("save.json", "r") as f:
            data = json.load(f)
            current_scene_id, current_text_index, music_volume = data["scene"], data["index"], data["vol"]
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
    """Вызывается при смене сцены для загрузки фона и музыки"""
    global current_bg, current_music_path
    scene = STORY.get(current_scene_id)
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
    btn_start = pygame.Rect(WIDTH//2 - 150, 250, 300, 60)
    btn_load = pygame.Rect(WIDTH//2 - 150, 330, 300, 60)
    slider_rect = pygame.Rect(WIDTH//2 - 150, 480, 300, 10)
    
    # Кнопки
    for b, text in [(btn_start, "НОВАЯ ИГРА"), (btn_load, "ПРОДОЛЖИТЬ")]:
        pygame.draw.rect(screen, (50, 55, 80), b, border_radius=10)
        txt = font_main.render(text, True, WHITE)
        screen.blit(txt, (b.centerx - txt.get_width()//2, b.centery - txt.get_height()//2))
    
    # Громкость
    pygame.draw.rect(screen, (100, 100, 100), slider_rect)
    pygame.draw.rect(screen, ACCENT, (slider_rect.x, slider_rect.y, 300 * music_volume, 10))
    vol_label = font_main.render(f"Громкость: {int(music_volume*100)}%", True, WHITE)
    screen.blit(vol_label, (WIDTH//2 - vol_label.get_width()//2, 440))
    
    return btn_start, btn_load, slider_rect

def draw_game():
    scene = STORY.get(current_scene_id)
    if not scene: return []
    
    if current_bg: screen.blit(current_bg, (0, 0))
    else: screen.fill((20, 20, 20))

    # --- ГЕРОИ (Логика расположения) ---
    char_list = scene.get("chars", [])
    if char_list:
        n = len(char_list)
        char_w = 400
        gap = WIDTH * 0.1 # 10% расстояние
        
        # Если не влезают — накладываем (уменьшаем gap)
        total_w = (char_w * n) + (gap * (n - 1))
        if total_w > WIDTH * 0.95:
            gap = (WIDTH * 0.95 - (char_w * n)) / (n - 1) if n > 1 else 0
            total_w = (char_w * n) + (gap * (n - 1))

        start_x = (WIDTH - total_w) / 2
        for i, path in enumerate(char_list):
            img = get_image(path, True)
            if img:
                # Масштабируем по высоте (600px)
                scale_h = 600
                scale_w = int(img.get_width() * (scale_h / img.get_height()))
                img = pygame.transform.scale(img, (scale_w, scale_h))
                screen.blit(img, (start_x + i * (char_w + gap), HEIGHT - 650))

    # --- ИНТЕРФЕЙС ---
    diag_rect = pygame.Rect(50, HEIGHT - 220, WIDTH - 100, 180)
    surf = pygame.Surface((diag_rect.width, diag_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(surf, GRAY_PANEL, (0, 0, diag_rect.width, diag_rect.height), border_radius=20)
    screen.blit(surf, (diag_rect.x, diag_rect.y))
    
    current_line = scene["text"][current_text_index]
    screen.blit(font_name.render(current_line["name"], True, ACCENT), (diag_rect.x + 30, diag_rect.y + 20))
    screen.blit(font_main.render(current_line["text"], True, WHITE), (diag_rect.x + 30, diag_rect.y + 70))

    # --- ВЫБОРЫ ---
    buttons = []
    if "choice" in current_line:
        for i, (next_id, c_text) in enumerate(current_line["choice"][0].items()):
            b_rect = pygame.Rect(diag_rect.x + 30 + (i * 350), diag_rect.y + 115, 320, 50)
            pygame.draw.rect(screen, (60, 65, 90), b_rect, border_radius=10)
            pygame.draw.rect(screen, ACCENT, b_rect, width=2, border_radius=10)
            bt = font_main.render(c_text, True, WHITE)
            screen.blit(bt, (b_rect.centerx - bt.get_width()//2, b_rect.centery - bt.get_height()//2))
            buttons.append((b_rect, next_id))
    return buttons

# --- ГЛАВНЫЙ ЦИКЛ ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    if current_state == "menu":
        btn_start, btn_load, slider_bg = draw_menu()
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
                    if current_text_index < len(STORY[current_scene_id]["text"]) - 1:
                        current_text_index += 1
                        save_game()
                    else:
                        current_state = "menu"

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
