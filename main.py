import math


class Matrix:
    """N×N 숫자 배열을 저장하고 조회한다."""

    def __init__(self, size):
        if type(size) is not int:
            raise TypeError("배열 크기는 정수여야 합니다.")

        if size <= 0:
            raise ValueError("배열 크기는 0보다 커야 합니다.")

        self.size = size
        self.data = [
            [0 for _ in range(size)]
            for _ in range(size)
        ]

    def _check_position(self, row, col):
        if type(row) is not int or type(col) is not int:
            raise TypeError("행과 열 번호는 정수여야 합니다.")

        if not (0 <= row < self.size and 0 <= col < self.size):
            raise IndexError(
                f"행과 열 번호는 0부터 {self.size - 1} 사이여야 합니다."
            )

    def get_value(self, row, col):
        self._check_position(row, col)
        return self.data[row][col]

    def set_value(self, row, col, value):
        self._check_position(row, col)

        if type(value) not in (int, float):
            raise TypeError("배열의 값은 정수 또는 실수여야 합니다.")

        if type(value) is float and not math.isfinite(value):
            raise ValueError("NaN이나 무한대는 사용할 수 없습니다.")

        self.data[row][col] = value
def mac_score(pattern, filter_data):
    """같은 위치의 값을 곱하고 누적하여 점수를 반환한다."""
    if not isinstance(pattern, Matrix):
        raise TypeError("입력 패턴은 Matrix 객체여야 합니다.")

    if not isinstance(filter_data, Matrix):
        raise TypeError("필터는 Matrix 객체여야 합니다.")

    if pattern.size != filter_data.size:
        raise ValueError("패턴과 필터의 크기가 일치해야 합니다.")

    total = 0

    for row in range(pattern.size):
        for col in range(pattern.size):
            input_value = pattern.get_value(row, col)
            filter_value = filter_data.get_value(row, col)
            total += input_value * filter_value

    if type(total) is float and not math.isfinite(total):
        raise ValueError("MAC 계산 결과가 유한한 숫자가 아닙니다.")

    return total
def normalize_label(label):
    """라벨 표현을 Cross 또는 X로 통일한다."""
    if not isinstance(label, str):
        raise TypeError("라벨은 문자열이어야 합니다.")

    cleaned = label.strip().casefold()

    aliases = {
        "+": "Cross",
        "cross": "Cross",
        "x": "X",
    }

    if cleaned not in aliases:
        raise ValueError(f"알 수 없는 라벨입니다: {label!r}")

    return aliases[cleaned]

EPSILON = 1e-9


def compare_scores(score_a, score_b, epsilon=EPSILON):
    """허용오차를 적용하여 A, B, UNDECIDED를 반환한다."""
    values = (
        ("A 점수", score_a),
        ("B 점수", score_b),
        ("epsilon", epsilon),
    )

    for name, value in values:
        if type(value) not in (int, float):
            raise TypeError(f"{name}는 정수 또는 실수여야 합니다.")

        if type(value) is float and not math.isfinite(value):
            raise ValueError(f"{name}는 유한한 숫자여야 합니다.")

    if epsilon <= 0:
        raise ValueError("epsilon은 0보다 커야 합니다.")

    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"

    if score_a > score_b:
        return "A"

    return "B"
def read_matrix(size, name):
    """숫자를 한 행씩 입력받아 정사각형 배열을 만든다."""
    matrix = Matrix(size)
    error_message = (
        f"입력 형식 오류: 각 줄에 {size}개의 숫자를 "
        "공백으로 구분해 입력하세요."
    )

    print(f"\n{name} 입력: {size}행을 입력하세요.")

    for row in range(size):
        while True:
            parts = input(f"{row + 1}행: ").split()

            if len(parts) != size:
                print(error_message)
                continue

            try:
                values = [float(part) for part in parts]
            except ValueError:
                print(error_message)
                continue

            if not all(math.isfinite(value) for value in values):
                print("입력값 오류: NaN이나 무한대는 사용할 수 없습니다.")
                continue

            for col, value in enumerate(values):
                matrix.set_value(row, col, value)

            break

    return matrix
def print_matrix(matrix, name):
    """저장된 배열을 행 단위로 출력한다."""
    print(f"\n{name}")

    for row in range(matrix.size):
        line = [
            f"{matrix.get_value(row, col):g}"
            for col in range(matrix.size)
        ]
        print(" ".join(line))


def run_manual_mode():
    """3×3 필터 두 개와 패턴을 입력받아 분석한다."""
    filter_a = read_matrix(3, "필터 A")
    filter_b = read_matrix(3, "필터 B")

    print("\n=== 필터 저장 확인 ===")
    print_matrix(filter_a, "필터 A")
    print_matrix(filter_b, "필터 B")

    pattern = read_matrix(3, "입력 패턴")

    try:
        score_a = mac_score(pattern, filter_a)
        score_b = mac_score(pattern, filter_b)
        decision = compare_scores(score_a, score_b)
    except ValueError as error:
        print(f"\n계산 오류: {error}")
        return None

    displayed = (
        "판정 불가"
        if decision == "UNDECIDED"
        else decision
    )

    print("\n=== 사용자 입력 분석 결과 ===")
    print(f"필터 A MAC 점수: {score_a:g}")
    print(f"필터 B MAC 점수: {score_b:g}")
    print(f"판정 결과: {displayed}")

    return {
        "score_a": score_a,
        "score_b": score_b,
        "decision": decision,
    }
