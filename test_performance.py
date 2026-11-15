import io
import math
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from unittest.mock import patch

from main import (
    Matrix,
    benchmark_sizes,
    mac_score,
    make_benchmark_pair,
    measure_mac_time,
    print_performance_table,
    run_json_mode,
    run_manual_mode,
)


class TestPerformance(unittest.TestCase):
    def test_average_ms_and_repetitions(self):
        """준비 실행을 제외한 10회 평균과 ms 환산을 확인한다."""
        pattern = Matrix(3)
        filter_data = Matrix(3)
        before = (
            deepcopy(pattern.data),
            deepcopy(filter_data.data),
        )
        ticks = [index * 0.001 for index in range(20)]

        with patch("time.perf_counter", side_effect=ticks) as timer:
            with patch("main.mac_score", wraps=mac_score) as calculate:
                result = measure_mac_time(pattern, filter_data)

        self.assertEqual(timer.call_count, 20)
        self.assertEqual(calculate.call_count, 11)
        self.assertAlmostEqual(result["average_ms"], 1.0)
        self.assertEqual(result["repeats"], 10)
        self.assertEqual(result["operations"], 9)
        self.assertEqual(
            (pattern.data, filter_data.data), before
        )

    def test_invalid_repetitions(self):
        """최소 10회와 정수 조건을 확인한다."""
        for repeats in ("10", None, True, 10.5):
            with self.subTest(repeats=repeats):
                with self.assertRaises(TypeError):
                    measure_mac_time(
                        Matrix(3), Matrix(3), repeats
                    )

        for repeats in (-1, 0, 9):
            with self.subTest(repeats=repeats):
                with self.assertRaises(ValueError):
                    measure_mac_time(
                        Matrix(3), Matrix(3), repeats
                    )

    def test_invalid_pair_before_timing(self):
        """잘못된 배열은 시간 측정 전에 거절한다."""
        with patch("time.perf_counter") as timer:
            with self.assertRaises(ValueError):
                measure_mac_time(Matrix(3), Matrix(5))

            timer.assert_not_called()

    def test_benchmark_arrays(self):
        """측정 자료가 크기별로 같은 숫자 조건인지 확인한다."""
        for size in (3, 5, 13, 25):
            with self.subTest(size=size):
                pattern, filter_data = make_benchmark_pair(size)

                self.assertTrue(
                    all(
                        value == 1.0
                        for row in pattern.data
                        for value in row
                    )
                )
                self.assertTrue(
                    all(
                        value == 1.0
                        for row in filter_data.data
                        for value in row
                    )
                )
                self.assertEqual(
                    mac_score(pattern, filter_data),
                    size * size,
                )

                pattern.set_value(0, 0, 7)
                self.assertEqual(
                    filter_data.get_value(0, 0), 1.0
                )

    def test_required_sizes(self):
        """네 크기의 실제 측정값과 연산 횟수를 확인한다."""
        results = benchmark_sizes()

        self.assertEqual(
            [result["size"] for result in results],
            [3, 5, 13, 25],
        )

        for result in results:
            with self.subTest(size=result["size"]):
                self.assertEqual(result["repeats"], 10)
                self.assertEqual(
                    result["operations"],
                    result["size"] ** 2,
                )
                self.assertTrue(
                    math.isfinite(result["average_ms"])
                )
                self.assertGreaterEqual(
                    result["average_ms"], 0
                )
                self.assertIn(
                    "공통 측정용 배열", result["source"]
                )

    def test_table_output(self):
        """표의 필수 항목과 시간 표시를 확인한다."""
        output = io.StringIO()
        example = {
            "size": 3,
            "average_ms": 1.234567,
            "operations": 9,
            "repeats": 10,
            "source": "시험용 측정값",
        }

        with redirect_stdout(output):
            print_performance_table([example])

        text = output.getvalue()
        self.assertIn("평균 시간(ms)", text)
        self.assertIn("연산 횟수(N²)", text)
        self.assertIn("측정 횟수", text)
        self.assertIn("3x3 | 1.234567 | 9 | 10", text)

    def test_manual_performance_order(self):
        """판정 후 실제 입력과 필터 A의 3×3 성능을 출력한다."""
        cross = ["0 1 0", "1 1 1", "0 1 0"]
        x_pattern = ["1 0 1", "0 1 0", "1 0 1"]
        output = io.StringIO()

        with patch(
            "main.measure_mac_time",
            wraps=measure_mac_time,
        ) as measured:
            with patch(
                "builtins.input",
                side_effect=cross + x_pattern + cross,
            ):
                with redirect_stdout(output):
                    result = run_manual_mode()

        text = output.getvalue()
        self.assertEqual(result["decision"], "A")
        self.assertEqual(measured.call_count, 1)

        pattern, filter_a = measured.call_args.args
        expected = [
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 0.0],
        ]
        self.assertEqual(pattern.data, expected)
        self.assertEqual(filter_a.data, expected)

        self.assertLess(
            text.index("판정 결과: A"),
            text.index("=== MAC 성능 분석 ==="),
        )
        self.assertIn("3x3 |", text)
        self.assertNotIn("5x5 |", text)
        self.assertIn("사용자 입력 패턴 / 필터 A", text)

    def test_json_performance_order(self):
        """케이스 결과와 전체 요약 사이에 네 크기를 출력한다."""
        output = io.StringIO()

        with redirect_stdout(output):
            report = run_json_mode()

        text = output.getvalue()
        self.assertEqual(report["total"], 6)
        self.assertEqual(report["passed"], 3)
        self.assertEqual(report["failed"], 3)

        self.assertLess(
            text.index("[케이스: size_25_2]"),
            text.index("=== MAC 성능 분석 ==="),
        )
        self.assertLess(
            text.index("=== MAC 성능 분석 ==="),
            text.index("=== 전체 분석 결과 ==="),
        )

        for size in (3, 5, 13, 25):
            with self.subTest(size=size):
                self.assertIn(f"{size}x{size} |", text)


if __name__ == "__main__":
    unittest.main()