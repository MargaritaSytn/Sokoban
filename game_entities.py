class GameObject:
    # Базовий клас для всіх об'єктів на ігровому полі
    # Конструктор, створює об’єкт із координатами x, y і символом symbol.
    def __init__(self, x, y, symbol):
        self._x = x 
        self._y = y
        self._symbol = symbol
    
    # Повертає координату X об’єкта.
    @property
    def x(self):
    # Координата X
        return self._x
    
    # Встановлює координату X. Не дозволяє від’ємні значення.
    @x.setter
    def x(self, value):
        if value < 0:
            raise ValueError("Координата не може бути від'ємною")
        self._x = value
    
    # Повертає координату Y об’єкта.
    @property
    def y(self):
    # Координата Y
        return self._y
    
    # Встановлює координату Y. Не дозволяє від’ємні значення.
    @y.setter
    def y(self, value):
        if value < 0:
            raise ValueError("Координата не може бути від'ємною")
        self._y = value
    
    # Повертає символ об’єкта.
    @property
    def symbol(self):
    # Символ об'єкта на карті
        return self._symbol
    
    # Повертає позицію об’єкта як кортеж (x, y).
    @property
    def position(self):
    # Позиція як кортеж
        return (self._x, self._y)
    
    # Порівнює два об’єкти по координатах. Повертає True, якщо x і y однакові.
    def __eq__(self, other):
    # Порівняння двох об'єктів
        if not isinstance(other, GameObject):
            return False
        return self._x == other._x and self._y == other._y

class Player(GameObject):
    # Клас гравця
    
    # Створює гравця з початковими координатами і напрямком down.
    def __init__(self, x, y):
        super().__init__(x, y, "@")
        self._direction = "down"
        self._moves_count = 0
    
    # Повертає напрямок гравця (up, down, left, right).
    @property
    def direction(self):
    # Напрямок погляду гравця"""
        return self._direction
    
    # Встановлює напрямок гравця. Перевіряє правильність значення.
    @direction.setter
    def direction(self, value):
        if value not in ["up", "down", "left", "right"]:
            raise ValueError("Невірний напрямок")
        self._direction = value
    
    # Повертає кількість зроблених ходів.
    @property
    def moves_count(self):
        # Кількість ходів
        return self._moves_count
    
    # Переміщує гравця на dx, dy і змінює напрямок, збільшує лічильник ходів.
    def move(self, dx, dy, direction):
        # Переміщення гравця
        self._x += dx
        self._y += dy
        self._direction = direction
        self._moves_count += 1



class Box(GameObject):
    # Клас ящика
    
    # Створює ящик з координатами та символом $.
    def __init__(self, x, y):
        super().__init__(x, y, "$")
        self._on_goal = False
    
    # Повертає True, якщо ящик стоїть на цілі.
    @property
    def on_goal(self):
        # Чи стоїть ящик на цілі
        return self._on_goal
    
    # Встановлює стан on_goal.
    @on_goal.setter
    def on_goal(self, value):
        self._on_goal = bool(value)
    
    # Переміщує ящик на dx, dy (штовхання).
    def push(self, dx, dy):
        # Штовхнути ящик
        self._x += dx
        self._y += dy


class Goal(GameObject):
    # Клас цілі
    
    # Створює ціль з координатами і символом ..
    def __init__(self, x, y):
        super().__init__(x, y, ".")
        self._occupied = False
    
    # Повертає True, якщо ціль зайнята ящиком.
    @property
    def occupied(self):
        # Чи зайнята ціль ящиком
        return self._occupied
    
    # Встановлює стан зайнятості цілі.
    @occupied.setter
    def occupied(self, value):
        self._occupied = bool(value)


class Wall(GameObject):
    # Клас стіни
    
    # Створює стіну з координатами і символом #.
    def __init__(self, x, y):
        super().__init__(x, y, "#")

