import pygame, json

# Инициализация
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ваше название игры")
clock = pygame.time.Clock()

# --- ЗАГРУЗКА РЕСУРСОВ ---
# Используем try-except, чтобы игра не вылетала, если файлов нет
try:
    bg_img = pygame.image.load("bg.png").convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
    hero_img = pygame.image.load("hero.png").convert_alpha()
    # Немного уменьшим героя, если он слишком большой
    hero_img = pygame.transform.scale(hero_img, (400, 600)) 
except:
    print("Ошибка: Файлы bg.png или hero.png не найдены!")
    bg_img = None
    hero_img = None

# Цвета и шрифты
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY_PANEL = (30, 30, 35, 220)
ACCENT = (0, 255, 136)

font_ui = pygame.font.SysFont("Arial", 50, bold=True)
font_main = pygame.font.SysFont("Arial", 26)
font_btn = pygame.font.SysFont("Arial", 22, bold=True)

# --- СОСТОЯНИЯ И СЮЖЕТ ---
LANGUAGE_FILE = "ru.json"
STATE_MENU = "menu"
STATE_GAME = "game"
current_state = STATE_MENU
current_scene_id = "start"

STORY = json.load(open(LANGUAGE_FILE))

def draw_menu():
    screen.fill((10, 15, 25))
    title = font_ui.render("LEGEND OF PYGAME", True, ACCENT)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
    
    btn_rect = pygame.Rect(WIDTH//2 - 150, 400, 300, 70)
    pygame.draw.rect(screen, (0, 80, 150), btn_rect, border_radius=15)
    
    txt = font_main.render("ИГРАТЬ", True, WHITE)
    screen.blit(txt, (btn_rect.centerx - txt.get_width()//2, btn_rect.centery - txt.get_height()//2))
    return btn_rect

def draw_game():
    # 1. Фон
    if bg_img:
        screen.blit(bg_img, (0, 0))
    else:
        screen.fill((50, 50, 50))

    # 2. Персонаж (справа)
    if hero_img:
        screen.blit(hero_img, (WIDTH - 500, HEIGHT - 650))

    # 3. Плашка для текста (снизу)
    text_panel = pygame.Rect(50, HEIGHT - 220, WIDTH - 100, 180)
    surface = pygame.Surface((text_panel.width, text_panel.height), pygame.SRCALPHA)
    pygame.draw.rect(surface, GRAY_PANEL, (0, 0, text_panel.width, text_panel.height), border_radius=20)
    screen.blit(surface, (text_panel.x, text_panel.y))
    
    # Текст текущей сцены
    scene = STORY[current_scene_id]
    words = font_main.render(scene["text"], True, WHITE)
    screen.blit(words, (80, HEIGHT - 190))

    # 4. Кнопки выбора
    buttons = []
    for i, choice in enumerate(scene["choices"]):
        b_rect = pygame.Rect(80 + (i * 320), HEIGHT - 110, 300, 50)
        pygame.draw.rect(screen, (60, 60, 70), b_rect, border_radius=10)
        pygame.draw.rect(screen, ACCENT, b_rect, width=2, border_radius=10)
        
        b_txt = font_btn.render(choice["text"], True, WHITE)
        screen.blit(b_txt, (b_rect.centerx - b_txt.get_width()//2, b_rect.centery - b_txt.get_height()//2))
        buttons.append((b_rect, choice["next"]))
    return buttons

# --- ГЛАВНЫЙ ЦИКЛ ---
running = True
menu_button = None

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_state == STATE_MENU:
                if menu_button and menu_button.collidepoint(mouse_pos):
                    current_state = STATE_GAME
                    current_scene_id = "start"
            
            elif current_state == STATE_GAME:
                for b_rect, next_id in game_buttons:
                    if b_rect.collidepoint(mouse_pos):
                        if next_id == "menu_return":
                            current_state = STATE_MENU
                        else:
                            current_scene_id = next_id

    # Отрисовка
    if current_state == STATE_MENU:
        menu_button = draw_menu()
    else:
        game_buttons = draw_game()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
