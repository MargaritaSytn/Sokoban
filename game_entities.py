class GameObject:
    # Базовий клас для всіх об'єктів на ігровому полі
    
    def __init__(self, x, y, symbol):
        self._x = x 
        self._y = y
        self._symbol = symbol
    
    @property
    def x(self):
    # Координата X
        return self._x
    
    @x.setter
    def x(self, value):
        if value < 0:
            raise ValueError("Координата не може бути від'ємною")
        self._x = value
    
    @property
    def y(self):
    # Координата Y
        return self._y
    
    @y.setter
    def y(self, value):
        if value < 0:
            raise ValueError("Координата не може бути від'ємною")
        self._y = value
    
    @property
    def symbol(self):
    # Символ об'єкта на карті
        return self._symbol
    
    @property
    def position(self):
    # Позиція як кортеж
        return (self._x, self._y)
    
    def __str__(self):
    # Рядкове представлення об'єкта
        return f"{self.__class__.__name__}({self._x}, {self._y})"
    
    def __repr__(self):
    # Представлення для налагодження
        return f"{self.__class__.__name__}(x={self._x}, y={self._y}, symbol='{self._symbol}')"
    
    def __eq__(self, other):
    # Порівняння двох об'єктів
        if not isinstance(other, GameObject):
            return False
        return self._x == other._x and self._y == other._y
    
    def __hash__(self):
    # Хеш для використання у множинах та словниках
        return hash((self._x, self._y, self._symbol))
    
    def can_move_to(self, level, new_x, new_y):
    # Чи може об'єкт переміститися на нову позицію
        return True
    
    def iter_objects(self):
    # Генератор об'єктів колекції
        for obj in self._objects:
            yield obj


class Player(GameObject):
    # Клас гравця
    
    def __init__(self, x, y):
        super().__init__(x, y, "@")
        self._direction = "down"
        self._moves_count = 0
    
    @property
    def direction(self):
    # Напрямок погляду гравця"""
        return self._direction
    
    @direction.setter
    def direction(self, value):
        if value not in ["up", "down", "left", "right"]:
            raise ValueError("Невірний напрямок")
        self._direction = value
    
    @property
    def moves_count(self):
        # Кількість ходів
        return self._moves_count
    
    def move(self, dx, dy, direction):
        # Переміщення гравця
        self._x += dx
        self._y += dy
        self._direction = direction
        self._moves_count += 1
    
    def reset_moves(self):
        # Скидання лічильника ходів
        self._moves_count = 0
    
    def __str__(self):
        return f"Гравець у ({self._x}, {self._y}), дивиться {self._direction}, ходів: {self._moves_count}"


class Box(GameObject):
    # Клас ящика
    
    def __init__(self, x, y):
        super().__init__(x, y, "$")
        self._on_goal = False
    
    @property
    def on_goal(self):
        # Чи стоїть ящик на цілі
        return self._on_goal
    
    @on_goal.setter
    def on_goal(self, value):
        self._on_goal = bool(value)
    
    def push(self, dx, dy):
        # Штовхнути ящик
        self._x += dx
        self._y += dy
    
    def __str__(self):
        status = "на цілі" if self._on_goal else "не на цілі"
        return f"Ящик у ({self._x}, {self._y}), {status}"


class Goal(GameObject):
    # Клас цілі
    
    def __init__(self, x, y):
        super().__init__(x, y, ".")
        self._occupied = False
    
    @property
    def occupied(self):
        # Чи зайнята ціль ящиком
        return self._occupied
    
    @occupied.setter
    def occupied(self, value):
        self._occupied = bool(value)
    
    def __str__(self):
        status = "зайнята" if self._occupied else "порожня"
        return f"Ціль у ({self._x}, {self._y}), {status}"


class Wall(GameObject):
    # Клас стіни
    
    def __init__(self, x, y):
        super().__init__(x, y, "#")
    
    def can_move_to(self, level, new_x, new_y):
        # Через стіну не можна пройти
        return False


class SerializableMixin:
    # Міксин для серіалізації об'єкта
    
    def to_dict(self):
        # Перетворення у словник
        return {
            'class': self.__class__.__name__,
            'x': self._x if hasattr(self, '_x') else 0,
            'y': self._y if hasattr(self, '_y') else 0
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(data['x'], data['y'])


class ComparableMixin:
    
    def __lt__(self, other):
        if not isinstance(other, GameObject):
            return NotImplemented
        return (self._y, self._x) < (other._y, other._x)
    
    def __le__(self, other):
        return self == other or self < other
    
    def __gt__(self, other):
        if not isinstance(other, GameObject):
            return NotImplemented
        return (self._y, self._x) > (other._y, other._x)
    
    def __ge__(self, other):
        return self == other or self > other


class AdvancedPlayer(Player, SerializableMixin, ComparableMixin):
    
    def __init__(self, x, y, name="Гравець"):
        super().__init__(x, y)
        self._name = name
        self._score = 0
    
    @property
    def name(self):
        return self._name
    
    @property
    def score(self):
        return self._score
    
    def add_score(self, points):
        self._score += points
    
    def __str__(self):
        return f"{self._name} у ({self._x}, {self._y}), рахунок: {self._score}, ходів: {self._moves_count}"
    
    def __add__(self, points):
        self._score += points
        return self
    
    def __iadd__(self, points):
        self._score += points
        return self
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self._name,
            'score': self._score,
            'moves': self._moves_count,
            'direction': self._direction
        })
        return data


class AdvancedBox(Box, SerializableMixin, ComparableMixin):
    
    def __init__(self, x, y, weight=1):
        super().__init__(x, y)
        self._weight = weight  
    
    @property
    def weight(self):
        return self._weight
    
    def __int__(self):
        return self._weight
    
    def __float__(self):
        return float(self._weight)
    
    def to_dict(self):
        data = super().to_dict()
        data['weight'] = self._weight
        data['on_goal'] = self._on_goal
        return data


class GameObjectCollection:
    # Колекція ігрових об'єктів
    
    def __init__(self):
        self._objects = []
    
    def add(self, obj):
        # Додати об'єкт
        if not isinstance(obj, GameObject):
            raise TypeError("Можна додавати тільки GameObject")
        self._objects.append(obj)
    
    def remove(self, obj):
        # Видалити об'єкт
        self._objects.remove(obj)
    
    def __len__(self):
        # Кількість об'єктів
        return len(self._objects)
    
    def __iter__(self):
        # Ітератор за об'єктами
        return iter(self._objects)
    
    def __getitem__(self, index):
        # Доступ за індексом
        return self._objects[index]
    
    def __setitem__(self, index, value):
        # Встановлення за індексом
        if not isinstance(value, GameObject):
            raise TypeError("Можна додавати тільки GameObject")
        self._objects[index] = value
    
    def __contains__(self, obj):
        # Перевірка наявності об'єкта
        return obj in self._objects
    
    def __str__(self):
        return f"GameObjectCollection({len(self._objects)} об'єктів)"
    
    def __repr__(self):
        return f"GameObjectCollection({self._objects})"
    
    def get_by_position(self, x, y):
        # Отримати об'єкт за позицією
        for obj in self._objects:
            if obj.x == x and obj.y == y:
                return obj
        return None
    
    def sort_by_position(self):
        # Сортування об'єктів за позицією
        comparable = [obj for obj in self._objects if isinstance(obj, ComparableMixin)]
        comparable.sort()
        return comparable