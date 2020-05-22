from abc import ABC, abstractmethod


# базовый астрактный класс, представляющий некое выражение
class Expression(ABC):
    # в каждом выражении нас интересует возможность вычислить его значение
    @abstractmethod
    def evaluate(self) -> float:
        pass


# класс, представляющий константу
class Constant(Expression):
    # конструктор константы извлекает ее значение из строки и хранит его в виде числа с плавающей точкой
    def __init__(self, s):
        self._value = float(s)

    # вычисление значения выражения из одной константы заключается в простом извлечении такового из памяти
    def evaluate(self) -> float:
        return self._value

    def __repr__(self):
        return f'Constant({self._value})'


# класс, представляющий унарную операцию
class UnaryOperation(Expression):
    # конструктор унарной операции может принять её операнд, а может позволить пользователю дописать их позже
    # самостоятельно
    def __init__(self, right: Expression = None):
        self.right = right

    # вычисление значения унарной операции заключается в применении операции над предварительно высчитанными
    # значениями операндов
    def evaluate(self) -> float:
        return self._operate(self.right.evaluate())

    # унарную операцию характеризует функция от одного аргумента, представляющая ее действие
    @abstractmethod
    def _operate(self, y: float) -> float:
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}({self.right})'


# класс, представляющий унырный плюс
class UnaryPlus(UnaryOperation):
    def _operate(self, y: float) -> float:
        return y


# класс, представляющий унарный минус
class UnaryMinus(UnaryOperation):
    def _operate(self, y: float) -> float:
        return -y


# класс, представляющий бинарную операцию
class BinaryOperation(Expression):
    # конструктор бинарной операции может принять её операнды, а может позволить пользователю дописать их позже
    # самостоятельно
    def __init__(self, left: Expression = None, right: Expression = None):
        self.left = left
        self.right = right

    # вычисление значения бинарной операции заключается в применении операции над предварительно высчитанными
    # значениями операндов
    def evaluate(self) -> float:
        return self._operate(self.left.evaluate(), self.right.evaluate())

    # бинарную операцию характеризует функция от двух аргументов, представляющая ее действие
    @abstractmethod
    def _operate(self, x: float, y: float) -> float:
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}({self.left}, {self.right})'


# класс, представляющий сложение
class Addition(BinaryOperation):
    def _operate(self, x: float, y: float) -> float:
        return x + y


# класс, представляющий вычитание
class Subtraction(BinaryOperation):
    def _operate(self, x: float, y: float) -> float:
        return x - y


# класс, представляющий произведение
class Multiplication(BinaryOperation):
    def _operate(self, x: float, y: float) -> float:
        return x * y


# класс, представляющий деление
class Division(BinaryOperation):
    def _operate(self, x: float, y: float) -> float:
        return x / y


# класс, представляющий возведение в степень
class Exponentiation(BinaryOperation):
    def _operate(self, x: float, y: float) -> float:
        return x ** y


# класс, представляющий часть записи математического выражения, несущей в себе информацию о приоритете вычисления
class ExpressionPart:
    def __init__(self, priority: int, expression: Expression):
        self.priority = priority
        self.expression = expression


# класс исключения, возникающего при обработке некорректной строки записи
class ParseError(Exception):
    pass


# функция, извлекающая выражение из строки записи
def parse_expression(s: str) -> Expression:
    balance = 0
    digit_start = 0
    parenthesis_start = 0
    digit = False
    unary = False
    components = []
    for i, c in enumerate(s + ' '):
        if balance > 0:
            if c == '(':
                balance += 1
            elif c == ')':
                balance -= 1
                if balance == 0:
                    expression = parse_expression(s[parenthesis_start:i])
                    if unary:
                        unary = False
                        part = components[-1]
                        assert isinstance(part.expression, UnaryOperation)
                        part.expression.right = expression
                    else:
                        components.append(ExpressionPart(-1, expression))
        elif c.isdigit() or c == '.':
            if not digit:
                digit = True
                digit_start = i
        else:
            if digit:
                digit = False
                constant = Constant(s[digit_start:i])
                if unary:
                    unary = False
                    part = components[-1]
                    assert isinstance(part.expression, UnaryOperation)
                    part.expression.right = constant
                else:
                    components.append(ExpressionPart(-1, constant))
            if c == '(':
                parenthesis_start = i + 1
                balance += 1
            elif c == '+':
                if len(components) == 0:
                    unary = True
                    components.append(ExpressionPart(-1, UnaryPlus()))
                else:
                    components.append(ExpressionPart(2, Addition()))
            elif c == '-':
                if len(components) == 0:
                    unary = True
                    components.append(ExpressionPart(-1, UnaryMinus()))
                else:
                    components.append(ExpressionPart(2, Subtraction()))
            elif c == '*':
                components.append(ExpressionPart(1, Multiplication()))
            elif c == '/':
                components.append(ExpressionPart(1, Division()))
            elif c == '^':
                components.append(ExpressionPart(0, Exponentiation()))
    for priority in range(3):
        skip = False
        for i, part in enumerate(components):
            if skip:
                skip = False
            elif part.priority == priority:
                assert isinstance(part.expression, BinaryOperation)
                if i == 0 or i + 1 == len(components):
                    raise ParseError('expression is incorrect')
                elif components[i - 1].priority >= priority or components[i + 1].priority >= priority:
                    raise ParseError('expression is incorrect')
                part.expression.left = components[i - 1].expression
                part.expression.right = components[i + 1].expression
                components[i - 1] = None
                components[i + 1] = ExpressionPart(-1, part.expression)
                components[i] = None
                skip = True
        j = 0
        for part in components:
            if part is not None:
                components[j] = part
                j += 1
        del components[j:]
    return components[0].expression


def demo(example: str):
    s = input('Enter your expression: ')
    if not s:
        print(example)
        s = example
    expression = parse_expression(s)
    print(expression)
    print(expression.evaluate())


# демонстрация работы системы
if __name__ == '__main__':
    demo('((6.63 + (56.62 + 16.8)) + (-((60.53 + 3.61) + 14.91)))')