class SerializableMixin:
    # Міксин для серіалізації об'єкта
    
    # Перетворює об’єкт у словник для збереження.
    def to_dict(self):
        # Перетворення у словник
        return {
            'class': self.__class__.__name__,
            'x': self._x if hasattr(self, '_x') else 0,
            'y': self._y if hasattr(self, '_y') else 0
        }
    # Створює об’єкт з даних словника.
    @classmethod
    def from_dict(cls, data):
        return cls(data['x'], data['y'])

class AdvancedPlayer(Player, SerializableMixin):
    
    # Створює гравця з ім’ям і рахунком.
    def __init__(self, x, y, name="Гравець"):
        super().__init__(x, y)
        self._name = name
        self._score = 0
    
    # Повертає ім’я гравця.
    @property
    def name(self):
        return self._name
    
    # Повертає рахунок гравця.
    @property
    def score(self):
        return self._score
    
    # Додає points до рахунку.
    def add_score(self, points):
        self._score += points
    
    # Перевантаження + для додавання до рахунку.
    def __add__(self, points):
        self._score += points
        return self
    
    # Перевантаження += для рахунку.
    def __iadd__(self, points):
        self._score += points
        return self
    
    # Перетворює гравця на словник з координатами, ім’ям, рахунком, ходами, напрямком.
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self._name,
            'score': self._score,
            'moves': self._moves_count,
            'direction': self._direction
        })
        return data


class AdvancedBox(Box, SerializableMixin):
    
    # Створює ящик з вагою weight.
    def __init__(self, x, y, weight=1):
        super().__init__(x, y)
        self._weight = weight  
    
    # Повертає вагу ящика.
    @property
    def weight(self):
        return self._weight
    
    # Перетворює ящик у ціле число (вагу).
    def __int__(self):
        return self._weight
    
    # Перетворює ящик у число з плаваючою крапкою (вагу).
    def __float__(self):
        return float(self._weight)
    
    # Перетворює ящик на словник із координатами, вагою та станом on_goal.
    def to_dict(self):
        data = super().to_dict()
        data['weight'] = self._weight
        data['on_goal'] = self._on_goal
        return data


class GameObjectCollection:
    # Колекція ігрових об'єктів
    
    # Створює порожню колекцію об’єктів.
    def __init__(self):
        self._objects = []
    
    # Додає об’єкт у колекцію.
    def add(self, obj):
        # Додати об'єкт
        if not isinstance(obj, GameObject):
            raise TypeError("Можна додавати тільки GameObject")
        self._objects.append(obj)
    
    # Видаляє об’єкт з колекції.
    def remove(self, obj):
        # Видалити об'єкт
        self._objects.remove(obj)
    
    # Повертає кількість об’єктів у колекції.
    def __len__(self):
        # Кількість об'єктів
        return len(self._objects)
    
    # Повертає ітератор для перебору об’єктів.
    def __iter__(self):
        # Ітератор за об'єктами
        return iter(self._objects)
    
    # Доступ до об’єкта за індексом.
    def __getitem__(self, index):
        # Доступ за індексом
        return self._objects[index]
    
    # Встановлює об’єкт на певний індекс.
    def __setitem__(self, index, value):
        # Встановлення за індексом
        if not isinstance(value, GameObject):
            raise TypeError("Можна додавати тільки GameObject")
        self._objects[index] = value
    
    # Перевіряє, чи є об’єкт у колекції.
    def __contains__(self, obj):
        # Перевірка наявності об'єкта
        return obj in self._objects
    
    # Повертає текстове представлення колекції.
    def __repr__(self):
        return f"GameObjectCollection({self._objects})"
    
    # Повертає об’єкт за координатами (x, y).
    def get_by_position(self, x, y):
        # Отримати об'єкт за позицією
        for obj in self._objects:
            if obj.x == x and obj.y == y:
                return obj
        return None
    
    # Повертає список об’єктів, відсортованих по позиції (тільки ті, що мають ComparableMixin).
    def sort_by_position(self):
        # Сортування об'єктів за позицією
        comparable = [obj for obj in self._objects if isinstance(obj)]
        comparable.sort()
        return comparable