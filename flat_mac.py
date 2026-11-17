"""1차원 배열을 사용하는 보너스 MAC 구현."""

import math

from main import Matrix


class FlatMatrix:
    """Matrix의 값을 행 순서대로 복사한 1차원 배열."""

    def __init__(self, matrix):
        if not isinstance(matrix, Matrix):
            raise TypeError("변환할 자료는 Matrix 객체여야 합니다.")

        self.size = matrix.size
        self.data = [
            matrix.get_value(row, col)
            for row in range(matrix.size)
            for col in range(matrix.size)
        ]

    def get_value(self, row, col):
        if type(row) is not int or type(col) is not int:
            raise TypeError("행과 열 번호는 정수여야 합니다.")

        if not (0 <= row < self.size and 0 <= col < self.size):
            raise IndexError("행 또는 열 번호가 배열 범위를 벗어났습니다.")

        return self.data[row * self.size + col]


def mac_score_flat(pattern, filter_data):
    """1차원 배열의 같은 위치를 곱하고 순서대로 누적한다."""
    if not isinstance(pattern, FlatMatrix):
        raise TypeError("입력 패턴은 FlatMatrix 객체여야 합니다.")

    if not isinstance(filter_data, FlatMatrix):
        raise TypeError("필터는 FlatMatrix 객체여야 합니다.")

    if pattern.size != filter_data.size:
        raise ValueError("패턴과 필터의 크기가 일치해야 합니다.")

    length = pattern.size * pattern.size

    if len(pattern.data) != length or len(filter_data.data) != length:
        raise ValueError("1차원 배열의 길이는 N²이어야 합니다.")

    input_values = pattern.data
    filter_values = filter_data.data
    total = 0

    for index in range(length):
        total += input_values[index] * filter_values[index]

    if type(total) is float and not math.isfinite(total):
        raise ValueError("MAC 계산 결과가 유한한 숫자가 아닙니다.")

    return total