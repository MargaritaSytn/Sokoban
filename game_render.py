import pygame
from database import get_leaderboard

class GameRenderer:
    """Класс для отрисовки игры"""
    def __init__(self, screen, tile_size):
        self.screen = screen
        self.TILE_SIZE = tile_size
        self.SCREEN_WIDTH = screen.get_width()
        self.SCREEN_HEIGHT = screen.get_height()
        
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_big = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 32)
        self.font_tiny = pygame.font.SysFont("Arial", 20)
        self.font_mini = pygame.font.SysFont("Arial", 16)
        
        self.player_sprites = {
            "down": self.load_img("images/down/player_down_1.png"),
            "up": self.load_img("images/up/player_up_1.png"),
            "left": self.load_img("images/left/player_left_1.png"),
            "right": self.load_img("images/right/player_right_1.png")
        }
        self.wall_img = self.load_img("images/walls/block_01.png")
        self.floor_img = self.load_img("images/ground/ground_06.png")
        self.box_img = self.load_img("images/boxes/crate_02.png")
        self.goal_img = self.load_img("images/enviroment/environment_02.png")
    
    def load_img(self, path):
        """Загрузка изображения"""
        try:
            return pygame.image.load(path).convert_alpha()
        except:
            surf = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
            surf.fill((200, 0, 200))
            return surf
    
    def draw_menu(self, username):
        """Отрисовка главного меню"""
        self.screen.fill((50, 50, 50))
        
        title = self.font_big.render("SOKOBAN", True, (255, 255, 255))
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        user_text = self.font_small.render(f"Игрок: {username}", True, (200, 200, 200))
        self.screen.blit(user_text, (self.SCREEN_WIDTH//2 - user_text.get_width()//2, 130))
        
        for i, txt in enumerate(["Играть", "Уровни", "Лидеры", "Выход"]):
            rect = pygame.Rect(300, 200 + i*80, 200, 60)
            pygame.draw.rect(self.screen, (200, 200, 200), rect, border_radius=10)
            st = self.font_small.render(txt, True, (0, 0, 0))
            self.screen.blit(st, (rect.centerx - st.get_width()//2, rect.centery - st.get_height()//2))
    
    def draw_levels_menu(self, levels_count):
        """Отрисовка меню выбора уровней"""
        self.screen.fill((50, 50, 50))
        
        title = self.font_big.render("ВЫБОР УРОВНЯ", True, (255, 255, 255))
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, 60))

        # Move level entries further down for better spacing under the title
        for i in range(levels_count):
            rect = pygame.Rect(300, 180 + i * 70, 200, 50)
            pygame.draw.rect(self.screen, (200, 200, 200), rect, border_radius=10)
            st = self.font_small.render(f"Уровень {i+1}", True, (0, 0, 0))
            self.screen.blit(st, (rect.centerx - st.get_width()//2, rect.centery - st.get_height()//2))
        
        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, (150, 150, 150), back_btn, border_radius=5)
        back_text = self.font.render("Назад", True, (0, 0, 0))
        self.screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2, back_btn.centery - back_text.get_height()//2))
    
    def draw_preview(self, game_logic, level_index):
        """Отрисовка превью уровня"""
        self.screen.fill((30, 30, 30))
        
        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, (150, 150, 150), back_btn, border_radius=5)
        back_text = self.font.render("Назад", True, (0, 0, 0))
        self.screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2, back_btn.centery - back_text.get_height()//2))
        
        title = self.font_big.render(f"Уровень {level_index + 1}", True, (255, 255, 255))
        self.screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        map_height = len(game_logic.level)
        map_width = max(len(row) for row in game_logic.level) if game_logic.level else 0
        
        preview_width, preview_height = 600, 400
        scale_x = preview_width / (map_width * self.TILE_SIZE) if map_width > 0 else 1
        scale_y = preview_height / (map_height * self.TILE_SIZE) if map_height > 0 else 1
        scale = min(scale_x, scale_y, 1.0)
        
        tile_preview_size = int(self.TILE_SIZE * scale)
        offset_x = (self.SCREEN_WIDTH - map_width * tile_preview_size) // 2
        offset_y = 100
        
        for y, row in enumerate(game_logic.level):
            for x, tile in enumerate(row):
                px = offset_x + x * tile_preview_size
                py = offset_y + y * tile_preview_size
                
                if tile_preview_size > 0:
                    floor_scaled = pygame.transform.scale(self.floor_img, (tile_preview_size, tile_preview_size))
                    self.screen.blit(floor_scaled, (px, py))
                    
                    if (x, y) in game_logic.goals:
                        goal_scaled = pygame.transform.scale(self.goal_img, (tile_preview_size, tile_preview_size))
                        self.screen.blit(goal_scaled, (px, py))
                    
                    if tile == "#":
                        wall_scaled = pygame.transform.scale(self.wall_img, (tile_preview_size, tile_preview_size))
                        self.screen.blit(wall_scaled, (px, py))
                    elif tile == "$":
                        box_scaled = pygame.transform.scale(self.box_img, (tile_preview_size, tile_preview_size))
                        self.screen.blit(box_scaled, (px, py))
                    elif tile == "@":
                        player_scaled = pygame.transform.scale(self.player_sprites[game_logic.current_direction], (tile_preview_size, tile_preview_size))
                        self.screen.blit(player_scaled, (px, py))
        
        btn_start = pygame.Rect(self.SCREEN_WIDTH // 2 - 100, self.SCREEN_HEIGHT - 80, 200, 50)
        pygame.draw.rect(self.screen, (50, 150, 50), btn_start, border_radius=10)
        start_text = self.font.render("Начать", True, (255, 255, 255))
        self.screen.blit(start_text, (btn_start.centerx - start_text.get_width()//2, btn_start.centery - start_text.get_height()//2))
    
    def draw_game(self, game_logic, level_index, deadlocks=None, show_stats=False, global_stats=None):
        """Отрисовка игрового процесса"""
        self.screen.fill((40, 40, 40))
        
        cam_x = game_logic.player_x * self.TILE_SIZE - self.SCREEN_WIDTH // 2 + self.TILE_SIZE // 2
        cam_y = game_logic.player_y * self.TILE_SIZE - self.SCREEN_HEIGHT // 2 + self.TILE_SIZE // 2

        for y, row in enumerate(game_logic.level):
            for x, tile in enumerate(row):
                draw_x = x * self.TILE_SIZE - cam_x
                draw_y = y * self.TILE_SIZE - cam_y
                
                if -self.TILE_SIZE < draw_x < self.SCREEN_WIDTH and -self.TILE_SIZE < draw_y < self.SCREEN_HEIGHT:
                    self.screen.blit(self.floor_img, (draw_x, draw_y))
                    if (x, y) in game_logic.goals: 
                        self.screen.blit(self.goal_img, (draw_x, draw_y))
                    if tile == "#": 
                        self.screen.blit(self.wall_img, (draw_x, draw_y))
                    elif tile == "$": 
                        self.screen.blit(self.box_img, (draw_x, draw_y))
                    elif tile == "@": 
                        self.screen.blit(self.player_sprites[game_logic.current_direction], (draw_x, draw_y))

        # Make info box slightly larger so steps value fits reliably
        info_box_w, info_box_h = 310, 40
        pygame.draw.rect(self.screen, (70, 70, 70), (10, 10, info_box_w, info_box_h), border_radius=6)
        info = self.font.render(f"Уровень {level_index + 1} | Шаги: {game_logic.steps_count}", True, (255, 255, 255))
        # vertically center the text inside the larger box
        self.screen.blit(info, (15, 10 + (info_box_h - info.get_height()) // 2))
        
        self.draw_control_buttons(game_logic)
        
        self.draw_minimap(game_logic)
        
        self.draw_key_hints()
        
        if show_stats:
            self.draw_statistics_overlay(game_logic, global_stats)
        
        # Deadlock visualization removed per request
    
    def draw_control_buttons(self, game_logic):
        """Отрисовка кнопок управления"""
        btn_undo = pygame.Rect(10, 60, 80, 35)
        btn_redo = pygame.Rect(100, 60, 80, 35)
        btn_reset = pygame.Rect(10, 105, 80, 35)
        btn_exit = pygame.Rect(100, 105, 80, 35)
        
        color_undo = (100, 150, 100) if game_logic.history_index > 0 else (60, 60, 60)
        pygame.draw.rect(self.screen, color_undo, btn_undo, border_radius=5)
        undo_text = self.font_small.render("Undo", True, (255, 255, 255))
        self.screen.blit(undo_text, (btn_undo.centerx - undo_text.get_width()//2, btn_undo.centery - undo_text.get_height()//2))
        
        color_redo = (100, 150, 100) if game_logic.history_index < len(game_logic.history) - 1 else (60, 60, 60)
        pygame.draw.rect(self.screen, color_redo, btn_redo, border_radius=5)
        redo_text = self.font_small.render("Redo", True, (255, 255, 255))
        self.screen.blit(redo_text, (btn_redo.centerx - redo_text.get_width()//2, btn_redo.centery - redo_text.get_height()//2))
        
        pygame.draw.rect(self.screen, (150, 100, 100), btn_reset, border_radius=5)
        reset_text = self.font_small.render("Reset", True, (255, 255, 255))
        self.screen.blit(reset_text, (btn_reset.centerx - reset_text.get_width()//2, btn_reset.centery - reset_text.get_height()//2))
        
        pygame.draw.rect(self.screen, (100, 100, 150), btn_exit, border_radius=5)
        exit_text = self.font_small.render("Exit", True, (255, 255, 255))
        self.screen.blit(exit_text, (btn_exit.centerx - exit_text.get_width()//2, btn_exit.centery - exit_text.get_height()//2))
    
    def draw_key_hints(self):
        """Подсказки по клавишам"""
        hints = [
            "M - Карта",
            "I - Статистика",
            "F5 - Сохранить",
            "F9 - Загрузить"
        ]
        
        y_start = self.SCREEN_HEIGHT - 120
        for i, hint in enumerate(hints):
            text = self.font_mini.render(hint, True, (180, 180, 180))
            self.screen.blit(text, (10, y_start + i * 20))
    
    def draw_statistics_overlay(self, game_logic, global_stats):
        """Оверлей со статистикой"""
        # Shrink overlay so it doesn't leave half-empty space and fill with text
        overlay_w, overlay_h = 360, 180
        overlay = pygame.Surface((overlay_w, overlay_h))
        overlay.set_alpha(230)
        overlay.fill((40, 40, 60))
        overlay_x = self.SCREEN_WIDTH // 2 - overlay_w // 2
        overlay_y = self.SCREEN_HEIGHT // 2 - overlay_h // 2
        self.screen.blit(overlay, (overlay_x, overlay_y))

        title = self.font.render("СТАТИСТИКА", True, (255, 255, 100))
        self.screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, overlay_y + 8))

        # Show only requested stats: steps, total boxes, boxes on goals
        steps = game_logic.steps_count
        boxes_total = sum(1 for row in game_logic.level for t in row if t in ["$", "*"])
        boxes_on_goals = 0
        for y, row in enumerate(game_logic.level):
            for x, t in enumerate(row):
                if (t == "$" and (x, y) in game_logic.goals) or t == "*":
                    boxes_on_goals += 1

        y_offset = overlay_y + 44
        stats_lines = [
            f"Шагов сделано: {steps}",
            f"Ящиков всего: {boxes_total}",
            f"Ящиков на месте: {boxes_on_goals}"
        ]

        for line in stats_lines:
            text = self.font_tiny.render(line, True, (255, 255, 255))
            self.screen.blit(text, (overlay_x + 16, y_offset))
            y_offset += 30

        # Hint placed below text to avoid overlap
        hint = self.font_mini.render("Нажмите I чтобы закрыть", True, (150, 150, 150))
        self.screen.blit(hint, (self.SCREEN_WIDTH // 2 - hint.get_width() // 2, overlay_y + overlay_h - 28))
    
    def draw_full_map(self, game_logic, level_index):
        """Полноэкранная карта (клавиша M)"""
        self.screen.fill((20, 20, 30))
        
        title = self.font_big.render(f"КАРТА УРОВНЯ {level_index + 1}", True, (255, 255, 255))
        self.screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        map_height = len(game_logic.level)
        map_width = max(len(row) for row in game_logic.level) if game_logic.level else 0
        
        available_width = self.SCREEN_WIDTH - 100
        available_height = self.SCREEN_HEIGHT - 150
        
        scale_x = available_width / (map_width * self.TILE_SIZE) if map_width > 0 else 1
        scale_y = available_height / (map_height * self.TILE_SIZE) if map_height > 0 else 1
        scale = min(scale_x, scale_y, 1.0)
        
        tile_size = max(int(self.TILE_SIZE * scale), 8)
        
        offset_x = (self.SCREEN_WIDTH - map_width * tile_size) // 2
        offset_y = 100
        
        for y, row in enumerate(game_logic.level):
            for x, tile in enumerate(row):
                px = offset_x + x * tile_size
                py = offset_y + y * tile_size
                
                floor_scaled = pygame.transform.scale(self.floor_img, (tile_size, tile_size))
                self.screen.blit(floor_scaled, (px, py))
                
                if (x, y) in game_logic.goals:
                    goal_scaled = pygame.transform.scale(self.goal_img, (tile_size, tile_size))
                    self.screen.blit(goal_scaled, (px, py))
                
                if tile == "#":
                    wall_scaled = pygame.transform.scale(self.wall_img, (tile_size, tile_size))
                    self.screen.blit(wall_scaled, (px, py))
                elif tile == "$":
                    box_scaled = pygame.transform.scale(self.box_img, (tile_size, tile_size))
                    self.screen.blit(box_scaled, (px, py))
                elif tile == "@":
                    player_scaled = pygame.transform.scale(self.player_sprites[game_logic.current_direction], (tile_size, tile_size))
                    self.screen.blit(player_scaled, (px, py))
                
                # visited overlay removed per request (no blue visited cells)
        
        hint = self.font_small.render("Нажмите M чтобы закрыть карту", True, (200, 200, 200))
        self.screen.blit(hint, (self.SCREEN_WIDTH // 2 - hint.get_width() // 2, self.SCREEN_HEIGHT - 50))
        
        # Legend & visited-count removed per request
    
    def draw_minimap(self, game_logic):
        """Отрисовка мини-карты"""
        map_height = len(game_logic.level)
        map_width = max(len(row) for row in game_logic.level) if game_logic.level else 0
        minimap_max_size = 150
        scale = min(minimap_max_size / (map_width * self.TILE_SIZE), minimap_max_size / (map_height * self.TILE_SIZE), 1.0)
        mini_tile_size = max(int(self.TILE_SIZE * scale), 2)
        
        minimap_width = map_width * mini_tile_size
        minimap_height = map_height * mini_tile_size
        minimap_x = self.SCREEN_WIDTH - minimap_width - 10
        minimap_y = 10
        
        pygame.draw.rect(self.screen, (40, 40, 40), (minimap_x - 5, minimap_y - 5, minimap_width + 10, minimap_height + 10), border_radius=5)
        
        for y, row in enumerate(game_logic.level):
            for x, tile in enumerate(row):
                px = minimap_x + x * mini_tile_size
                py = minimap_y + y * mini_tile_size
                
                if tile == "#":
                    pygame.draw.rect(self.screen, (100, 100, 100), (px, py, mini_tile_size, mini_tile_size))
                elif tile == "$":
                    color = (0, 200, 0) if (x, y) in game_logic.goals else (139, 69, 19)
                    pygame.draw.rect(self.screen, color, (px, py, mini_tile_size, mini_tile_size))
                elif tile == "@":
                    pygame.draw.rect(self.screen, (255, 255, 0), (px, py, mini_tile_size, mini_tile_size))
                elif (x, y) in game_logic.goals:
                    pygame.draw.rect(self.screen, (50, 50, 150), (px, py, mini_tile_size, mini_tile_size))
    
    def draw_leaderboard(self, levels_count):
        """Отрисовка таблицы лидеров"""
        self.screen.fill((30, 30, 50))
        
        title = self.font_big.render("ТАБЛИЦА ЛИДЕРОВ", True, (255, 255, 255))
        # Move title down so it doesn't overlap the back button
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, 60))

        # Start listing leaderboard entries below the title
        y_offset = 140
        for level_num in range(1, levels_count + 1):
            level_title = self.font.render(f"Уровень {level_num}:", True, (255, 200, 100))
            self.screen.blit(level_title, (50, y_offset))
            y_offset += 40
            
            leaderboard = get_leaderboard(level_num)
            if leaderboard:
                for idx, (username, steps) in enumerate(leaderboard[:3], 1):
                    entry_text = self.font_tiny.render(f"{idx}. {username} - {steps} шагов", True, (200, 200, 200))
                    self.screen.blit(entry_text, (70, y_offset))
                    y_offset += 22
            else:
                no_data = self.font_tiny.render("Нет данных", True, (150, 150, 150))
                self.screen.blit(no_data, (70, y_offset))
                y_offset += 22
            
            y_offset += 15
        
        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, (150, 150, 150), back_btn, border_radius=5)
        back_text = self.font.render("Назад", True, (0, 0, 0))
        self.screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2, back_btn.centery - back_text.get_height()//2))
    
    def draw_win_screen(self, level_index, levels_count, steps, has_user):
        """Отрисовка экрана победы"""
        self.screen.fill((20, 20, 20))
        
        msg = "УРОВЕНЬ ПРОЙДЕН!"
        win_t = self.font_big.render(msg, True, (0, 255, 0))
        self.screen.blit(win_t, (self.SCREEN_WIDTH // 2 - win_t.get_width() // 2, 150))
        
        steps_text = self.font.render(f"Шагов: {steps}", True, (255, 255, 255))
        self.screen.blit(steps_text, (self.SCREEN_WIDTH // 2 - steps_text.get_width() // 2, 250))
        
        if has_user:
            saved_text = self.font_small.render("Результат сохранён!", True, (100, 255, 100))
            self.screen.blit(saved_text, (self.SCREEN_WIDTH // 2 - saved_text.get_width() // 2, 290))
        
        btn_next = pygame.Rect(250, 350, 300, 60)
        pygame.draw.rect(self.screen, (50, 180, 50), btn_next, border_radius=10)
        next_text = "Следующий уровень" if level_index < levels_count - 1 else "Завершить"
        t_next = self.font.render(next_text, True, (255, 255, 255))
        self.screen.blit(t_next, (btn_next.centerx - t_next.get_width()//2, btn_next.centery - t_next.get_height()//2))
        
        btn_menu = pygame.Rect(250, 430, 300, 60)
        pygame.draw.rect(self.screen, (100, 100, 180), btn_menu, border_radius=10)
        menu_text = self.font.render("В меню", True, (255, 255, 255))
        self.screen.blit(menu_text, (btn_menu.centerx - menu_text.get_width()//2, btn_menu.centery - menu_text.get_height()//2))