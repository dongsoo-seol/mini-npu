import unittest

from main import Matrix


class TestMatrix(unittest.TestCase):
    def test_required_sizes(self):
        """네 가지 크기에서 생성과 저장·조회를 확인한다."""
        for size in (3, 5, 13, 25):
            with self.subTest(size=size):
                matrix = Matrix(size)

                self.assertEqual(len(matrix.data), size)
                self.assertTrue(
                    all(len(row) == size for row in matrix.data)
                )
                self.assertTrue(
                    all(value == 0 for row in matrix.data for value in row)
                )

                center = size // 2
                matrix.set_value(center, center, 7)
                self.assertEqual(matrix.get_value(center, center), 7)

                matrix.set_value(size - 1, size - 1, 1.5)
                self.assertEqual(
                    matrix.get_value(size - 1, size - 1), 1.5
                )

    def test_independent_rows(self):
        """한 행의 변경이 다른 행에 영향을 주지 않는다."""
        matrix = Matrix(3)
        matrix.set_value(1, 1, 7)

        self.assertEqual(matrix.get_value(0, 1), 0)
        self.assertEqual(matrix.get_value(2, 1), 0)

    def test_independent_matrices(self):
        """서로 다른 배열의 값이 독립적으로 유지된다."""
        first = Matrix(3)
        second = Matrix(3)
        first.set_value(1, 1, 7)

        self.assertEqual(second.get_value(1, 1), 0)

    def test_invalid_positions(self):
        """배열 범위를 벗어난 읽기와 쓰기를 거절한다."""
        matrix = Matrix(3)

        for row, col in ((-1, 0), (0, -1), (3, 0), (0, 3)):
            with self.subTest(row=row, col=col):
                with self.assertRaises(IndexError):
                    matrix.get_value(row, col)

                with self.assertRaises(IndexError):
                    matrix.set_value(row, col, 7)

    def test_invalid_values(self):
        """숫자가 아니거나 유효하지 않은 실수를 거절한다."""
        matrix = Matrix(3)

        for value in ("abc", None, True):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    matrix.set_value(0, 0, value)

        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    matrix.set_value(0, 0, value)


if __name__ == "__main__":
    unittest.main()