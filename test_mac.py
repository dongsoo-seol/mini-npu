import unittest

from main import Matrix, mac_score


class TestMac(unittest.TestCase):
    def make_matrix(self, rows):
        matrix = Matrix(len(rows))

        for row_number, row in enumerate(rows):
            for col_number, value in enumerate(row):
                matrix.set_value(row_number, col_number, value)

        return matrix

    def test_cross_and_x_scores(self):
        """십자가와 X의 네 가지 조합을 확인한다."""
        cross = self.make_matrix([
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0],
        ])
        x_pattern = self.make_matrix([
            [1, 0, 1],
            [0, 1, 0],
            [1, 0, 1],
        ])

        cases = [
            ("십자가와 십자가", cross, cross, 5),
            ("십자가와 X", cross, x_pattern, 1),
            ("X와 십자가", x_pattern, cross, 1),
            ("X와 X", x_pattern, x_pattern, 5),
        ]

        for name, pattern, filter_data, expected in cases:
            with self.subTest(case=name):
                self.assertEqual(
                    mac_score(pattern, filter_data), expected
                )

    def test_decimal_and_negative_values(self):
        """소수와 음수가 포함된 계산을 확인한다."""
        pattern = self.make_matrix([
            [0.5, -1.5, 2],
            [0, 0, 0],
            [0, 0, 0],
        ])
        filter_data = self.make_matrix([
            [2, 4, 0.25],
            [0, 0, 0],
            [0, 0, 0],
        ])

        # 0.5×2 + (-1.5)×4 + 2×0.25 = -4.5
        self.assertAlmostEqual(
            mac_score(pattern, filter_data), -4.5
        )

    def test_zero_pattern(self):
        """입력이 모두 0이면 점수도 0이다."""
        pattern = Matrix(3)
        filter_data = self.make_matrix([
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0],
        ])

        self.assertEqual(mac_score(pattern, filter_data), 0)

    def test_required_sizes(self):
        """네 크기에서 모든 위치가 계산되는지 확인한다."""
        for size in (3, 5, 13, 25):
            with self.subTest(size=size):
                pattern = Matrix(size)
                filter_data = Matrix(size)

                for row in range(size):
                    for col in range(size):
                        pattern.set_value(row, col, 1)
                        filter_data.set_value(row, col, 2)

                self.assertEqual(
                    mac_score(pattern, filter_data),
                    2 * size * size,
                )

    def test_size_mismatch(self):
        """서로 다른 크기의 배열은 계산하지 않는다."""
        with self.assertRaises(ValueError):
            mac_score(Matrix(3), Matrix(5))

    def test_invalid_arguments(self):
        """Matrix가 아닌 인수를 거절한다."""
        with self.assertRaises(TypeError):
            mac_score([], Matrix(3))

        with self.assertRaises(TypeError):
            mac_score(Matrix(3), [])

    def test_nonfinite_result(self):
        """큰 실수의 곱으로 무한대가 발생하면 거절한다."""
        pattern = Matrix(3)
        filter_data = Matrix(3)

        pattern.set_value(0, 0, 1e308)
        filter_data.set_value(0, 0, 1e308)

        with self.assertRaises(ValueError):
            mac_score(pattern, filter_data)


if __name__ == "__main__":
    unittest.main()