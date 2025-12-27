"""
Модуль с игровыми сущностями
Демонстрирует: классы, наследование, системные методы, свойства, множественное наследование
"""

class GameObject:
    """Базовый класс для всех объектов на игровом поле"""
    
    def __init__(self, x, y, symbol):
        self._x = x 
        self._y = y
        self._symbol = symbol
    
    @property
    def x(self):
        """Координата X"""
        return self._x
    
    @x.setter
    def x(self, value):
        if value < 0:
            raise ValueError("Координата не может быть отрицательной")
        self._x = value
    
    @property
    def y(self):
        """Координата Y"""
        return self._y
    
    @y.setter
    def y(self, value):
        if value < 0:
            raise ValueError("Координата не может быть отрицательной")
        self._y = value
    
    @property
    def symbol(self):
        """Символ объекта на карте"""
        return self._symbol
    
    @property
    def position(self):
        """Позиция как кортеж"""
        return (self._x, self._y)
    
    def __str__(self):
        """Строковое представление объекта"""
        return f"{self.__class__.__name__}({self._x}, {self._y})"
    
    def __repr__(self):
        """Представление для отладки"""
        return f"{self.__class__.__name__}(x={self._x}, y={self._y}, symbol='{self._symbol}')"
    
    def __eq__(self, other):
        """Сравнение двух объектов"""
        if not isinstance(other, GameObject):
            return False
        return self._x == other._x and self._y == other._y
    
    def __hash__(self):
        """Хеш для использования в множествах и словарях"""
        return hash((self._x, self._y, self._symbol))
    
    def can_move_to(self, level, new_x, new_y):
        """Может ли объект переместиться на новую позицию"""
        return True


class Player(GameObject):
    """Класс игрока"""
    
    def __init__(self, x, y):
        super().__init__(x, y, "@")
        self._direction = "down"
        self._moves_count = 0
    
    @property
    def direction(self):
        """Направление взгляда игрока"""
        return self._direction
    
    @direction.setter
    def direction(self, value):
        if value not in ["up", "down", "left", "right"]:
            raise ValueError("Неверное направление")
        self._direction = value
    
    @property
    def moves_count(self):
        """Количество ходов"""
        return self._moves_count
    
    def move(self, dx, dy, direction):
        """Перемещение игрока"""
        self._x += dx
        self._y += dy
        self._direction = direction
        self._moves_count += 1
    
    def reset_moves(self):
        """Сброс счётчика ходов"""
        self._moves_count = 0
    
    def __str__(self):
        return f"Player at ({self._x}, {self._y}), facing {self._direction}, moves: {self._moves_count}"


class Box(GameObject):
    """Класс ящика"""
    
    def __init__(self, x, y):
        super().__init__(x, y, "$")
        self._on_goal = False
    
    @property
    def on_goal(self):
        """Стоит ли ящик на цели"""
        return self._on_goal
    
    @on_goal.setter
    def on_goal(self, value):
        self._on_goal = bool(value)
    
    def push(self, dx, dy):
        """Толкнуть ящик"""
        self._x += dx
        self._y += dy
    
    def __str__(self):
        status = "on goal" if self._on_goal else "not on goal"
        return f"Box at ({self._x}, {self._y}), {status}"


class Goal(GameObject):
    """Класс цели"""
    
    def __init__(self, x, y):
        super().__init__(x, y, ".")
        self._occupied = False
    
    @property
    def occupied(self):
        """Занята ли цель ящиком"""
        return self._occupied
    
    @occupied.setter
    def occupied(self, value):
        self._occupied = bool(value)
    
    def __str__(self):
        status = "occupied" if self._occupied else "empty"
        return f"Goal at ({self._x}, {self._y}), {status}"


class Wall(GameObject):
    """Класс стены"""
    
    def __init__(self, x, y):
        super().__init__(x, y, "#")
    
    def can_move_to(self, level, new_x, new_y):
        """Через стену нельзя пройти"""
        return False


