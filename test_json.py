import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from main import (
    Matrix,
    load_json_data,
    matrix_from_rows,
    parse_case_size,
    prepare_case,
)


class TestJson(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "data.json"

    def valid_data(self, size=5):
        rows = [[0 for _ in range(size)] for _ in range(size)]

        return {
            "filters": {
                f"size_{size}": {
                    "cross": deepcopy(rows),
                    "x": deepcopy(rows),
                }
            },
            "patterns": {
                f"size_{size}_1": {
                    "input": deepcopy(rows),
                    "expected": "+",
                }
            },
        }

    def test_matrix_conversion(self):
        """정상 배열을 원본과 독립적인 Matrix로 변환한다."""
        rows = [
            [0.5, -1, 2],
            [0, 0, 0],
            [0, 0, 0],
        ]
        matrix = matrix_from_rows(rows, 3, "시험 배열")

        self.assertIsInstance(matrix, Matrix)
        self.assertEqual(matrix.data, rows)

        matrix.set_value(0, 0, 7)
        self.assertEqual(rows[0][0], 0.5)

    def test_invalid_matrix_data(self):
        """잘못된 구조와 값을 위치 정보와 함께 거절한다."""
        cases = [
            None,
            {},
            [],
            [[0, 0, 0], [0, 0, 0]],
            [[0, 0, 0], "잘못된 행", [0, 0, 0]],
            [[0, 0, 0], [0, 0], [0, 0, 0]],
            [["abc", 0, 0], [0, 0, 0], [0, 0, 0]],
            [[True, 0, 0], [0, 0, 0], [0, 0, 0]],
            [[float("nan"), 0, 0], [0, 0, 0], [0, 0, 0]],
            [[float("inf"), 0, 0], [0, 0, 0], [0, 0, 0]],
        ]

        for index, rows in enumerate(cases):
            with self.subTest(case=index):
                with self.assertRaises(ValueError):
                    matrix_from_rows(rows, 3, "시험 배열")

        with self.assertRaises(ValueError) as caught:
            matrix_from_rows(
                [[0, 0, 0], [0, "abc", 0], [0, 0, 0]],
                3,
                "시험 배열",
            )

        self.assertIn("시험 배열", str(caught.exception))
        self.assertIn("2행 2열", str(caught.exception))

    def test_case_identifier(self):
        """식별자에서 크기를 추출하고 잘못된 이름을 거절한다."""
        for size in (3, 5, 13, 25):
            with self.subTest(size=size):
                self.assertEqual(
                    parse_case_size(f"size_{size}_1"), size
                )

        for case_id in (
            "size_5",
            "size_5_a",
            "wrong_5_1",
            "size_0_1",
            "size_-5_1",
            None,
        ):
            with self.subTest(case_id=case_id):
                with self.assertRaises(ValueError):
                    parse_case_size(case_id)

    def test_load_valid_json(self):
        """UTF-8 BOM이 있는 JSON도 원본 변경 없이 읽는다."""
        data = self.valid_data()
        self.path.write_text(
            json.dumps(data, ensure_ascii=False),
            encoding="utf-8-sig",
        )
        before = self.path.read_bytes()

        loaded = load_json_data(self.path)

        self.assertEqual(loaded, data)
        self.assertEqual(self.path.read_bytes(), before)

    def test_load_errors(self):
        """파일 오류와 잘못된 최상위 구조를 안내할 수 있게 한다."""
        with self.assertRaises(ValueError):
            load_json_data(self.path)

        self.path.write_text("{", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_json_data(self.path)

        self.path.write_bytes(b"\xff")
        with self.assertRaises(ValueError):
            load_json_data(self.path)

        invalid_documents = [
            [],
            {},
            {"filters": {}},
            {"filters": [], "patterns": {}},
            {"filters": {}, "patterns": []},
        ]

        for index, data in enumerate(invalid_documents):
            with self.subTest(case=index):
                self.path.write_text(
                    json.dumps(data), encoding="utf-8"
                )
                with self.assertRaises(ValueError):
                    load_json_data(self.path)

    def test_prepare_valid_sizes(self):
        """이름의 크기에 맞는 필터를 선택하고 원본을 유지한다."""
        for size in (5, 13, 25):
            with self.subTest(size=size):
                data = self.valid_data(size)

                # 현재 케이스와 무관한 필터는 검증에 사용하지 않는다.
                data["filters"]["size_3"] = {
                    "cross": [[9]],
                    "x": [[9]],
                }
                before = deepcopy(data)
                case_id = f"size_{size}_1"

                prepared = prepare_case(
                    case_id,
                    data["patterns"][case_id],
                    data["filters"],
                )

                self.assertEqual(prepared["size"], size)
                self.assertEqual(prepared["expected"], "Cross")
                self.assertEqual(
                    set(prepared["filters"]), {"Cross", "X"}
                )
                self.assertEqual(prepared["pattern"].size, size)
                self.assertEqual(
                    prepared["filters"]["Cross"].size, size
                )
                self.assertEqual(
                    prepared["filters"]["X"].size, size
                )
                self.assertEqual(data, before)

    def test_invalid_patterns(self):
        """필수 항목, 기대 라벨과 패턴 크기 오류를 거절한다."""
        data = self.valid_data()
        rows = data["patterns"]["size_5_1"]["input"]

        cases = [
            None,
            {},
            {"input": rows},
            {"expected": "+"},
            {"input": rows, "expected": "circle"},
            {"input": rows, "expected": None},
            {"input": rows[:-1], "expected": "+"},
        ]

        for index, item in enumerate(cases):
            with self.subTest(case=index):
                with self.assertRaises((ValueError, TypeError)):
                    prepare_case(
                        "size_5_1", item, data["filters"]
                    )

    def test_invalid_filters(self):
        """누락, 잘못된 크기, 알 수 없는 이름과 중복을 거절한다."""
        data = self.valid_data()
        item = data["patterns"]["size_5_1"]
        rows = item["input"]

        with self.assertRaises(ValueError):
            prepare_case("size_5_1", item, {})

        groups = [
            None,
            {},
            {"cross": rows},
            {"cross": rows, "x": rows[:-1]},
            {"cross": rows, "x": rows, "circle": rows},
            {"cross": rows, "Cross": rows, "x": rows},
        ]

        for index, group in enumerate(groups):
            with self.subTest(case=index):
                with self.assertRaises((ValueError, TypeError)):
                    prepare_case(
                        "size_5_1", item, {"size_5": group}
                    )


if __name__ == "__main__":
    unittest.main()