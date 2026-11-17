import unittest

from main import Matrix, mac_score
from flat_mac import FlatMatrix, mac_score_flat


class TestFlatMac(unittest.TestCase):
    def test_required_sizes_and_order(self):
        """네 크기에서 길이, 행 우선 순서와 위치 조회를 확인한다."""
        for size in (3, 5, 13, 25):
            with self.subTest(size=size):
                matrix = Matrix(size)

                for row in range(size):
                    for col in range(size):
                        matrix.set_value(row, col, row * size + col)

                flat = FlatMatrix(matrix)

                self.assertEqual(len(flat.data), size * size)
                self.assertEqual(flat.data, list(range(size * size)))

                for row in range(size):
                    for col in range(size):
                        self.assertEqual(
                            flat.get_value(row, col),
                            matrix.get_value(row, col),
                        )

    def test_independent_storage(self):
        """변환 전후의 목록이 서로 영향을 주지 않는다."""
        matrix = Matrix(3)
        matrix.set_value(1, 1, 7)
        flat = FlatMatrix(matrix)

        matrix.set_value(1, 1, 9)
        self.assertEqual(flat.get_value(1, 1), 7)

        flat.data[0] = 5
        self.assertEqual(matrix.get_value(0, 0), 0)

    def test_scores_match_for_required_sizes(self):
        """모든 위치에 소수와 음수를 넣어 기존 MAC과 비교한다."""
        for size in (3, 5, 13, 25):
            with self.subTest(size=size):
                pattern = Matrix(size)
                filter_data = Matrix(size)

                for row in range(size):
                    for col in range(size):
                        pattern.set_value(
                            row, col, (row - col) * 0.25
                        )
                        filter_data.set_value(
                            row, col, (row + col + 1) * 0.5
                        )

                expected = mac_score(pattern, filter_data)
                actual = mac_score_flat(
                    FlatMatrix(pattern), FlatMatrix(filter_data)
                )

                self.assertEqual(actual, expected)

    def test_cross_and_x_scores(self):
        """알려진 점수로 계산의 정확성을 확인한다."""
        cross = Matrix(3)
        x_shape = Matrix(3)

        for row in range(3):
            for col in range(3):
                cross.set_value(row, col, int(row == 1 or col == 1))
                x_shape.set_value(
                    row, col, int(row == col or row + col == 2)
                )

        flat_cross = FlatMatrix(cross)
        flat_x = FlatMatrix(x_shape)

        self.assertEqual(mac_score_flat(flat_cross, flat_cross), 5)
        self.assertEqual(mac_score_flat(flat_cross, flat_x), 1)
        self.assertEqual(mac_score_flat(flat_x, flat_cross), 1)
        self.assertEqual(mac_score_flat(flat_x, flat_x), 5)

    def test_invalid_arguments_and_sizes(self):
        """잘못된 객체와 서로 다른 배열 크기를 거절한다."""
        flat = FlatMatrix(Matrix(3))

        with self.assertRaises(TypeError):
            FlatMatrix([[0]])

        with self.assertRaises(TypeError):
            mac_score_flat(Matrix(3), flat)

        with self.assertRaises(TypeError):
            mac_score_flat(flat, Matrix(3))

        with self.assertRaises(ValueError):
            mac_score_flat(flat, FlatMatrix(Matrix(5)))

    def test_invalid_positions(self):
        """음수, 범위 밖 위치와 잘못된 인덱스 자료형을 거절한다."""
        flat = FlatMatrix(Matrix(3))

        for row, col in ((-1, 0), (0, -1), (3, 0), (0, 3)):
            with self.subTest(row=row, col=col):
                with self.assertRaises(IndexError):
                    flat.get_value(row, col)

        for row, col in ((True, 0), (0, 1.5), ("1", 0)):
            with self.subTest(row=row, col=col):
                with self.assertRaises(TypeError):
                    flat.get_value(row, col)

    def test_nonfinite_result(self):
        """유한한 입력의 곱이 무한대가 되는 경우를 거절한다."""
        pattern = Matrix(3)
        filter_data = Matrix(3)
        pattern.set_value(0, 0, 1e308)
        filter_data.set_value(0, 0, 1e308)

        with self.assertRaises(ValueError):
            mac_score_flat(
                FlatMatrix(pattern), FlatMatrix(filter_data)
            )


if __name__ == "__main__":
    unittest.main()