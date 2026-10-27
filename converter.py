class Converter:
    @staticmethod
    def do(x: float) -> int:
        """Преобразовать число с одним знаком после запятой по заданным диапазонам."""
        if x >= 100.7:
            return 1000
        elif 0 < x < 100.7:
            return int(x)
        elif x == 0.0:
            raise ValueError("x не должен быть равен нулю.")
        elif -30.4 <= x < 0:
            return int(x) - 5
        else:
            return -2000