def matrix_from_rows(rows, size, name="배열"):
    """외부 배열의 구조와 값을 검사하여 Matrix로 변환한다."""
    if type(size) is not int or size <= 0:
        raise ValueError("배열 크기는 0보다 큰 정수여야 합니다.")

    if not isinstance(rows, list):
        raise ValueError(f"{name}: 배열은 리스트여야 합니다.")

    if len(rows) != size:
        raise ValueError(
            f"{name}: 행 수가 {len(rows)}개입니다. "
            f"{size}개여야 합니다."
        )

    for row_number, row in enumerate(rows, start=1):
        if not isinstance(row, list):
            raise ValueError(
                f"{name}: {row_number}행은 리스트여야 합니다."
            )

        if len(row) != size:
            raise ValueError(
                f"{name}: {row_number}행의 열 수가 {len(row)}개입니다. "
                f"{size}개여야 합니다."
            )

    matrix = Matrix(size)

    for row_number, row in enumerate(rows):
        for col_number, value in enumerate(row):
            try:
                matrix.set_value(row_number, col_number, value)
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"{name}: {row_number + 1}행 "
                    f"{col_number + 1}열 값 오류: {error}"
                ) from error

    return matrix
def load_json_data(file_path=None):
    """JSON 파일을 읽고 최상위 구조를 확인한다."""
    import json
    from pathlib import Path

    if file_path is None:
        path = Path(__file__).resolve().parent / "data.json"
    else:
        path = Path(file_path)

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
    except (OSError, UnicodeError, ValueError) as error:
        raise ValueError(
            f"JSON 파일을 읽을 수 없습니다: {path} / {error}"
        ) from error

    if not isinstance(data, dict):
        raise ValueError("JSON 최상위 자료는 딕셔너리여야 합니다.")

    for key in ("filters", "patterns"):
        if key not in data:
            raise ValueError(f"JSON에 {key} 항목이 없습니다.")

        if not isinstance(data[key], dict):
            raise ValueError(
                f"JSON의 {key} 항목은 딕셔너리여야 합니다."
            )

    return data
def parse_case_size(case_id):
    """size_N_idx 형식의 식별자에서 N을 추출한다."""
    import re

    if not isinstance(case_id, str):
        raise ValueError("케이스 식별자는 문자열이어야 합니다.")

    matched = re.fullmatch(
        r"size_([0-9]+)_([0-9]+)",
        case_id,
    )

    if matched is None:
        raise ValueError(
            f"케이스 식별자 형식이 잘못되었습니다: {case_id!r}"
        )

    size = int(matched.group(1))

    if size <= 0:
        raise ValueError("케이스 크기는 0보다 커야 합니다.")

    return size


def prepare_case(case_id, case_data, all_filters):
    """케이스와 해당 필터를 검증하고 계산용 자료를 준비한다."""
    size = parse_case_size(case_id)

    if not isinstance(case_data, dict):
        raise ValueError("패턴 항목은 딕셔너리여야 합니다.")

    for key in ("input", "expected"):
        if key not in case_data:
            raise ValueError(f"패턴에 {key} 항목이 없습니다.")

    expected = normalize_label(case_data["expected"])

    if not isinstance(all_filters, dict):
        raise ValueError("filters 항목은 딕셔너리여야 합니다.")

    filter_key = f"size_{size}"

    if filter_key not in all_filters:
        raise ValueError(f"{filter_key} 필터가 없습니다.")

    group = all_filters[filter_key]

    if not isinstance(group, dict):
        raise ValueError(
            f"{filter_key} 필터 묶음은 딕셔너리여야 합니다."
        )

    normalized_filters = {}

    for label, rows in group.items():
        standard = normalize_label(label)

        if standard in normalized_filters:
            raise ValueError(
                f"{filter_key}: {standard} 필터가 중복되었습니다."
            )

        normalized_filters[standard] = rows

    for required in ("Cross", "X"):
        if required not in normalized_filters:
            raise ValueError(
                f"{filter_key}: {required} 필터가 없습니다."
            )

    converted_filters = {}

    for label in ("Cross", "X"):
        converted_filters[label] = matrix_from_rows(
            normalized_filters[label],
            size,
            f"{filter_key}/{label}",
        )

    pattern = matrix_from_rows(
        case_data["input"],
        size,
        f"{case_id}/input",
    )

    return {
        "id": case_id,
        "size": size,
        "filters": converted_filters,
        "pattern": pattern,
        "expected": expected,
    }