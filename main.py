import pygame
import sys
from database import init_database, save_score
from auth import LoginWindow
from game_logic import GameLogic, get_global_statistics
from game_render import GameRenderer
from ui_config import UIConfig 

class SokobanApp:
    def __init__(self):
        pygame.init()
        self.TILE_SIZE = 64
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Sokoban")
        
        init_database()
        self.game_logic = GameLogic()
        self.renderer = GameRenderer(self.screen, self.TILE_SIZE)
        self.clock = pygame.time.Clock()
        
        self.state = "menu"
        self.levels_list = ["level1.txt", "level2.txt", "level3.txt", "level4.txt", "level5.txt"]
        self.current_level_index = 0
        self.preview_origin = None
        
        self.logged_in, self.user_id, self.username = LoginWindow().show_login()
        if not self.logged_in:
            self.user_id, self.username = None, "Гость"
            
        self.show_statistics = False
        self.show_full_map = False
        self.save_message = ""
        self.save_message_timer = 0
        self.move_hold = {"up": False, "down": False, "left": False, "right": False}
        self.last_move_tick = 0
        self.MOVE_REPEAT_MS = 200
        
        self.running = True
        self.game_logic.reset_level(self.levels_list[0])

    def run(self):
        while self.running:
            self._update_timers()
            self._handle_events()
            self._update_logic()
            self._draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._process_mouse_click(event.pos)
            
            elif self.state == "game":
                self._process_game_keyboard(event)

    def _process_mouse_click(self, pos):
        if self.state == "menu":
            self._handle_menu_click(pos)
        elif self.state == "levels":
            self._handle_levels_click(pos)
        elif self.state == "preview":
            self._handle_preview_click(pos)
        elif self.state == "game":
            self._handle_game_ui_click(pos)
        elif self.state == "win":
            self._handle_win_click(pos)
        elif self.state == "leaderboard":
            self._handle_back_to_menu_click(pos)

    def _process_game_keyboard(self, event):
        if event.type == pygame.KEYDOWN:
            key_map = {
                pygame.K_w: "up", pygame.K_UP: "up",
                pygame.K_s: "down", pygame.K_DOWN: "down",
                pygame.K_a: "left", pygame.K_LEFT: "left",
                pygame.K_d: "right", pygame.K_RIGHT: "right"
            }
            if event.key in key_map:
                direction = key_map[event.key]
                self.move_hold[direction] = True
                if not self.show_full_map:
                    self._move_player_by_dir(direction)
                    # prevent immediate double-move by updating repeat timer
                    self.last_move_tick = pygame.time.get_ticks()

            if event.key == pygame.K_r:
                self.game_logic.reset_level(self.levels_list[self.current_level_index])
            elif event.key == pygame.K_i:
                self.show_statistics = not self.show_statistics
            elif event.key == pygame.K_m:
                self.show_full_map = not self.show_full_map
            elif event.key == pygame.K_F5:
                self._quick_save()
            elif event.key == pygame.K_F9:
                self._quick_load()
            elif event.key == pygame.K_ESCAPE:
                self.state = "menu"

        elif event.type == pygame.KEYUP:
            key_map = {
                pygame.K_w: "up", pygame.K_UP: "up",
                pygame.K_s: "down", pygame.K_DOWN: "down",
                pygame.K_a: "left", pygame.K_LEFT: "left",
                pygame.K_d: "right", pygame.K_RIGHT: "right"
            }
            if event.key in key_map:
                self.move_hold[key_map[event.key]] = False


    def _handle_menu_click(self, pos):
        if pygame.Rect(*UIConfig.MENU_PLAY).collidepoint(pos):
            self._start_level(0, "menu")
        elif pygame.Rect(*UIConfig.MENU_LEVELS).collidepoint(pos):
            self.state = "levels"
        elif pygame.Rect(*UIConfig.MENU_LEADERS).collidepoint(pos):
            self.state = "leaderboard"
        elif pygame.Rect(*UIConfig.MENU_EXIT).collidepoint(pos):
            self.running = False

    def _handle_levels_click(self, pos):
        for i in range(len(self.levels_list)):
            if pygame.Rect(*UIConfig.get_level_rect(i)).collidepoint(pos):
                self._start_level(i, "levels")
        if pygame.Rect(*UIConfig.BACK_BTN).collidepoint(pos):
            self.state = "menu"

    def _handle_preview_click(self, pos):
        if pygame.Rect(*UIConfig.PREVIEW_START).collidepoint(pos):
            self.state = "game"
        elif pygame.Rect(*UIConfig.BACK_BTN).collidepoint(pos):
            self.state = self.preview_origin or "menu"

    def _handle_game_ui_click(self, pos):
        if pygame.Rect(*UIConfig.GAME_UNDO).collidepoint(pos):
            self.game_logic.undo()
        elif pygame.Rect(*UIConfig.GAME_REDO).collidepoint(pos):
            self.game_logic.redo()
        elif pygame.Rect(*UIConfig.GAME_RESET).collidepoint(pos):
            self.game_logic.reset_level(self.levels_list[self.current_level_index])
        elif pygame.Rect(*UIConfig.GAME_EXIT).collidepoint(pos):
            self.state = "menu"

    def _handle_win_click(self, pos):
        if pygame.Rect(*UIConfig.WIN_NEXT).collidepoint(pos):
            if self.current_level_index < len(self.levels_list) - 1:
                self._start_level(self.current_level_index + 1, "levels")
            else:
                self.state = "menu"
        elif pygame.Rect(*UIConfig.WIN_MENU).collidepoint(pos):
            self.state = "menu"

    def _handle_back_to_menu_click(self, pos):
        if pygame.Rect(*UIConfig.BACK_BTN).collidepoint(pos):
            self.state = "menu"


    def _start_level(self, index, origin):
        self.current_level_index = index
        self.game_logic.reset_level(self.levels_list[index])
        self.state = "preview"
        self.preview_origin = origin
        self.move_hold = {k: False for k in self.move_hold}

    def _update_timers(self):
        if self.save_message_timer > 0:
            self.save_message_timer -= 1
            if self.save_message_timer == 0:
                self.save_message = ""

    def _update_logic(self):
        if self.state == "game" and not self.show_full_map:
            now = pygame.time.get_ticks()
            if now - self.last_move_tick >= self.MOVE_REPEAT_MS:
                for direction, is_held in self.move_hold.items():
                    if is_held:
                        self._move_player_by_dir(direction)
                        self.last_move_tick = now
                        break
            
            if self.game_logic.check_win():
                if self.user_id:
                    save_score(self.user_id, self.current_level_index + 1, self.game_logic.steps_count)
                self.state = "win"

    def _move_player_by_dir(self, direction):
        dirs = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        dx, dy = dirs[direction]
        self.game_logic.move_player(dx, dy, direction)

    def _quick_save(self):
        self.game_logic.save_state_to_binary("quicksave.bin")
        self.save_message, self.save_message_timer = "Гра збережена (F5)", 180

    def _quick_load(self):
        if self.game_logic.load_state_from_binary("quicksave.bin"):
            self.save_message = "Гра загружена (F9)"
        else:
            self.save_message = "Нема збереженої гри!"
        self.save_message_timer = 180


    def _draw(self):
        if self.state == "menu":
            self.renderer.draw_menu(self.username)
        elif self.state == "levels":
            self.renderer.draw_levels_menu(len(self.levels_list))
        elif self.state == "preview":
            self.renderer.draw_preview(self.game_logic, self.current_level_index)
        elif self.state == "game":
            self._draw_game_screen()
        elif self.state == "leaderboard":
            self.renderer.draw_leaderboard(len(self.levels_list))
        elif self.state == "win":
            self.renderer.draw_win_screen(
                self.current_level_index, 
                len(self.levels_list), 
                self.game_logic.steps_count, 
                self.user_id is not None
            )
        pygame.display.flip()

    def _draw_game_screen(self):
        if self.show_full_map:
            self.renderer.draw_full_map(self.game_logic, self.current_level_index)
        else:
            stats = get_global_statistics() if self.show_statistics else None
            self.renderer.draw_game(
                self.game_logic, 
                self.current_level_index, 
                show_stats=self.show_statistics,
                global_stats=stats
            )
            if self.save_message:
                self.renderer.draw_status_msg(self.save_message)

if __name__ == "__main__":
    app = SokobanApp()
    app.run()