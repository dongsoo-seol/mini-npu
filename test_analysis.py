import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path

import main
from main import (
    EPSILON,
    analyze_all_cases,
    load_json_data,
    run_json_mode,
)


class TestAnalysis(unittest.TestCase):
    def make_data(self):
        size = 5
        center = size // 2

        cross = [
            [
                1 if row == center or col == center else 0
                for col in range(size)
            ]
            for row in range(size)
        ]
        x_pattern = [
            [
                1 if row == col or row + col == size - 1 else 0
                for col in range(size)
            ]
            for row in range(size)
        ]

        return {
            "filters": {
                "size_5": {
                    "cross": cross,
                    "x": x_pattern,
                }
            },
            "patterns": {
                "size_5_1": {
                    "input": deepcopy(cross),
                    "expected": "+",
                },
                "size_5_2": {
                    "input": deepcopy(x_pattern),
                    "expected": "x",
                },
            },
        }

    def run_saved_data(self, data):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data.json"
            path.write_text(
                json.dumps(data, ensure_ascii=False),
                encoding="utf-8",
            )
            before = path.read_bytes()
            output = io.StringIO()

            with redirect_stdout(output):
                report = run_json_mode(path)

            self.assertEqual(path.read_bytes(), before)

        return report, output.getvalue()

    def test_matching_labels(self):
        """라벨을 정규화하고 Cross와 X를 올바르게 판정한다."""
        data = self.make_data()
        before = deepcopy(data)
        report = analyze_all_cases(data)

        self.assertEqual(report["total"], 2)
        self.assertEqual(report["passed"], 2)
        self.assertEqual(report["failed"], 0)
        self.assertEqual(report["failures"], [])
        self.assertEqual(
            [r["decision"] for r in report["results"]],
            ["Cross", "X"],
        )
        self.assertEqual(data, before)

    def test_mismatch_and_tie(self):
        """기대값 불일치와 동점을 각각 FAIL로 기록한다."""
        data = self.make_data()
        data["patterns"]["size_5_1"]["expected"] = "x"
        data["patterns"]["size_5_2"]["input"] = [
            [0 for _ in range(5)] for _ in range(5)
        ]

        report = analyze_all_cases(data)

        self.assertEqual(report["passed"], 0)
        self.assertEqual(report["failed"], 2)
        self.assertEqual(
            report["results"][0]["decision"], "Cross"
        )
        self.assertEqual(
            report["results"][1]["decision"], "UNDECIDED"
        )
        self.assertTrue(
            all(r["reason"] for r in report["failures"])
        )

    def test_invalid_case_continues(self):
        """첫 케이스의 크기 오류 후 다음 케이스를 분석한다."""
        data = self.make_data()
        data["patterns"]["size_5_1"]["input"] = [
            [0 for _ in range(5)] for _ in range(4)
        ]

        report = analyze_all_cases(data)
        first, second = report["results"]

        self.assertEqual(first["status"], "FAIL")
        self.assertIsNone(first["score_cross"])
        self.assertIsNone(first["score_x"])
        self.assertIsNone(first["decision"])
        self.assertIn("행 수", first["reason"])
        self.assertEqual(second["status"], "PASS")
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["passed"], 1)
        self.assertEqual(report["failed"], 1)

    def test_invalid_case_details(self):
        """식별자·필수 항목·필터·라벨 오류를 FAIL로 모은다."""
        rows = [[0 for _ in range(5)] for _ in range(5)]
        cases = [
            ("wrong_case", {"input": rows, "expected": "+"}),
            ("size_5_3", {"input": rows}),
            ("size_13_1", {"input": rows, "expected": "+"}),
            ("size_5_4", {"input": rows, "expected": "circle"}),
        ]

        for case_id, item in cases:
            with self.subTest(case_id=case_id):
                data = self.make_data()
                data["patterns"][case_id] = item
                report = analyze_all_cases(data)

                self.assertEqual(report["total"], 3)
                self.assertEqual(report["passed"], 2)
                self.assertEqual(report["failed"], 1)
                self.assertEqual(
                    report["failures"][0]["id"], case_id
                )
                self.assertTrue(
                    report["failures"][0]["reason"]
                )

    def test_file_error_no_summary(self):
        """파일 오류를 정상 분석의 0 FAIL로 표시하지 않는다."""
        with tempfile.TemporaryDirectory() as folder:
            missing = Path(folder) / "missing.json"
            broken = Path(folder) / "broken.json"
            broken.write_text("{", encoding="utf-8")

            for path in (missing, broken):
                with self.subTest(path=path.name):
                    output = io.StringIO()

                    with redirect_stdout(output):
                        report = run_json_mode(path)

                    self.assertIsNone(report)
                    self.assertIn(
                        "JSON 분석을 시작할 수 없습니다",
                        output.getvalue(),
                    )
                    self.assertNotIn(
                        "=== 전체 분석 결과 ===",
                        output.getvalue(),
                    )

    def test_mode_output_summary(self):
        """계산 불가 표시와 출력 순서·집계를 확인한다."""
        data = self.make_data()
        data["patterns"]["size_5_1"]["input"] = []

        report, output = self.run_saved_data(data)

        self.assertEqual(report["total"], 2)
        self.assertIn("Cross 점수: 계산 불가", output)
        self.assertIn("X 점수: 계산 불가", output)
        self.assertIn("전체 테스트 수: 2", output)
        self.assertIn("통과 수: 1", output)
        self.assertIn("실패 수: 1", output)
        self.assertIn("- size_5_1:", output)

        self.assertLess(
            output.index("[케이스: size_5_2]"),
            output.index("=== 전체 분석 결과 ==="),
        )

    def test_mode_zero_failures(self):
        """실패가 없을 때 집계와 없음 표시를 확인한다."""
        report, output = self.run_saved_data(self.make_data())

        self.assertEqual(report["failed"], 0)
        self.assertIn("실패 수: 0", output)
        self.assertIn("[실패 케이스]\n없음", output)

    def test_epsilon_in_json_analysis(self):
        """점수가 조금 더 높아도 epsilon 이내면 동점이다."""
        data = self.make_data()
        pattern = [[0 for _ in range(5)] for _ in range(5)]
        pattern[0][0] = EPSILON / 2
        data["patterns"]["size_5_1"] = {
            "input": pattern,
            "expected": "x",
        }

        report = analyze_all_cases(data)
        result = report["results"][0]

        self.assertEqual(result["score_cross"], 0)
        self.assertGreater(result["score_x"], 0)
        self.assertEqual(result["decision"], "UNDECIDED")
        self.assertEqual(result["status"], "FAIL")

    def test_provided_data_report(self):
        """제공 원본의 실제 분석 결과와 원본 유지를 확인한다."""
        path = Path(main.__file__).resolve().parent / "data.json"
        before = path.read_bytes()

        report = analyze_all_cases(load_json_data())

        self.assertEqual(report["total"], 6)
        self.assertEqual(report["passed"], 3)
        self.assertEqual(report["failed"], 3)
        self.assertEqual(
            {r["id"] for r in report["failures"]},
            {"size_5_1", "size_13_2", "size_25_1"},
        )
        self.assertTrue(
            all(
                r["decision"] == "UNDECIDED"
                for r in report["failures"]
            )
        )
        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
