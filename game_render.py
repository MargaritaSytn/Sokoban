import pygame
from database import get_leaderboard

class GameRenderer:
    # Клас для відмальовування гри
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
        # Завантаження зображення
        try:
            return pygame.image.load(path).convert_alpha()
        except:
            surf = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
            surf.fill((200, 0, 200))
            return surf
    
    def draw_menu(self, username):
        # Відмальовування головного меню
        self.screen.fill((40, 20, 20))
        
        title = self.font_big.render("SOKOBAN", True, (255, 200, 200))
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        user_text = self.font_small.render(f"Гравець: {username}", True, (255, 180, 180))
        self.screen.blit(user_text, (self.SCREEN_WIDTH//2 - user_text.get_width()//2, 130))
        
        for i, txt in enumerate(["Грати", "Рівні", "Лідери", "Вихід"]):
            rect = pygame.Rect(300, 200 + i*80, 200, 60)
            pygame.draw.rect(self.screen, (180, 60, 60), rect, border_radius=10)
            st = self.font_small.render(txt, True, (255, 240, 240))
            self.screen.blit(st, (rect.centerx - st.get_width()//2, rect.centery - st.get_height()//2))
    
    def draw_levels_menu(self, levels_count):
        # Відмальовування меню вибору рівнів
        self.screen.fill((40, 20, 20))
        
        title = self.font_big.render("ВИБІР РІВНЯ", True, (255, 200, 200))
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, 60))

        for i in range(levels_count):
            rect = pygame.Rect(300, 180 + i * 70, 200, 50)
            pygame.draw.rect(self.screen, (180, 60, 60), rect, border_radius=10)
            st = self.font_small.render(f"Рівень {i+1}", True, (255, 240, 240))
            self.screen.blit(st, (rect.centerx - st.get_width()//2, rect.centery - st.get_height()//2))
        
        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, (140, 50, 50), back_btn, border_radius=5)
        back_text = self.font.render("Назад", True, (255, 240, 240))
        self.screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2, back_btn.centery - back_text.get_height()//2))
    
    def draw_preview(self, game_logic, level_index):
        # Відмальовування прев'ю рівня
        self.screen.fill((30, 15, 15))
        
        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, (140, 50, 50), back_btn, border_radius=5)
        back_text = self.font.render("Назад", True, (255, 240, 240))
        self.screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2, back_btn.centery - back_text.get_height()//2))
        
        title = self.font_big.render(f"Рівень {level_index + 1}", True, (255, 200, 200))
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
        pygame.draw.rect(self.screen, (160, 50, 50), btn_start, border_radius=10)
        start_text = self.font.render("Почати", True, (255, 240, 240))
        self.screen.blit(start_text, (btn_start.centerx - start_text.get_width()//2, btn_start.centery - start_text.get_height()//2))
    
    def draw_game(self, game_logic, level_index, deadlocks=None, show_stats=False, global_stats=None):
        # Відмальовування ігрового процесу
        self.screen.fill((35, 20, 20))
        
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

        info_box_w, info_box_h = 310, 40
        pygame.draw.rect(self.screen, (80, 40, 40), (10, 10, info_box_w, info_box_h), border_radius=6)
        info = self.font.render(f"Рівень {level_index + 1} | Кроків: {game_logic.steps_count}", True, (255, 220, 220))
        self.screen.blit(info, (15, 10 + (info_box_h - info.get_height()) // 2))
        
        self.draw_control_buttons(game_logic)
        
        self.draw_minimap(game_logic)
        
        self.draw_key_hints()
        
        if show_stats:
            self.draw_statistics_overlay(game_logic, global_stats)
    
    def draw_control_buttons(self, game_logic):
        # Відмальовування кнопок керування
        btn_undo = pygame.Rect(10, 60, 80, 35)
        btn_redo = pygame.Rect(100, 60, 80, 35)
        btn_reset = pygame.Rect(10, 105, 80, 35)
        btn_exit = pygame.Rect(100, 105, 80, 35)
        
        # Undo - зелений (назад у часі - безпечно)
        color_undo = (60, 140, 60) if game_logic.history_index > 0 else (40, 60, 40)
        pygame.draw.rect(self.screen, color_undo, btn_undo, border_radius=5)
        undo_text = self.font_small.render("Undo", True, (240, 255, 240))
        self.screen.blit(undo_text, (btn_undo.centerx - undo_text.get_width()//2, btn_undo.centery - undo_text.get_height()//2))
        
        # Redo - синій (вперед у часі)
        color_redo = (60, 100, 160) if game_logic.history_index < len(game_logic.history) - 1 else (30, 50, 70)
        pygame.draw.rect(self.screen, color_redo, btn_redo, border_radius=5)
        redo_text = self.font_small.render("Redo", True, (240, 245, 255))
        self.screen.blit(redo_text, (btn_redo.centerx - redo_text.get_width()//2, btn_redo.centery - redo_text.get_height()//2))
        
        # Reset - помаранчевий (попередження)
        pygame.draw.rect(self.screen, (200, 120, 40), btn_reset, border_radius=5)
        reset_text = self.font_small.render("Reset", True, (255, 250, 240))
        self.screen.blit(reset_text, (btn_reset.centerx - reset_text.get_width()//2, btn_reset.centery - reset_text.get_height()//2))
        
        # Exit - червоний (вихід)
        pygame.draw.rect(self.screen, (180, 50, 50), btn_exit, border_radius=5)
        exit_text = self.font_small.render("Exit", True, (255, 240, 240))
        self.screen.blit(exit_text, (btn_exit.centerx - exit_text.get_width()//2, btn_exit.centery - exit_text.get_height()//2))
    def draw_key_hints(self):
        """Підказки по клавішах"""
        hints = [
            "M - Карта",
            "I - Статистика",
            "F5 - Зберегти",
            "F9 - Завантажити"
        ]
        
        y_start = self.SCREEN_HEIGHT - 120
        for i, hint in enumerate(hints):
            text = self.font_mini.render(hint, True, (255, 180, 180))
            self.screen.blit(text, (10, y_start + i * 20))
    
    def draw_statistics_overlay(self, game_logic, global_stats):
        # Оверлей зі статистикою
        overlay_w, overlay_h = 360, 180
        overlay = pygame.Surface((overlay_w, overlay_h))
        overlay.set_alpha(230)
        overlay.fill((50, 25, 25))
        overlay_x = self.SCREEN_WIDTH // 2 - overlay_w // 2
        overlay_y = self.SCREEN_HEIGHT // 2 - overlay_h // 2
        self.screen.blit(overlay, (overlay_x, overlay_y))

        title = self.font.render("СТАТИСТИКА", True, (255, 200, 100))
        self.screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, overlay_y + 8))

        steps = game_logic.steps_count
        boxes_total = sum(1 for row in game_logic.level for t in row if t in ["$", "*"])
        boxes_on_goals = 0
        for y, row in enumerate(game_logic.level):
            for x, t in enumerate(row):
                if (t == "$" and (x, y) in game_logic.goals) or t == "*":
                    boxes_on_goals += 1

        y_offset = overlay_y + 44
        stats_lines = [
            f"Кроків зроблено: {steps}",
            f"Ящиків всього: {boxes_total}",
            f"Ящиків на місці: {boxes_on_goals}"
        ]

        for line in stats_lines:
            text = self.font_tiny.render(line, True, (255, 230, 230))
            self.screen.blit(text, (overlay_x + 16, y_offset))
            y_offset += 30

        hint = self.font_mini.render("Натисніть I щоб закрити", True, (200, 150, 150))
        self.screen.blit(hint, (self.SCREEN_WIDTH // 2 - hint.get_width() // 2, overlay_y + overlay_h - 28))
    
    def draw_full_map(self, game_logic, level_index):
        # Повноекранна карта (клавіша M)
        self.screen.fill((25, 15, 20))
        
        title = self.font_big.render(f"КАРТА РІВНЯ {level_index + 1}", True, (255, 200, 200))
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
        
        hint = self.font_small.render("Натисніть M щоб закрити карту", True, (255, 180, 180))
        self.screen.blit(hint, (self.SCREEN_WIDTH // 2 - hint.get_width() // 2, self.SCREEN_HEIGHT - 50))
    
    def draw_minimap(self, game_logic):
        # Відмальовування міні-карти
        map_height = len(game_logic.level)
        map_width = max(len(row) for row in game_logic.level) if game_logic.level else 0
        minimap_max_size = 150
        scale = min(minimap_max_size / (map_width * self.TILE_SIZE), minimap_max_size / (map_height * self.TILE_SIZE), 1.0)
        mini_tile_size = max(int(self.TILE_SIZE * scale), 2)
        
        minimap_width = map_width * mini_tile_size
        minimap_height = map_height * mini_tile_size
        minimap_x = self.SCREEN_WIDTH - minimap_width - 10
        minimap_y = 10
        
        # Рамка міні-карти - темно-сірий
        pygame.draw.rect(self.screen, (50, 50, 55), (minimap_x - 5, minimap_y - 5, minimap_width + 10, minimap_height + 10), border_radius=5)
        
        for y, row in enumerate(game_logic.level):
            for x, tile in enumerate(row):
                px = minimap_x + x * mini_tile_size
                py = minimap_y + y * mini_tile_size
                
                if tile == "#":
                    # Стіни - темно-сірий
                    pygame.draw.rect(self.screen, (80, 80, 85), (px, py, mini_tile_size, mini_tile_size))
                elif tile == "$":
                    # Ящик на цілі - яскраво-зелений, звичайний ящик - коричневий
                    color = (50, 200, 50) if (x, y) in game_logic.goals else (139, 90, 43)
                    pygame.draw.rect(self.screen, color, (px, py, mini_tile_size, mini_tile_size))
                elif tile == "@":
                    # Гравець - яскраво-жовтий
                    pygame.draw.rect(self.screen, (255, 220, 50), (px, py, mini_tile_size, mini_tile_size))
                elif (x, y) in game_logic.goals:
                    # Порожні цілі - блакитний
                    pygame.draw.rect(self.screen, (80, 120, 200), (px, py, mini_tile_size, mini_tile_size))
    
    def draw_leaderboard(self, levels_count):
        # Відмальовування таблиці лідерів
        self.screen.fill((35, 20, 25))
        
        title = self.font_big.render("ТАБЛИЦЯ ЛІДЕРІВ", True, (255, 200, 200))
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, 60))

        y_offset = 140
        for level_num in range(1, levels_count + 1):
            level_title = self.font.render(f"Рівень {level_num}:", True, (255, 180, 120))
            self.screen.blit(level_title, (50, y_offset))
            y_offset += 40
            
            leaderboard = get_leaderboard(level_num)
            if leaderboard:
                for idx, (username, steps) in enumerate(leaderboard[:3], 1):
                    entry_text = self.font_tiny.render(f"{idx}. {username} - {steps} кроків", True, (255, 200, 200))
                    self.screen.blit(entry_text, (70, y_offset))
                    y_offset += 22
            else:
                no_data = self.font_tiny.render("Немає даних", True, (180, 120, 120))
                self.screen.blit(no_data, (70, y_offset))
                y_offset += 22
            
            y_offset += 15
        
        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.screen, (140, 50, 50), back_btn, border_radius=5)
        back_text = self.font.render("Назад", True, (255, 240, 240))
        self.screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2, back_btn.centery - back_text.get_height()//2))
    
    def draw_win_screen(self, level_index, levels_count, steps, has_user):
    # Відмальовування екрана перемоги
        self.screen.fill((25, 15, 15))
        
        msg = "РІВЕНЬ ПРОЙДЕНО!"
        win_t = self.font_big.render(msg, True, (255, 100, 100))
        self.screen.blit(win_t, (self.SCREEN_WIDTH // 2 - win_t.get_width() // 2, 150))
        
        steps_text = self.font.render(f"Кроків: {steps}", True, (255, 220, 220))
        self.screen.blit(steps_text, (self.SCREEN_WIDTH // 2 - steps_text.get_width() // 2, 250))
        
        if has_user:
            saved_text = self.font_small.render("Результат збережено!", True, (255, 150, 150))
            self.screen.blit(saved_text, (self.SCREEN_WIDTH // 2 - saved_text.get_width() // 2, 290))
        
        btn_next = pygame.Rect(250, 350, 300, 60)
        pygame.draw.rect(self.screen, (180, 60, 60), btn_next, border_radius=10)
        next_text = "Наступний рівень" if level_index < levels_count - 1 else "Завершити"
        t_next = self.font.render(next_text, True, (255, 240, 240))
        self.screen.blit(t_next, (btn_next.centerx - t_next.get_width()//2, btn_next.centery - t_next.get_height()//2))
        
        btn_menu = pygame.Rect(250, 430, 300, 60)
        pygame.draw.rect(self.screen, (160, 70, 70), btn_menu, border_radius=10)
        menu_text = self.font.render("В меню", True, (255, 240, 240))
        self.screen.blit(menu_text, (btn_menu.centerx - menu_text.get_width()//2, btn_menu.centery - menu_text.get_height()//2))