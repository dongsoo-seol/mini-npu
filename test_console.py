import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import main


class TestConsole(unittest.TestCase):
    CROSS = ["0 1 0", "1 1 1", "0 1 0"]
    X_PATTERN = ["1 0 1", "0 1 0", "1 0 1"]

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.script = self.folder / "main.py"
        self.data_path = self.folder / "data.json"

        source = Path(main.__file__).resolve().parent
        shutil.copy2(source / "main.py", self.script)
        shutil.copy2(source / "data.json", self.data_path)

    def run_program(self, lines, cwd=None):
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(self.script)],
            input=lines,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=self.folder if cwd is None else cwd,
            timeout=20,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result.stdout

    def test_menu_validation_and_exit(self):
        """메뉴의 문자·빈 입력·범위 오류와 종료를 확인한다."""
        output = self.run_program("abc\n\n9\n 0 \n")

        self.assertEqual(output.count("입력 오류:"), 3)
        self.assertIn("프로그램을 종료합니다.", output)
        self.assertNotIn("JSON 케이스별 분석", output)

    def test_manual_mode(self):
        """실제 실행 파일에서 사용자 모드 전체를 확인한다."""
        lines = (
            ["1"]
            + self.CROSS
            + self.X_PATTERN
            + self.CROSS
            + ["0"]
        )
        output = self.run_program("\n".join(lines) + "\n")

        self.assertIn("필터 A MAC 점수: 5", output)
        self.assertIn("필터 B MAC 점수: 1", output)
        self.assertIn("판정 결과: A", output)
        self.assertIn("3x3 |", output)
        self.assertIn("사용자 입력 패턴 / 필터 A", output)
        self.assertNotIn("5x5 |", output)

        self.assertLess(
            output.index("=== 필터 저장 확인 ==="),
            output.index("입력 패턴 입력:"),
        )
        self.assertLess(
            output.index("판정 결과: A"),
            output.index("=== MAC 성능 분석 ==="),
        )
        self.assertEqual(
            output.count("=== Mini NPU 시뮬레이터 ==="), 2
        )

    def test_json_mode(self):
        """실제 실행 파일의 JSON 분석과 출력 순서를 확인한다."""
        before = self.data_path.read_bytes()
        output = self.run_program("2\n0\n")

        self.assertEqual(output.count("[케이스:"), 6)
        self.assertIn("전체 테스트 수: 6", output)
        self.assertIn("통과 수: 3", output)
        self.assertIn("실패 수: 3", output)

        for case_id in ("size_5_1", "size_13_2", "size_25_1"):
            with self.subTest(case_id=case_id):
                self.assertIn(f"- {case_id}:", output)

        for size in (3, 5, 13, 25):
            with self.subTest(size=size):
                self.assertIn(f"{size}x{size} |", output)

        self.assertLess(
            output.index("[케이스: size_25_2]"),
            output.index("=== MAC 성능 분석 ==="),
        )
        self.assertLess(
            output.index("=== MAC 성능 분석 ==="),
            output.index("=== 전체 분석 결과 ==="),
        )
        self.assertEqual(
            output.count("=== Mini NPU 시뮬레이터 ==="), 2
        )
        self.assertEqual(self.data_path.read_bytes(), before)

    def test_manual_input_errors(self):
        """실행 파일에서도 잘못된 행을 다시 입력받는다."""
        lines = [
            "1",
            "0 1",
            "0 1 0 1",
            "0 abc 0",
            "",
            "0 nan 0",
        ]
        lines += self.CROSS + self.X_PATTERN + self.CROSS + ["0"]

        output = self.run_program("\n".join(lines) + "\n")

        self.assertIn("입력 형식 오류", output)
        self.assertIn("NaN이나 무한대", output)
        self.assertIn("필터 A MAC 점수: 5", output)
        self.assertIn("판정 결과: A", output)
        self.assertIn("프로그램을 종료합니다.", output)

    def test_invalid_case_continues(self):
        """복사본의 첫 케이스 오류 후 나머지 분석을 계속한다."""
        data = json.loads(
            self.data_path.read_text(encoding="utf-8-sig")
        )
        data["patterns"]["size_5_1"]["input"] = []
        self.data_path.write_text(
            json.dumps(data, ensure_ascii=False),
            encoding="utf-8",
        )

        output = self.run_program("2\n0\n")

        self.assertEqual(output.count("[케이스:"), 6)
        self.assertIn("Cross 점수: 계산 불가", output)
        self.assertIn("행 수", output)
        self.assertIn("[케이스: size_25_2]", output)
        self.assertIn("전체 테스트 수: 6", output)
        self.assertIn("통과 수: 3", output)
        self.assertIn("실패 수: 3", output)
        self.assertIn("=== MAC 성능 분석 ===", output)

    def test_json_file_errors(self):
        """파일 오류를 안내하고 메뉴로 돌아온다."""
        cases = [
            ("파일 없음", None),
            ("JSON 손상", "{"),
            ("최상위 구조 오류", "[]"),
        ]

        for name, content in cases:
            with self.subTest(case=name):
                if self.data_path.exists():
                    self.data_path.unlink()

                if content is not None:
                    self.data_path.write_text(
                        content, encoding="utf-8"
                    )

                output = self.run_program("2\n0\n")

                self.assertIn(
                    "JSON 분석을 시작할 수 없습니다", output
                )
                self.assertNotIn(
                    "=== 전체 분석 결과 ===", output
                )
                self.assertNotIn(
                    "=== MAC 성능 분석 ===", output
                )
                self.assertEqual(
                    output.count("=== Mini NPU 시뮬레이터 ==="),
                    2,
                )
                self.assertIn(
                    "프로그램을 종료합니다.", output
                )

    def test_eof_exit(self):
        """메뉴와 분석 중 입력 종료를 안내하고 끝낸다."""
        cases = [
            "",
            "1\n",
            "1\n0 1 0\n",
            "2\n",
        ]

        for lines in cases:
            with self.subTest(input=repr(lines)):
                output = self.run_program(lines)
                self.assertIn(
                    "입력이 종료되어 프로그램을 종료합니다.",
                    output,
                )

    def test_keyboard_interrupt_exit(self):
        """모의 KeyboardInterrupt를 최종 실행 부분에서 처리한다."""
        cases = [
            ["__INTERRUPT__"],
            ["1"] + self.CROSS + self.X_PATTERN + ["__INTERRUPT__"],
        ]

        for responses in cases:
            with self.subTest(responses=responses):
                helper = (
                    "import builtins, runpy\n"
                    f"responses = iter({responses!r})\n"
                    "def fake_input(prompt=''):\n"
                    "    value = next(responses)\n"
                    "    if value == '__INTERRUPT__':\n"
                    "        raise KeyboardInterrupt\n"
                    "    return value\n"
                    "builtins.input = fake_input\n"
                    f"runpy.run_path({str(self.script)!r}, "
                    "run_name='__main__')\n"
                )

                result = subprocess.run(
                    [sys.executable, "-X", "utf8", "-c", helper],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    cwd=self.folder,
                    timeout=20,
                )

                self.assertEqual(
                    result.returncode, 0, result.stderr
                )
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn(
                    "입력이 취소되어 프로그램을 종료합니다.",
                    result.stdout,
                )

    def test_other_working_directory(self):
        """다른 작업 폴더에서도 실행 파일 옆 JSON을 읽는다."""
        outside = self.folder / "outside"
        outside.mkdir()
        before = self.data_path.read_bytes()

        output = self.run_program("2\n0\n", cwd=outside)

        self.assertIn("전체 테스트 수: 6", output)
        self.assertIn("통과 수: 3", output)
        self.assertIn("실패 수: 3", output)
        self.assertEqual(self.data_path.read_bytes(), before)
        self.assertEqual(list(outside.iterdir()), [])

    def test_import_without_menu(self):
        """함수를 불러오기만 할 때 메뉴를 실행하지 않는다."""
        result = subprocess.run(
            [
                sys.executable,
                "-X",
                "utf8",
                "-c",
                "import main; print('불러오기 성공')",
            ],
            input="",
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=self.folder,
            timeout=20,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "불러오기 성공")
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()