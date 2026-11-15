import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from main import read_matrix, run_manual_mode


class TestInput(unittest.TestCase):
    CROSS = ["0 1 0", "1 1 1", "0 1 0"]
    X_PATTERN = ["1 0 1", "0 1 0", "1 0 1"]
    ZERO = ["0 0 0", "0 0 0", "0 0 0"]

    def run_mode(self, lines):
        output = io.StringIO()

        with patch("builtins.input", side_effect=lines):
            with redirect_stdout(output):
                result = run_manual_mode()

        return result, output.getvalue()

    def test_read_valid_values(self):
        """공백, 소수와 음수를 입력받는다."""
        lines = ["  0.5   -1.5  2  ", "0 0 0", "0 0 0"]

        with patch("builtins.input", side_effect=lines):
            with redirect_stdout(io.StringIO()):
                matrix = read_matrix(3, "시험 배열")

        self.assertEqual(
            matrix.data,
            [[0.5, -1.5, 2.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
        )

    def test_read_invalid_values(self):
        """잘못된 행만 다시 받고 앞서 저장한 행을 유지한다."""
        lines = [
            "0 1 0",
            "1 1",
            "1 1 1 1",
            "1 abc 1",
            "",
            "1 nan 1",
            "1 inf 1",
            "1 1 1",
            "0 1 0",
        ]
        output = io.StringIO()

        with patch("builtins.input", side_effect=lines):
            with redirect_stdout(output):
                matrix = read_matrix(3, "시험 배열")

        self.assertEqual(
            matrix.data,
            [[0.0, 1.0, 0.0], [1.0, 1.0, 1.0], [0.0, 1.0, 0.0]],
        )
        self.assertIn("입력 형식 오류", output.getvalue())
        self.assertIn("NaN이나 무한대", output.getvalue())

    def test_read_interrupted(self):
        """중단된 입력을 완성된 배열로 반환하지 않는다."""
        for error_type in (EOFError, KeyboardInterrupt):
            with self.subTest(error=error_type.__name__):
                with patch(
                    "builtins.input",
                    side_effect=["0 1 0", error_type()],
                ):
                    with redirect_stdout(io.StringIO()):
                        with self.assertRaises(error_type):
                            read_matrix(3, "시험 배열")

    def test_manual_decisions(self):
        """패턴과 필터 배치에 따라 A/B/동점을 판정한다."""
        cases = [
            (
                "십자가 입력",
                self.CROSS, self.X_PATTERN, self.CROSS,
                5, 1, "A",
            ),
            (
                "X 입력",
                self.CROSS, self.X_PATTERN, self.X_PATTERN,
                1, 5, "B",
            ),
            (
                "필터 순서 교환",
                self.X_PATTERN, self.CROSS, self.CROSS,
                1, 5, "B",
            ),
            (
                "모두 0",
                self.CROSS, self.X_PATTERN, self.ZERO,
                0, 0, "UNDECIDED",
            ),
        ]

        for name, filter_a, filter_b, pattern, a, b, expected in cases:
            with self.subTest(case=name):
                result, output = self.run_mode(
                    filter_a + filter_b + pattern
                )

                self.assertEqual(result["score_a"], a)
                self.assertEqual(result["score_b"], b)
                self.assertEqual(result["decision"], expected)

                displayed = (
                    "판정 불가" if expected == "UNDECIDED" else expected
                )
                self.assertIn(f"판정 결과: {displayed}", output)

    def test_manual_output_order(self):
        """필터 저장 확인이 패턴 입력보다 먼저 나온다."""
        _, output = self.run_mode(
            self.CROSS + self.X_PATTERN + self.CROSS
        )
        markers = [
            "필터 A 입력:",
            "필터 B 입력:",
            "=== 필터 저장 확인 ===",
            "입력 패턴 입력:",
            "=== 사용자 입력 분석 결과 ===",
        ]
        positions = [output.index(marker) for marker in markers]

        self.assertEqual(positions, sorted(positions))

    def test_manual_epsilon(self):
        """실제 MAC 점수의 근소한 차이에도 동점 정책을 적용한다."""
        filter_b = ["1 0 0", "0 0 0", "0 0 0"]
        pattern = ["5e-10 0 0", "0 0 0", "0 0 0"]

        result, output = self.run_mode(
            self.ZERO + filter_b + pattern
        )

        self.assertEqual(result["score_a"], 0)
        self.assertAlmostEqual(result["score_b"], 5e-10, delta=1e-20)
        self.assertEqual(result["decision"], "UNDECIDED")
        self.assertIn("판정 결과: 판정 불가", output)

    def test_manual_calculation_error(self):
        """계산 결과가 무한대이면 안내하고 분석을 마친다."""
        large = ["1e308 0 0", "0 0 0", "0 0 0"]

        result, output = self.run_mode(
            large + self.ZERO + large
        )

        self.assertIsNone(result)
        self.assertIn("계산 오류:", output)


if __name__ == "__main__":
    unittest.main()