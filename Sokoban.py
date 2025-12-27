import pygame
import sys
import os

pygame.init()

# --- Настройки ---
TILE_SIZE = 64
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sokoban - Camera System")

font = pygame.font.SysFont("Arial", 24, bold=True)
font_big = pygame.font.SysFont("Arial", 72, bold=True)
font_small = pygame.font.SysFont("Arial", 32)

# --- Данные уровней ---
game_state = "menu" 
levels_list = ["level1.txt", "level2.txt", "level3.txt", "level4.txt", "level5.txt"]
current_level_index = 0
show_preview = False  # Флаг для показа превью карты

# --- Загрузка изображений ---
def load_img(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except:
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((200, 0, 200)) 
        return surf

player_sprites = {
    "down": load_img("images/down/player_down_1.png"),
    "up": load_img("images/up/player_up_1.png"),
    "left": load_img("images/left/player_left_1.png"),
    "right": load_img("images/right/player_right_1.png")
}
wall_img = load_img("images/walls/block_01.png")
floor_img = load_img("images/ground/ground_06.png")
box_img = load_img("images/boxes/crate_02.png")
goal_img = load_img("images/enviroment/environment_02.png")

current_direction = "down"
player_img = player_sprites[current_direction]

# --- Логика уровней ---
level = []
goals = []
player_x, player_y = 0, 0
history = []  # История ходов для отката
history_index = -1  # Текущая позиция в истории

def load_level_data(filename):
    path = f"levels/{filename}"
    if not os.path.exists(path):
        return [["#"]*15 for _ in range(15)] # Заглушка для теста больших карт
    with open(path, "r", encoding="utf-8") as f:
        return [list(line.rstrip("\n")) for line in f]

def save_state():
    """Сохраняет текущее состояние игры в историю"""
    global history, history_index
    # Создаём копию уровня и позиции игрока
    state = {
        "level": [row[:] for row in level],
        "player_pos": (player_x, player_y),
        "direction": current_direction
    }
    # Удаляем всю историю после текущей позиции (если делали откат)
    history = history[:history_index + 1]
    history.append(state)
    history_index += 1

def undo():
    """Откат на шаг назад"""
    global level, player_x, player_y, current_direction, player_img, history_index
    if history_index > 0:
        history_index -= 1
        state = history[history_index]
        level = [row[:] for row in state["level"]]
        player_x, player_y = state["player_pos"]
        current_direction = state["direction"]
        player_img = player_sprites[current_direction]

def redo():
    """Откат вперёд"""
    global level, player_x, player_y, current_direction, player_img, history_index
    if history_index < len(history) - 1:
        history_index += 1
        state = history[history_index]
        level = [row[:] for row in state["level"]]
        player_x, player_y = state["player_pos"]
        current_direction = state["direction"]
        player_img = player_sprites[current_direction]

def reset_level(index):
    global level, goals, player_x, player_y, current_direction, player_img, current_level_index, history, history_index
    current_level_index = index
    level = load_level_data(levels_list[index])
    goals = [(x, y) for y, row in enumerate(level) for x, ch in enumerate(row) if ch in [".", "*"]]
    current_direction = "down"
    player_img = player_sprites[current_direction]
    history = []
    history_index = -1
    
    for y, row in enumerate(level):
        for x, ch in enumerate(row):
            if ch == "@":
                player_x, player_y = x, y
    
    # Сохраняем начальное состояние
    save_state()

def move_player(dx, dy, direction):
    global player_x, player_y, current_direction, player_img
    current_direction = direction
    player_img = player_sprites[direction]
    nx, ny = player_x + dx, player_y + dy
    nnx, nny = player_x + 2 * dx, player_y + 2 * dy

    if not (0 <= ny < len(level) and 0 <= nx < len(level[0])): return
    target = level[ny][nx]
    if target == "#": return
    
    moved = False
    if target == "$":
        if 0 <= nny < len(level) and 0 <= nnx < len(level[0]):
            after_box = level[nny][nnx]
            if after_box in [" ", "."]:
                level[nny][nnx] = "$"
                level[ny][nx] = "@"
                level[player_y][player_x] = "." if (player_x, player_y) in goals else " "
                player_x, player_y = nx, ny
                moved = True
    elif target in [" ", "."]:
        level[ny][nx] = "@"
        level[player_y][player_x] = "." if (player_x, player_y) in goals else " "
        player_x, player_y = nx, ny
        moved = True
    
    # Сохраняем состояние только если был совершён ход
    if moved:
        save_state()

def check_win():
    for (x, y) in goals:
        if level[y][x] != "$": return False
    return True

# --- Цикл игры ---
reset_level(0)
running = True
clock = pygame.time.Clock()

while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "menu":
                if pygame.Rect(300, 250, 200, 60).collidepoint(mx, my):
                    reset_level(0)
                    show_preview = True
                    game_state = "preview"
                elif pygame.Rect(300, 330, 200, 60).collidepoint(mx, my):
                    game_state = "levels"
                elif pygame.Rect(300, 410, 200, 60).collidepoint(mx, my):
                    running = False
            elif game_state == "levels":
                # Упрощенная логика кнопок уровней для примера
                for i in range(len(levels_list)):
                    rect = pygame.Rect(300, 120 + i * 70, 200, 50)
                    if rect.collidepoint(mx, my):
                        reset_level(i)
                        show_preview = True
                        game_state = "preview"
                if pygame.Rect(20, 20, 100, 40).collidepoint(mx, my):
                    game_state = "menu"
            elif game_state == "preview":
                # Клик по кнопке "Начать"
                if pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50).collidepoint(mx, my):
                    game_state = "game"
                # Клик по кнопке "Назад"
                elif pygame.Rect(20, 20, 100, 40).collidepoint(mx, my):
                    game_state = "levels"
            elif game_state == "game":
                # Проверка кликов по кнопкам управления
                if pygame.Rect(10, 60, 80, 35).collidepoint(mx, my):  # Undo
                    undo()
                elif pygame.Rect(100, 60, 80, 35).collidepoint(mx, my):  # Redo
                    redo()
                elif pygame.Rect(10, 105, 80, 35).collidepoint(mx, my):  # Reset
                    reset_level(current_level_index)
                elif pygame.Rect(100, 105, 80, 35).collidepoint(mx, my):  # Exit
                    game_state = "menu"
            elif game_state == "win":
                if pygame.Rect(250, 350, 300, 60).collidepoint(mx, my):
                    if current_level_index < len(levels_list) - 1:
                        reset_level(current_level_index + 1)
                        show_preview = True
                        game_state = "preview"
                    else:
                        game_state = "menu"

        if game_state == "game" and event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]: move_player(0, -1, "up")
            elif event.key in [pygame.K_s, pygame.K_DOWN]: move_player(0, 1, "down")
            elif event.key in [pygame.K_a, pygame.K_LEFT]: move_player(-1, 0, "left")
            elif event.key in [pygame.K_d, pygame.K_RIGHT]: move_player(1, 0, "right")
            elif event.key == pygame.K_r:  # Reset
                reset_level(current_level_index)
            elif event.key == pygame.K_ESCAPE:  # Exit to menu
                game_state = "menu"
            elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+Z - Undo
                undo()
            elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+Y - Redo
                redo()
            if check_win(): game_state = "win"

    # --- Отрисовка с камерой ---
    if game_state == "preview":
        screen.fill((30, 30, 30))
        
        # Кнопка "Назад" в левом верхнем углу
        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(screen, (150, 150, 150), back_btn, border_radius=5)
        back_text = font.render("Назад", True, (0, 0, 0))
        screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2, back_btn.centery - back_text.get_height()//2))
        
        # Заголовок
        title = font_big.render(f"Уровень {current_level_index + 1}", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Вычисляем размеры карты
        map_height = len(level)
        map_width = max(len(row) for row in level) if level else 0
        
        # Вычисляем масштаб для превью (чтобы карта поместилась в область 600x400)
        preview_width = 600
        preview_height = 400
        scale_x = preview_width / (map_width * TILE_SIZE) if map_width > 0 else 1
        scale_y = preview_height / (map_height * TILE_SIZE) if map_height > 0 else 1
        scale = min(scale_x, scale_y, 1.0)  # Не увеличиваем, только уменьшаем
        
        tile_preview_size = int(TILE_SIZE * scale)
        
        # Центрируем превью
        offset_x = (SCREEN_WIDTH - map_width * tile_preview_size) // 2
        offset_y = 100
        
        # Рисуем превью карты
        for y, row in enumerate(level):
            for x, tile in enumerate(row):
                px = offset_x + x * tile_preview_size
                py = offset_y + y * tile_preview_size
                
                # Рисуем уменьшенные тайлы
                if tile_preview_size > 0:
                    floor_scaled = pygame.transform.scale(floor_img, (tile_preview_size, tile_preview_size))
                    screen.blit(floor_scaled, (px, py))
                    
                    if (x, y) in goals:
                        goal_scaled = pygame.transform.scale(goal_img, (tile_preview_size, tile_preview_size))
                        screen.blit(goal_scaled, (px, py))
                    
                    if tile == "#":
                        wall_scaled = pygame.transform.scale(wall_img, (tile_preview_size, tile_preview_size))
                        screen.blit(wall_scaled, (px, py))
                    elif tile == "$":
                        box_scaled = pygame.transform.scale(box_img, (tile_preview_size, tile_preview_size))
                        screen.blit(box_scaled, (px, py))
                    elif tile == "@":
                        player_scaled = pygame.transform.scale(player_img, (tile_preview_size, tile_preview_size))
                        screen.blit(player_scaled, (px, py))
        
        # Кнопка "Начать"
        btn_start = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        pygame.draw.rect(screen, (50, 150, 50), btn_start, border_radius=10)
        start_text = font.render("Начать", True, (255, 255, 255))
        screen.blit(start_text, (btn_start.centerx - start_text.get_width()//2, btn_start.centery - start_text.get_height()//2))

    elif game_state == "game":
        screen.fill((40, 40, 40))
        
        # ВЫЧИСЛЕНИЕ КАМЕРЫ
        # Мы хотим, чтобы игрок (player_x * TILE_SIZE) был в центре экрана (SCREEN_WIDTH // 2)
        cam_x = player_x * TILE_SIZE - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        cam_y = player_y * TILE_SIZE - SCREEN_HEIGHT // 2 + TILE_SIZE // 2

        # Рисуем карту относительно камеры
        for y, row in enumerate(level):
            for x, tile in enumerate(row):
                # Позиция на экране = Позиция в мире - Позиция камеры
                draw_x = x * TILE_SIZE - cam_x
                draw_y = y * TILE_SIZE - cam_y
                
                # Оптимизация: рисуем только то, что видно на экране
                if -TILE_SIZE < draw_x < SCREEN_WIDTH and -TILE_SIZE < draw_y < SCREEN_HEIGHT:
                    screen.blit(floor_img, (draw_x, draw_y))
                    if (x, y) in goals: screen.blit(goal_img, (draw_x, draw_y))
                    if tile == "#": screen.blit(wall_img, (draw_x, draw_y))
                    elif tile == "$": screen.blit(box_img, (draw_x, draw_y))
                    elif tile == "@": screen.blit(player_img, (draw_x, draw_y))

        # UI (Рисуем ПОВЕРХ карты, без учета камеры)
        # Панель информации
        pygame.draw.rect(screen, (70, 70, 70), (10, 10, 180, 40), border_radius=5)
        info = font.render(f"Уровень {current_level_index + 1}", True, (255, 255, 255))
        screen.blit(info, (20, 15))
        
        # Кнопки управления
        btn_undo = pygame.Rect(10, 60, 80, 35)
        btn_redo = pygame.Rect(100, 60, 80, 35)
        btn_reset = pygame.Rect(10, 105, 80, 35)
        btn_exit = pygame.Rect(100, 105, 80, 35)
        
        # Undo
        color_undo = (100, 150, 100) if history_index > 0 else (60, 60, 60)
        pygame.draw.rect(screen, color_undo, btn_undo, border_radius=5)
        undo_text = font_small.render("Undo", True, (255, 255, 255))
        screen.blit(undo_text, (btn_undo.centerx - undo_text.get_width()//2, btn_undo.centery - undo_text.get_height()//2))
        
        # Redo
        color_redo = (100, 150, 100) if history_index < len(history) - 1 else (60, 60, 60)
        pygame.draw.rect(screen, color_redo, btn_redo, border_radius=5)
        redo_text = font_small.render("Redo", True, (255, 255, 255))
        screen.blit(redo_text, (btn_redo.centerx - redo_text.get_width()//2, btn_redo.centery - redo_text.get_height()//2))
        
        # Reset
        pygame.draw.rect(screen, (150, 100, 100), btn_reset, border_radius=5)
        reset_text = font_small.render("Reset", True, (255, 255, 255))
        screen.blit(reset_text, (btn_reset.centerx - reset_text.get_width()//2, btn_reset.centery - reset_text.get_height()//2))
        
        # Exit
        pygame.draw.rect(screen, (100, 100, 150), btn_exit, border_radius=5)
        exit_text = font_small.render("Exit", True, (255, 255, 255))
        screen.blit(exit_text, (btn_exit.centerx - exit_text.get_width()//2, btn_exit.centery - exit_text.get_height()//2))
        
        # Мини-карта в правом верхнем углу
        map_height = len(level)
        map_width = max(len(row) for row in level) if level else 0
        minimap_max_size = 150
        scale = min(minimap_max_size / (map_width * TILE_SIZE), minimap_max_size / (map_height * TILE_SIZE), 1.0)
        mini_tile_size = max(int(TILE_SIZE * scale), 2)
        
        minimap_width = map_width * mini_tile_size
        minimap_height = map_height * mini_tile_size
        minimap_x = SCREEN_WIDTH - minimap_width - 10
        minimap_y = 10
        
        # Фон мини-карты
        pygame.draw.rect(screen, (40, 40, 40), (minimap_x - 5, minimap_y - 5, minimap_width + 10, minimap_height + 10), border_radius=5)
        
        # Рисуем мини-карту
        for y, row in enumerate(level):
            for x, tile in enumerate(row):
                px = minimap_x + x * mini_tile_size
                py = minimap_y + y * mini_tile_size
                
                # Используем цвета вместо картинок для производительности
                if tile == "#":
                    pygame.draw.rect(screen, (100, 100, 100), (px, py, mini_tile_size, mini_tile_size))
                elif tile == "$":
                    color = (0, 200, 0) if (x, y) in goals else (139, 69, 19)
                    pygame.draw.rect(screen, color, (px, py, mini_tile_size, mini_tile_size))
                elif tile == "@":
                    pygame.draw.rect(screen, (255, 255, 0), (px, py, mini_tile_size, mini_tile_size))
                elif (x, y) in goals:
                    pygame.draw.rect(screen, (50, 50, 150), (px, py, mini_tile_size, mini_tile_size))

    elif game_state == "menu":
        screen.fill((50, 50, 50))
        # (Тут твой код отрисовки меню)
        t = font_big.render("SOKOBAN", True, (255, 255, 255))
        screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 100))
        # Отрисовка кнопок "Играть", "Уровни"...
        for i, txt in enumerate(["Играть", "Уровни", "Выход"]):
            rect = pygame.Rect(300, 250 + i*80, 200, 60)
            pygame.draw.rect(screen, (200, 200, 200), rect, border_radius=10)
            st = font_small.render(txt, True, (0, 0, 0))
            screen.blit(st, (rect.centerx - st.get_width()//2, rect.centery - st.get_height()//2))

    elif game_state == "levels":
        screen.fill((50, 50, 50))
        title = font_big.render("ВЫБОР УРОВНЯ", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        for i in range(len(levels_list)):
            rect = pygame.Rect(300, 120 + i * 70, 200, 50)
            pygame.draw.rect(screen, (200, 200, 200), rect, border_radius=10)
            st = font_small.render(f"Уровень {i+1}", True, (0, 0, 0))
            screen.blit(st, (rect.centerx - st.get_width()//2, rect.centery - st.get_height()//2))
        
        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(screen, (150, 150, 150), back_btn, border_radius=5)
        back_text = font.render("Назад", True, (0, 0, 0))
        screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2, back_btn.centery - back_text.get_height()//2))

    elif game_state == "win":
        screen.fill((20, 20, 20))
        msg = "УРОВЕНЬ ПРОЙДЕН!"
        win_t = font_big.render(msg, True, (0, 255, 0))
        screen.blit(win_t, (SCREEN_WIDTH // 2 - win_t.get_width() // 2, 200))
        btn_next = pygame.Rect(250, 350, 300, 60)
        pygame.draw.rect(screen, (50, 180, 50), btn_next, border_radius=10)
        next_text = "Следующий уровень" if current_level_index < len(levels_list) - 1 else "В меню"
        t_next = font.render(next_text, True, (255, 255, 255))
        screen.blit(t_next, (btn_next.centerx - t_next.get_width()//2, btn_next.centery - t_next.get_height()//2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()