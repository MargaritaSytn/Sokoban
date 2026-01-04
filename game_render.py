import pygame
from database import get_leaderboard
from ui_config import UIConfig

class GameRenderer:
    # Клас для відмальовування гри
    def __init__(self, screen, tile_size):
        self.screen = screen
        self.TILE_SIZE = tile_size
        self.SCREEN_WIDTH = screen.get_width()
        self.SCREEN_HEIGHT = screen.get_height()
        
        # Ініціалізація шрифтів
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_big = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 32)
        self.font_tiny = pygame.font.SysFont("Arial", 20)
        self.font_mini = pygame.font.SysFont("Arial", 16)
        
        # Завантаження спрайтів
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
        # Безпечне завантаження зображення
        try:
            return pygame.image.load(path).convert_alpha()
        except:
            surf = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
            surf.fill((200, 0, 200))
            return surf

    def _draw_text_centered(self, text, rect, font, color=(255, 240, 240)):
        surf = font.render(text, True, color)
        self.screen.blit(surf, (rect.centerx - surf.get_width()//2, rect.centery - surf.get_height()//2))

    def draw_menu(self, username):
        # Відмальовування головного меню
        self.screen.fill((40, 20, 20))
        
        title = self.font_big.render("SOKOBAN", True, (255, 200, 200))
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        user_text = self.font_small.render(f"Гравець: {username}", True, (255, 180, 180))
        self.screen.blit(user_text, (self.SCREEN_WIDTH//2 - user_text.get_width()//2, 130))
        
        # Використання UIConfig для кнопок меню
        menu_items = [
            (UIConfig.MENU_PLAY, "Грати"),
            (UIConfig.MENU_LEVELS, "Рівні"),
            (UIConfig.MENU_LEADERS, "Лідери"),
            (UIConfig.MENU_EXIT, "Вихід")
        ]
        for coords, txt in menu_items:
            rect = pygame.Rect(*coords)
            pygame.draw.rect(self.screen, (180, 60, 60), rect, border_radius=10)
            self._draw_text_centered(txt, rect, self.font_small)

    def draw_levels_menu(self, levels_count):
        # Відмальовування меню вибору рівнів
        self.screen.fill((40, 20, 20))
        
        title = self.font_big.render("ВИБІР РІВНЯ", True, (255, 200, 200))
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, 60))

        for i in range(levels_count):
            rect = pygame.Rect(*UIConfig.get_level_rect(i))
            pygame.draw.rect(self.screen, (180, 60, 60), rect, border_radius=10)
            self._draw_text_centered(f"Рівень {i+1}", rect, self.font_small)
        
        # Кнопка Назад
        back_rect = pygame.Rect(*UIConfig.BACK_BTN)
        pygame.draw.rect(self.screen, (140, 50, 50), back_rect, border_radius=5)
        self._draw_text_centered("Назад", back_rect, self.font)

    def draw_preview(self, game_logic, level_index):
        # Відмальовування прев'ю рівня
        self.screen.fill((30, 15, 15))
        
        back_rect = pygame.Rect(*UIConfig.BACK_BTN)
        pygame.draw.rect(self.screen, (140, 50, 50), back_rect, border_radius=5)
        self._draw_text_centered("Назад", back_rect, self.font)
        
        title = self.font_big.render(f"Рівень {level_index + 1}", True, (255, 200, 200))
        self.screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Логіка масштабування карти для прев'ю
        map_height = len(game_logic.level)
        map_width = max(len(row) for row in game_logic.level) if game_logic.level else 0
        
        preview_width, preview_height = 600, 400
        scale_x = preview_width / (map_width * self.TILE_SIZE) if map_width > 0 else 1
        scale_y = preview_height / (map_height * self.TILE_SIZE) if map_height > 0 else 1
        scale = min(scale_x, scale_y, 1.0)
        
        tile_preview_size = int(self.TILE_SIZE * scale)
        offset_x = (self.SCREEN_WIDTH - map_width * tile_preview_size) // 2
        offset_y = 100
        
        # Малювання мініатюрної карти
        for y, row in enumerate(game_logic.level):
            for x, tile in enumerate(row):
                px, py = offset_x + x * tile_preview_size, offset_y + y * tile_preview_size
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
        
        # Кнопка Почати
        start_rect = pygame.Rect(*UIConfig.PREVIEW_START)
        pygame.draw.rect(self.screen, (160, 50, 50), start_rect, border_radius=10)
        self._draw_text_centered("Почати", start_rect, self.font)

    def draw_game(self, game_logic, level_index, show_stats=False, global_stats=None):
        # Основний рендер гри з камерою
        self.screen.fill((35, 20, 20))
        
        cam_x = game_logic.player_x * self.TILE_SIZE - self.SCREEN_WIDTH // 2 + self.TILE_SIZE // 2
        cam_y = game_logic.player_y * self.TILE_SIZE - self.SCREEN_HEIGHT // 2 + self.TILE_SIZE // 2

        for y, row in enumerate(game_logic.level):
            for x, tile in enumerate(row):
                draw_x, draw_y = x * self.TILE_SIZE - cam_x, y * self.TILE_SIZE - cam_y
                if -self.TILE_SIZE < draw_x < self.SCREEN_WIDTH and -self.TILE_SIZE < draw_y < self.SCREEN_HEIGHT:
                    self.screen.blit(self.floor_img, (draw_x, draw_y))
                    if (x, y) in game_logic.goals: self.screen.blit(self.goal_img, (draw_x, draw_y))
                    if tile == "#": self.screen.blit(self.wall_img, (draw_x, draw_y))
                    elif tile == "$": self.screen.blit(self.box_img, (draw_x, draw_y))
                    elif tile == "@": self.screen.blit(self.player_sprites[game_logic.current_direction], (draw_x, draw_y))

        pygame.draw.rect(self.screen, (80, 40, 40), (10, 10, 310, 40), border_radius=6)
        info = self.font.render(f"Рівень {level_index + 1} | Кроків: {game_logic.steps_count}", True, (255, 220, 220))
        self.screen.blit(info, (15, 10 + (40 - info.get_height()) // 2))
        
        self.draw_control_buttons(game_logic)
        self.draw_minimap(game_logic)
        self.draw_key_hints()
        
        if show_stats:
            self.draw_statistics_overlay(game_logic, global_stats)

    def draw_control_buttons(self, game_logic):
        # Кнопки Undo/Redo/Reset/Exit через UIConfig
        controls = [
            (UIConfig.GAME_UNDO, "Undo", (60, 140, 60) if game_logic.history_index > 0 else (40, 60, 40)),
            (UIConfig.GAME_REDO, "Redo", (60, 100, 160) if game_logic.history_index < len(game_logic.history) - 1 else (30, 50, 70)),
            (UIConfig.GAME_RESET, "Reset", (200, 120, 40)),
            (UIConfig.GAME_EXIT, "Exit", (180, 50, 50))
        ]
        for coords, txt, color in controls:
            rect = pygame.Rect(*coords)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            self._draw_text_centered(txt, rect, self.font_small)

    def draw_status_msg(self, message):
        """Метод для малювання повідомлень про збереження"""
        msg_surf = self.font_small.render(message, True, (100, 255, 100))
        self.screen.blit(msg_surf, (self.SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, 100))

    def draw_key_hints(self):
        hints = ["M - Карта", "I - Статистика", "F5 - Зберегти", "F9 - Завантажити"]
        y_start = self.SCREEN_HEIGHT - 120
        for i, hint in enumerate(hints):
            text = self.font_mini.render(hint, True, (255, 180, 180))
            self.screen.blit(text, (10, y_start + i * 20))

    def draw_statistics_overlay(self, game_logic, global_stats):
        # Оверлей статистики
        overlay_w, overlay_h = 360, 180
        overlay_x, overlay_y = (self.SCREEN_WIDTH - overlay_w)//2, (self.SCREEN_HEIGHT - overlay_h)//2
        
        surf = pygame.Surface((overlay_w, overlay_h))
        surf.set_alpha(230)
        surf.fill((50, 25, 25))
        self.screen.blit(surf, (overlay_x, overlay_y))

        title = self.font.render("СТАТИСТИКА", True, (255, 200, 100))
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, overlay_y + 8))
        
        boxes_on_goals = sum(1 for y, row in enumerate(game_logic.level) for x, t in enumerate(row) 
                             if (t == "$" and (x, y) in game_logic.goals) or t == "*")
        
        lines = [f"Кроків: {game_logic.steps_count}", f"Ящиків на місці: {boxes_on_goals}"]
        for i, line in enumerate(lines):
            text = self.font_tiny.render(line, True, (255, 230, 230))
            self.screen.blit(text, (overlay_x + 16, overlay_y + 44 + i * 30))

    def draw_full_map(self, game_logic, level_index):
        # Повноекранна карта рівня
        self.screen.fill((25, 15, 20))
        title = self.font_big.render(f"КАРТА РІВНЯ {level_index + 1}", True, (255, 200, 200))
        self.screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

    def draw_minimap(self, game_logic):
        # Відмальовування міні-карти
        map_h = len(game_logic.level)
        map_w = max(len(row) for row in game_logic.level) if game_logic.level else 0
        scale = min(150 / (map_w * self.TILE_SIZE), 150 / (map_h * self.TILE_SIZE), 1.0)
        size = max(int(self.TILE_SIZE * scale), 2)
        
        mx, my = self.SCREEN_WIDTH - (map_w * size) - 10, 10
        pygame.draw.rect(self.screen, (50, 50, 55), (mx-5, my-5, map_w*size+10, map_h*size+10), border_radius=5)
        
        for y, row in enumerate(game_logic.level):
            for x, tile in enumerate(row):
                px, py = mx + x * size, my + y * size
                if tile == "#": color = (80, 80, 85)
                elif tile == "$": color = (50, 200, 50) if (x, y) in game_logic.goals else (139, 90, 43)
                elif tile == "@": color = (255, 220, 50)
                elif (x, y) in game_logic.goals: color = (80, 120, 200)
                else: continue
                pygame.draw.rect(self.screen, color, (px, py, size, size))

    def draw_leaderboard(self, levels_count):
        # Таблиця лідерів
        self.screen.fill((35, 20, 25))
        title = self.font_big.render("ТАБЛИЦЯ ЛІДЕРІВ", True, (255, 200, 200))
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, 40))

        for level_num in range(1, levels_count + 1):
            col, row = (level_num - 1) // 3, (level_num - 1) % 3
            x_pos, current_y = 60 + col * 350, 130 + row * 135
            
            level_title = self.font.render(f"Рівень {level_num}:", True, (255, 180, 120))
            self.screen.blit(level_title, (x_pos, current_y))
            
            leaderboard = get_leaderboard(level_num)
            if leaderboard:
                for idx, (username, steps) in enumerate(leaderboard[:3], 1):
                    entry = self.font_tiny.render(f"{idx}. {username} - {steps} кр.", True, (255, 230, 230))
                    self.screen.blit(entry, (x_pos + 20, current_y + 35 + (idx-1)*22))
            else:
                no_data = self.font_tiny.render("Немає даних", True, (160, 100, 100))
                self.screen.blit(no_data, (x_pos + 20, current_y + 35))
        
        back_rect = pygame.Rect(*UIConfig.BACK_BTN)
        pygame.draw.rect(self.screen, (140, 50, 50), back_rect, border_radius=5)
        self._draw_text_centered("Назад", back_rect, self.font)

    def draw_win_screen(self, level_index, levels_count, steps, has_user):
        self.screen.fill((25, 15, 15))
        win_t = self.font_big.render("РІВЕНЬ ПРОЙДЕНО!", True, (255, 100, 100))
        self.screen.blit(win_t, (self.SCREEN_WIDTH // 2 - win_t.get_width() // 2, 150))
        
        btn_next_rect = pygame.Rect(*UIConfig.WIN_NEXT)
        pygame.draw.rect(self.screen, (180, 60, 60), btn_next_rect, border_radius=10)
        next_text = "Наступний рівень" if level_index < levels_count - 1 else "Завершити"
        self._draw_text_centered(next_text, btn_next_rect, self.font)
        
        btn_menu_rect = pygame.Rect(*UIConfig.WIN_MENU)
        pygame.draw.rect(self.screen, (160, 70, 70), btn_menu_rect, border_radius=10)
        self._draw_text_centered("В меню", btn_menu_rect, self.font)