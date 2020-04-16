# импортируем все нужное для создания абстрактного класса
from abc import ABC, abstractmethod, abstractproperty


# простой класс "анимации": хранится массив ключевых точек с временными метками 
class Animation:
    def __init__(self):
        self._data = [(0, 0, 0)]

    def __repr__(self):
        return f'Animation(last keyframe: ({self.x}, {self.y}) at {self.t})'

    # добавление ключевых точек осуществляется через единственный метод
    # и по абсолютным значениям, что не всегда удобно
    def add_point(self, x, y, t):
        self._data.append((x, y, t))

    # для примера функциональности класса есть возможность определить координаты,
    # которые соответствуют определенному моменту времени
    def get_location(self, t):
        if t >= self.t:
            return (self.x, self.y)
        else:
            for left_keyframe, right_keyframe in zip(self._data[:-1], self._data[1:]):
                if right_keyframe[2] > t:
                    k = (t - left_keyframe[2]) / (right_keyframe[2] - left_keyframe[2])
                    return (k * right_keyframe[0] + (1 - k) * left_keyframe[0], k * right_keyframe[1] + (1 - k) * left_keyframe[1])

    # свойства, возвращающие информацию о последней добавленной точке
    @property
    def x(self):
        return self._data[-1][0]

    @property
    def y(self):
        return self._data[-1][1]

    @property
    def t(self):
        return self._data[-1][2]


# абстрактный базовый класс нужного нам строителя
class AnimationBuilder(ABC):
    def __init__(self):
        self.reset()
    
    @property
    def product(self):
        result = self._product
        self.reset()
        return result

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def move_to(self, x, y, t):
        pass


# реализация строителя с перемещением от точки к точке по прямой линии,
# но с заданием отсечек времени вместо временных меток при добавлении ключевой точки
class StraightAnimationBuilder(AnimationBuilder):
    def reset(self):
        self._product = Animation()

    def move_to(self, x, y, t):
        self._product.add_point(x, y, self._product.t + t)


# реализация строителя с перемещением, характерным для ладьи:
# сначала строго по вертикали, затем строго по горизонтали
class RookAnimationBuilder(AnimationBuilder):
    def reset(self):
        self._product = Animation()

    def move_to(self, x, y, t):
        dx, dy = x - self._product.x, y - self._product.y
        s = abs(dx) + abs(dy)
        if s == 0:
            self._product.add_point(x, y, self._product.t + ty)
        else:
            tx, ty = abs(dx) / s * t, abs(dy) / s * t
            self._product.add_point(self._product.x, y, self._product.t + ty)
            self._product.add_point(x, y, self._product.t + tx)



# реализация строителя, собирающего информацию о перемещениях в список ключевых точек,
# наподобие того, что хранится внутри объектов Animation.
# Как видим, строители, происходящие от одного и того же базового класса,
# вовсе не обязанны строить объекты близкородственных друг другу классов
class ListAnimationBuilder(AnimationBuilder):
    def reset(self):
        self._product = [(0, 0, 0)]

    def move_to(self, x, y, t):
        self._product.append((x, y, t + self._product[-1][2]))


# реализация строителя, ведущего запись информации о перемещениях в текстовом виде
class AnimationLogBuilder(AnimationBuilder):
    def reset(self):
        self._product = ''

    def move_to(self, x, y, t):
        self._product += f'moving to ({x}, {y}) in {t} seconds\n'


# реализация строителя, ведущего запись информации о перемещениях в текстовом виде,
# с печатью в стандартный поток вывода
class AnimationVerboseLogBuilder(AnimationLogBuilder):
    def move_to(self, x, y, t):
        super().move_to(x, y, t)
        print(f'moving to ({x}, {y}) in {t} seconds')


# класс директора, позволяющий создавать сложные последовательности движений
# для их реализации определенным строителем
class AnimationDirector:
    def __init__(self):
        self._builder = None

    @property
    def builder(self):
        return self._builder

    @builder.setter
    def builder(self, builder):
        self._builder = builder

    # пример работы директора: движение до точки и обратно несколько раз
    def build_periodic(self, t, x, y, c):
        for _ in range(c):
            self._builder.move_to(x, y, t)
            self._builder.move_to(0, 0, t)

    # пример работы директора: движение от точки к точке и возвращение в обратно
    def build_cycle(self, t, *points):
        for point in points:
            self._builder.move_to(point[0], point[1], t)
        self._builder.move_to(0, 0, t)


# небольшая демонстрация работы
if __name__ == '__main__':
    director = AnimationDirector()
    straight_builder = StraightAnimationBuilder()
    rook_builder = RookAnimationBuilder()
    lister = ListAnimationBuilder()
    logger = AnimationLogBuilder()
    printer = AnimationVerboseLogBuilder()
    results = []
    print('\nСейчас мы применим одни и те же методы директора с разными строителями:\n')
    for builder in (straight_builder, rook_builder, lister, logger, printer):
        director.builder = builder
        director.build_periodic(100, 10, -8, 3)
        director.build_cycle(10, (-5, 3), (0, 7), (2, -2))
        results.append(director.builder.product)
    print('\nИ вот результаты работы строителей:\n')
    for result in results:
        print(result)
