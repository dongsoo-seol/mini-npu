import unittest

from main import EPSILON, compare_scores, normalize_label


class TestPolicies(unittest.TestCase):
    def test_label_normalization(self):
        """필수 라벨과 공백·대소문자 표현을 표준화한다."""
        cases = [
            ("+", "Cross"),
            ("cross", "Cross"),
            ("Cross", "Cross"),
            (" CROSS ", "Cross"),
            ("x", "X"),
            ("X", "X"),
            (" x ", "X"),
        ]

        for original, expected in cases:
            with self.subTest(label=original):
                result = normalize_label(original)
                self.assertEqual(result, expected)
                self.assertEqual(normalize_label(result), expected)

    def test_invalid_labels(self):
        """알 수 없거나 문자열이 아닌 라벨을 거절한다."""
        for label in ("", " ", "circle", "UNDECIDED"):
            with self.subTest(label=label):
                with self.assertRaises(ValueError):
                    normalize_label(label)

        for label in (None, 1, True, []):
            with self.subTest(label=label):
                with self.assertRaises(TypeError):
                    normalize_label(label)

    def test_larger_score(self):
        """동점이 아니면 높은 점수를 선택한다."""
        cases = [
            (5, 1, "A"),
            (1, 5, "B"),
            (-1, -5, "A"),
            (-5, -1, "B"),
        ]

        for score_a, score_b, expected in cases:
            with self.subTest(a=score_a, b=score_b):
                self.assertEqual(
                    compare_scores(score_a, score_b), expected
                )

    def test_ties(self):
        """같은 점수와 epsilon보다 작은 차이는 동점이다."""
        cases = [
            (0, 0),
            (5, 5),
            (-3, -3),
            (0, EPSILON / 2),
            (EPSILON / 2, 0),
            (-EPSILON / 2, 0),
        ]

        for score_a, score_b in cases:
            with self.subTest(a=score_a, b=score_b):
                self.assertEqual(
                    compare_scores(score_a, score_b),
                    "UNDECIDED",
                )

    def test_epsilon_boundary(self):
        """차이가 epsilon 이상이면 동점으로 처리하지 않는다."""
        cases = [
            (0, EPSILON, "B"),
            (EPSILON, 0, "A"),
            (0, EPSILON * 2, "B"),
            (EPSILON * 2, 0, "A"),
        ]

        for score_a, score_b, expected in cases:
            with self.subTest(a=score_a, b=score_b):
                self.assertEqual(
                    compare_scores(score_a, score_b), expected
                )

    def test_custom_epsilon(self):
        """전달한 epsilon에 따라 비교 정책을 적용한다."""
        self.assertEqual(
            compare_scores(0.01, 0.02, epsilon=0.1),
            "UNDECIDED",
        )
        self.assertEqual(
            compare_scores(0.01, 0.02, epsilon=0.001),
            "B",
        )

    def test_invalid_scores(self):
        """잘못된 자료형과 유한하지 않은 점수를 거절한다."""
        for value in ("5", None, True):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    compare_scores(value, 0)

                with self.assertRaises(TypeError):
                    compare_scores(0, value)

        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    compare_scores(value, 0)

                with self.assertRaises(ValueError):
                    compare_scores(0, value)

    def test_invalid_epsilon(self):
        """epsilon은 양수인 유한한 숫자여야 한다."""
        for value in ("0.1", None, True):
            with self.subTest(epsilon=value):
                with self.assertRaises(TypeError):
                    compare_scores(1, 2, epsilon=value)

        for value in (
            0,
            -1,
            float("nan"),
            float("inf"),
            float("-inf"),
        ):
            with self.subTest(epsilon=value):
                with self.assertRaises(ValueError):
                    compare_scores(1, 2, epsilon=value)


if __name__ == "__main__":
    unittest.main()