class SerializableMixin:
    """Миксин для сериализации объекта"""
    
    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'class': self.__class__.__name__,
            'x': self._x if hasattr(self, '_x') else 0,
            'y': self._y if hasattr(self, '_y') else 0
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание объекта из словаря"""
        return cls(data['x'], data['y'])


class ComparableMixin:
    """Миксин для сравнения объектов по позиции"""
    
    def __lt__(self, other):
        """Меньше - для сортировки"""
        if not isinstance(other, GameObject):
            return NotImplemented
        return (self._y, self._x) < (other._y, other._x)
    
    def __le__(self, other):
        """Меньше или равно"""
        return self == other or self < other
    
    def __gt__(self, other):
        """Больше"""
        if not isinstance(other, GameObject):
            return NotImplemented
        return (self._y, self._x) > (other._y, other._x)
    
    def __ge__(self, other):
        """Больше или равно"""
        return self == other or self > other


class AdvancedPlayer(Player, SerializableMixin, ComparableMixin):
    """
    Продвинутый игрок с множественным наследованием
    Наследует: Player (основной функционал), SerializableMixin (сериализация), 
    ComparableMixin (сравнение)
    """
    
    def __init__(self, x, y, name="Player"):
        super().__init__(x, y)
        self._name = name
        self._score = 0
    
    @property
    def name(self):
        """Имя игрока"""
        return self._name
    
    @property
    def score(self):
        """Очки игрока"""
        return self._score
    
    def add_score(self, points):
        """Добавить очки"""
        self._score += points
    
    def __str__(self):
        return f"{self._name} at ({self._x}, {self._y}), score: {self._score}, moves: {self._moves_count}"
    
    def __add__(self, points):
        """Оператор + для добавления очков"""
        self._score += points
        return self
    
    def __iadd__(self, points):
        """Оператор += для добавления очков"""
        self._score += points
        return self
    
    def to_dict(self):
        """Расширенная сериализация"""
        data = super().to_dict()
        data.update({
            'name': self._name,
            'score': self._score,
            'moves': self._moves_count,
            'direction': self._direction
        })
        return data


class AdvancedBox(Box, SerializableMixin, ComparableMixin):
    """Продвинутый ящик с множественным наследованием"""
    
    def __init__(self, x, y, weight=1):
        super().__init__(x, y)
        self._weight = weight  
    
    @property
    def weight(self):
        """Вес ящика"""
        return self._weight
    
    def __int__(self):
        """Преобразование в int - возвращает вес"""
        return self._weight
    
    def __float__(self):
        """Преобразование в float"""
        return float(self._weight)
    
    def to_dict(self):
        """Расширенная сериализация"""
        data = super().to_dict()
        data['weight'] = self._weight
        data['on_goal'] = self._on_goal
        return data


class GameObjectCollection:
    """Коллекция игровых объектов"""
    
    def __init__(self):
        self._objects = []
    
    def add(self, obj):
        """Добавить объект"""
        if not isinstance(obj, GameObject):
            raise TypeError("Можно добавлять только GameObject")
        self._objects.append(obj)
    
    def remove(self, obj):
        """Удалить объект"""
        self._objects.remove(obj)
    
    def __len__(self):
        """Количество объектов"""
        return len(self._objects)
    
    def __iter__(self):
        """Итератор по объектам"""
        return iter(self._objects)
    
    def __getitem__(self, index):
        """Доступ по индексу"""
        return self._objects[index]
    
    def __setitem__(self, index, value):
        """Установка по индексу"""
        if not isinstance(value, GameObject):
            raise TypeError("Можно добавлять только GameObject")
        self._objects[index] = value
    
    def __contains__(self, obj):
        """Проверка наличия объекта (оператор in)"""
        return obj in self._objects
    
    def __str__(self):
        return f"GameObjectCollection({len(self._objects)} objects)"
    
    def __repr__(self):
        return f"GameObjectCollection({self._objects})"
    
    def get_by_position(self, x, y):
        """Получить объект по позиции"""
        for obj in self._objects:
            if obj.x == x and obj.y == y:
                return obj
        return None
    
    def sort_by_position(self):
        """Сортировка объектов по позиции (требует ComparableMixin)"""
        comparable = [obj for obj in self._objects if isinstance(obj, ComparableMixin)]
        comparable.sort()
        return comparable