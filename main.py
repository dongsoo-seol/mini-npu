import math


class Matrix:
    """N×N 숫자 배열을 저장하고 조회한다."""

    def __init__(self, size):
        if type(size) is not int:
            raise TypeError("배열 크기는 정수여야 합니다.")

        if size <= 0:
            raise ValueError("배열 크기는 0보다 커야 합니다.")

        self.size = size
        self.data = [
            [0 for _ in range(size)]
            for _ in range(size)
        ]

    def _check_position(self, row, col):
        if type(row) is not int or type(col) is not int:
            raise TypeError("행과 열 번호는 정수여야 합니다.")

        if not (0 <= row < self.size and 0 <= col < self.size):
            raise IndexError(
                f"행과 열 번호는 0부터 {self.size - 1} 사이여야 합니다."
            )

    def get_value(self, row, col):
        self._check_position(row, col)
        return self.data[row][col]

    def set_value(self, row, col, value):
        self._check_position(row, col)

        if type(value) not in (int, float):
            raise TypeError("배열의 값은 정수 또는 실수여야 합니다.")

        if type(value) is float and not math.isfinite(value):
            raise ValueError("NaN이나 무한대는 사용할 수 없습니다.")

        self.data[row][col] = value
def mac_score(pattern, filter_data):
    """같은 위치의 값을 곱하고 누적하여 점수를 반환한다."""
    if not isinstance(pattern, Matrix):
        raise TypeError("입력 패턴은 Matrix 객체여야 합니다.")

    if not isinstance(filter_data, Matrix):
        raise TypeError("필터는 Matrix 객체여야 합니다.")

    if pattern.size != filter_data.size:
        raise ValueError("패턴과 필터의 크기가 일치해야 합니다.")

    total = 0

    for row in range(pattern.size):
        for col in range(pattern.size):
            input_value = pattern.get_value(row, col)
            filter_value = filter_data.get_value(row, col)
            total += input_value * filter_value

    if type(total) is float and not math.isfinite(total):
        raise ValueError("MAC 계산 결과가 유한한 숫자가 아닙니다.")

    return total
def normalize_label(label):
    """라벨 표현을 Cross 또는 X로 통일한다."""
    if not isinstance(label, str):
        raise TypeError("라벨은 문자열이어야 합니다.")

    cleaned = label.strip().casefold()

    aliases = {
        "+": "Cross",
        "cross": "Cross",
        "x": "X",
    }

    if cleaned not in aliases:
        raise ValueError(f"알 수 없는 라벨입니다: {label!r}")

    return aliases[cleaned]

EPSILON = 1e-9


def compare_scores(score_a, score_b, epsilon=EPSILON):
    """허용오차를 적용하여 A, B, UNDECIDED를 반환한다."""
    values = (
        ("A 점수", score_a),
        ("B 점수", score_b),
        ("epsilon", epsilon),
    )

    for name, value in values:
        if type(value) not in (int, float):
            raise TypeError(f"{name}는 정수 또는 실수여야 합니다.")

        if type(value) is float and not math.isfinite(value):
            raise ValueError(f"{name}는 유한한 숫자여야 합니다.")

    if epsilon <= 0:
        raise ValueError("epsilon은 0보다 커야 합니다.")

    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"

    if score_a > score_b:
        return "A"

    return "B"