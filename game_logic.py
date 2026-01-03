import os
import pickle
from game_entities import (
    AdvancedPlayer, AdvancedBox, Goal, Wall, 
    GameObjectCollection,
)

total_games_played = 0
total_steps_made = 0

def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"[LOG] Виклик: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

class GameLogic:
    # Клас для керування ігровою логікою
    
    def __init__(self):
        self.level = []
        self.goals = set() 
        self.player_x = 0
        self.player_y = 0
        self.history = []
        self.history_index = -1
        self.steps_count = 0
        self.current_direction = "down"
        self.visited_positions = set() 
        
        self.player_obj = None 
        self.boxes = GameObjectCollection() 
        self.goals_obj = GameObjectCollection()  
        self.walls = GameObjectCollection()  
    
    def load_level_data(self, filename):
        # Завантаження рівня з файлу
        path = f"levels/{filename}"
        if not os.path.exists(path):
            return [["#"]*15 for _ in range(15)]
        with open(path, "r", encoding="utf-8") as f:
            return [list(line.rstrip("\n")) for line in f]
    
    def save_state(self):
        # Збереження поточного стану в історію
        state = {
            "level": [row[:] for row in self.level],
            "player_pos": (self.player_x, self.player_y),
            "direction": self.current_direction,
            "steps": self.steps_count
        }
        self.history = self.history[:self.history_index + 1]
        self.history.append(state)
        self.history_index += 1
    
    def undo(self):
        # Відкат на крок назад
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            self.level = [row[:] for row in state["level"]]
            self.player_x, self.player_y = state["player_pos"]
            self.current_direction = state["direction"]
            self.steps_count = state["steps"]
            
            if self.player_obj:
                self.player_obj.x = self.player_x
                self.player_obj.y = self.player_y
                self.player_obj.direction = self.current_direction
    
    def redo(self):
        # Відкат уперед
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            state = self.history[self.history_index]
            self.level = [row[:] for row in state["level"]]
            self.player_x, self.player_y = state["player_pos"]
            self.current_direction = state["direction"]
            self.steps_count = state["steps"]
            
            if self.player_obj:
                self.player_obj.x = self.player_x
                self.player_obj.y = self.player_y
                self.player_obj.direction = self.current_direction
    
    def reset_level(self, level_filename):
        # Скидання рівня
        global total_games_played 
        total_games_played += 1
        
        self.level = self.load_level_data(level_filename)
        self.goals = {(x, y) for y, row in enumerate(self.level) for x, ch in enumerate(row) if ch in [".", "*"]}
        self.visited_positions = set() 
        self.current_direction = "down"
        self.history = []
        self.history_index = -1
        self.steps_count = 0
        
        self.boxes = GameObjectCollection()
        self.goals_obj = GameObjectCollection()
        self.walls = GameObjectCollection()
        
        for y, row in enumerate(self.level):
            for x, ch in enumerate(row):
                if ch == "@":
                    self.player_x, self.player_y = x, y
                    self.player_obj = AdvancedPlayer(x, y, "Герой")
                    self.visited_positions.add((x, y))
                elif ch == "$":
                    box = AdvancedBox(x, y, weight=1)
                    self.boxes.add(box)
                elif ch in [".", "*"]:
                    goal = Goal(x, y)
                    self.goals_obj.add(goal)
                elif ch == "#":
                    wall = Wall(x, y)
                    self.walls.add(wall)
        
        self.save_state()

    @log_call
    def move_player(self, dx: int, dy: int, direction: str) -> None:
        # Переміщення гравця (Основне завдання)
        global total_steps_made
        self.current_direction = direction
        
        nx, ny = self.player_x + dx, self.player_y + dy
        nnx, nny = self.player_x + 2 * dx, self.player_y + 2 * dy

        if 0 <= ny < len(self.level) and 0 <= nx < len(self.level[ny]):
            pass
        else:
            return
   
        target = self.level[ny][nx]
        if target == "#": 
            return
        
        moved = False
        if target == "$":
            if 0 <= nny < len(self.level) and 0 <= nnx < len(self.level[nny]):
                after_box = self.level[nny][nnx]
                if after_box in [" ", "."]:
                    self.level[nny][nnx] = "$"
                    self.level[ny][nx] = "@"
                    self.level[self.player_y][self.player_x] = "." if (self.player_x, self.player_y) in self.goals else " "
                    self.player_x, self.player_y = nx, ny
                    moved = True
                    
                    box = self.boxes.get_by_position(nx, ny)
                    if box: box.push(dx, dy)
        
        elif target in [" ", "."]:
            self.level[ny][nx] = "@"
            self.level[self.player_y][self.player_x] = "." if (self.player_x, self.player_y) in self.goals else " "
            self.player_x, self.player_y = nx, ny
            moved = True
        
        if moved:
            self.steps_count += 1
            total_steps_made += 1
            self.visited_positions.add((self.player_x, self.player_y))
            if self.player_obj:
                self.player_obj += 10
            self.save_state()
    
    def check_win(self) -> bool:
        # Перевірка перемоги
        boxes_positions = {(x, y) for y, row in enumerate(self.level) for x, tile in enumerate(row) if tile == "$"}
        return boxes_positions == self.goals
    
    def save_progress_to_text(self, filename="progress.txt"):
        # Збереження прогресу в текстовий файл
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Кроків: {self.steps_count}\n")
            f.write(f"Напрямок: {self.current_direction}\n")
            f.write(f"Позиція гравця: {self.player_x},{self.player_y}\n")
            f.write(f"Відвідано клітин: {len(self.visited_positions)}\n")
            f.write(f"Цілей: {len(self.goals)}\n")
            
            if self.player_obj:
                f.write(f"Дані гравця: {self.player_obj.to_dict()}\n")
            
            f.write("Рівень:\n")
            for row in self.level:
                f.write("".join(row) + "\n")
    
    def save_state_to_binary(self, filename="gamestate.bin"):
        # Збереження повного стану гри в бінарний файл
        state = {
            "level": self.level,
            "goals": self.goals,
            "player_x": self.player_x,
            "player_y": self.player_y,
            "steps_count": self.steps_count,
            "current_direction": self.current_direction,
            "history": self.history,
            "history_index": self.history_index,
            "visited_positions": self.visited_positions,
            "player_data": self.player_obj.to_dict() if self.player_obj else None
        }
        with open(filename, "wb") as f:
            pickle.dump(state, f)
    
    def load_state_from_binary(self, filename="gamestate.bin"):
        # Завантаження стану гри з бінарного файлу
        if not os.path.exists(filename):
            return False
        try:
            with open(filename, "rb") as f:
                state = pickle.load(f)
            self.level = state["level"]
            self.goals = state["goals"]
            self.player_x = state["player_x"]
            self.player_y = state["player_y"]
            self.steps_count = state["steps_count"]
            self.current_direction = state["current_direction"]
            self.history = state["history"]
            self.history_index = state["history_index"]
            self.visited_positions = state["visited_positions"]
            
            if state.get("player_data"):
                player_data = state["player_data"]
                self.player_obj = AdvancedPlayer(
                    player_data['x'], 
                    player_data['y'],
                    player_data.get('name', 'Герой')
                )
                self.player_obj._score = player_data.get('score', 0)
                self.player_obj._moves_count = player_data.get('moves', 0)
                self.player_obj._direction = player_data.get('direction', 'down')
            
            return True
        except:
            return False

def get_global_statistics():
    # Отримання глобальної статистики
    global total_games_played, total_steps_made
    return {
        "games_played": total_games_played,
        "total_steps": total_steps_made,
        "avg_steps": total_steps_made / total_games_played if total_games_played > 0 else 0
    }

def reset_global_statistics():
    # Скидання глобальної статистики
    global total_games_played, total_steps_made
    total_games_played = 0
    total_steps_made = 0