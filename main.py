import pygame
import sys
from database import init_database, save_score
from auth import LoginWindow
from game_logic import GameLogic, get_global_statistics, reset_global_statistics
from game_render import GameRenderer

pygame.init()

TILE_SIZE = 64
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sokoban")

# Підготовка гри. Ініціалізація бази даних, створення об’єкта логіки гри, створення об’єкта для малювання
init_database()
game_logic = GameLogic()
renderer = GameRenderer(screen, TILE_SIZE)

# Вхід користувача
login_window = LoginWindow()
logged_in, user_id, username = login_window.show_login()

if logged_in:
    current_user_id = user_id
    current_username = username
else:
    current_user_id = None
    current_username = "Гість"

# Скидання глобальної статистики при новому запуску гри
game_state = "menu"
levels_list = ["level1.txt", "level2.txt", "level3.txt", "level4.txt", "level5.txt"]
current_level_index = 0
preview_origin = None

show_statistics = False
show_full_map = False
current_deadlocks = None
save_message = ""
save_message_timer = 0

MOVE_REPEAT_MS = 200
move_hold = {"up": False, "down": False, "left": False, "right": False}
last_move_tick = 0

game_logic.reset_level(levels_list[0])

running = True
clock = pygame.time.Clock()

while running:
    mx, my = pygame.mouse.get_pos()

    # Таймер повідомлення про збереження 
    if save_message_timer > 0:
        save_message_timer -= 1
        if save_message_timer == 0:
            save_message = ""
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "menu":
                if pygame.Rect(300, 200, 200, 60).collidepoint(mx, my):
                    game_logic.reset_level(levels_list[0])
                    current_level_index = 0
                    game_state = "preview"
                    preview_origin = "menu"
                    move_hold = {"up": False, "down": False, "left": False, "right": False}
                    last_move_tick = pygame.time.get_ticks()
                elif pygame.Rect(300, 280, 200, 60).collidepoint(mx, my):
                    game_state = "levels"
                elif pygame.Rect(300, 360, 200, 60).collidepoint(mx, my):
                    game_state = "leaderboard"
                elif pygame.Rect(300, 440, 200, 60).collidepoint(mx, my):
                    running = False
                    
            elif game_state == "levels":
                for i in range(len(levels_list)):
                    rect = pygame.Rect(300, 180 + i * 70, 200, 50)
                    if rect.collidepoint(mx, my):
                        game_logic.reset_level(levels_list[i])
                        current_level_index = i
                        game_state = "preview"
                        preview_origin = "levels"
                        move_hold = {"up": False, "down": False, "left": False, "right": False}
                        last_move_tick = pygame.time.get_ticks()
                if pygame.Rect(20, 20, 100, 40).collidepoint(mx, my):
                    game_state = "menu"
                    
            elif game_state == "preview":
                if pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50).collidepoint(mx, my):
                    game_state = "game"
                    show_deadlocks = False
                    show_statistics = False
                    show_full_map = False
                    move_hold = {"up": False, "down": False, "left": False, "right": False}
                    last_move_tick = pygame.time.get_ticks()
                elif pygame.Rect(20, 20, 100, 40).collidepoint(mx, my):
                    if preview_origin == "levels":
                        game_state = "levels"
                    else:
                        game_state = "menu"
                    preview_origin = None
                    
            elif game_state == "game":
                if pygame.Rect(10, 60, 80, 35).collidepoint(mx, my):
                    game_logic.undo()
                elif pygame.Rect(100, 60, 80, 35).collidepoint(mx, my):
                    game_logic.redo()
                elif pygame.Rect(10, 105, 80, 35).collidepoint(mx, my):
                    game_logic.reset_level(levels_list[current_level_index])
                    show_deadlocks = False
                    show_statistics = False
                    # clear held movement after a reset
                    move_hold = {"up": False, "down": False, "left": False, "right": False}
                    last_move_tick = pygame.time.get_ticks()
                elif pygame.Rect(100, 105, 80, 35).collidepoint(mx, my):
                    game_state = "menu"
                    show_deadlocks = False
                    show_statistics = False
                    show_full_map = False
                    
            elif game_state == "win":
                if pygame.Rect(250, 350, 300, 60).collidepoint(mx, my):
                    if current_level_index < len(levels_list) - 1:
                        current_level_index += 1
                        game_logic.reset_level(levels_list[current_level_index])
                        game_state = "preview"
                        preview_origin = "levels"
                        move_hold = {"up": False, "down": False, "left": False, "right": False}
                        last_move_tick = pygame.time.get_ticks()
                    else:
                        game_state = "menu"
                elif pygame.Rect(250, 430, 300, 60).collidepoint(mx, my):
                    game_state = "menu"
                    
            elif game_state == "leaderboard":
                if pygame.Rect(20, 20, 100, 40).collidepoint(mx, my):
                    game_state = "menu"

        if game_state == "game" and event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]:
                move_hold["up"] = True
                if not show_full_map:
                    game_logic.move_player(0, -1, "up")
                    last_move_tick = pygame.time.get_ticks()
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                move_hold["down"] = True
                if not show_full_map:
                    game_logic.move_player(0, 1, "down")
                    last_move_tick = pygame.time.get_ticks()
            elif event.key in [pygame.K_a, pygame.K_LEFT]:
                move_hold["left"] = True
                if not show_full_map:
                    game_logic.move_player(-1, 0, "left")
                    last_move_tick = pygame.time.get_ticks()
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                move_hold["right"] = True
                if not show_full_map:
                    game_logic.move_player(1, 0, "right")
                    last_move_tick = pygame.time.get_ticks()

            if event.key == pygame.K_r:
                game_logic.reset_level(levels_list[current_level_index])
                show_deadlocks = False
                show_statistics = False
            elif event.key == pygame.K_ESCAPE:
                game_state = "menu"
                show_deadlocks = False
                show_statistics = False
                show_full_map = False
            elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                game_logic.undo()
            elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
                game_logic.redo()

            elif event.key == pygame.K_i: 
                show_statistics = not show_statistics

            elif event.key == pygame.K_m:
                show_full_map = not show_full_map
                if show_full_map:
                    game_logic.current_direction = "down"
                    if getattr(game_logic, 'player_obj', None):
                        try:
                            game_logic.player_obj.direction = "down"
                        except Exception:
                            pass

            elif event.key == pygame.K_F5: 
                game_logic.save_state_to_binary("quicksave.bin")
                save_message = "Гру збережено (F5)"
                save_message_timer = 180 

            elif event.key == pygame.K_F9: 
                if game_logic.load_state_from_binary("quicksave.bin"):
                    save_message = "Гру завантажено (F9)"
                    save_message_timer = 180
                else:
                    save_message = "Немає збереження"
                    save_message_timer = 180
          
            if game_logic.check_win():
                if current_user_id:
                    save_score(current_user_id, current_level_index + 1, game_logic.steps_count)
                game_state = "win"
                show_deadlocks = False
                show_statistics = False
                show_full_map = False
                
        if event.type == pygame.KEYUP and game_state == "game":
            if event.key in [pygame.K_w, pygame.K_UP]:
                move_hold["up"] = False
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                move_hold["down"] = False
            elif event.key in [pygame.K_a, pygame.K_LEFT]:
                move_hold["left"] = False
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                move_hold["right"] = False
    if game_state == "menu":
        renderer.draw_menu(current_username)
    elif game_state == "levels":
        renderer.draw_levels_menu(len(levels_list))
    elif game_state == "preview":
        renderer.draw_preview(game_logic, current_level_index)
    elif game_state == "game":
        if show_full_map:
            renderer.draw_full_map(game_logic, current_level_index)
        else:
            global_stats = get_global_statistics() if show_statistics else None
            renderer.draw_game(
                game_logic, 
                current_level_index, 
                deadlocks=current_deadlocks if show_deadlocks else None,
                show_stats=show_statistics,
                global_stats=global_stats
            )
            
            if save_message:
                msg_surf = renderer.font_small.render(save_message, True, (100, 255, 100))
                screen.blit(msg_surf, (SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, 100))

        if game_state == "game" and not show_full_map:
            now = pygame.time.get_ticks()
            if now - last_move_tick >= MOVE_REPEAT_MS:
                if move_hold.get("up"):
                    game_logic.move_player(0, -1, "up")
                    last_move_tick = now
                elif move_hold.get("down"):
                    game_logic.move_player(0, 1, "down")
                    last_move_tick = now
                elif move_hold.get("left"):
                    game_logic.move_player(-1, 0, "left")
                    last_move_tick = now
                elif move_hold.get("right"):
                    game_logic.move_player(1, 0, "right")
                    last_move_tick = now
    
    elif game_state == "leaderboard":
        renderer.draw_leaderboard(len(levels_list))
    elif game_state == "win":
        renderer.draw_win_screen(current_level_index, len(levels_list), game_logic.steps_count, current_user_id is not None)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()