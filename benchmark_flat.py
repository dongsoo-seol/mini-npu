"""동일 자료로 기존 MAC과 1차원 MAC의 성능을 비교한다."""

import json
import math
from pathlib import Path
from time import perf_counter

from main import Matrix, mac_score
from flat_mac import FlatMatrix, mac_score_flat


def mac_score_direct(pattern, filter_data):
    """메서드 호출을 줄인 2차원 직접 접근 비교용 구현."""
    if not isinstance(pattern, Matrix):
        raise TypeError("입력 패턴은 Matrix 객체여야 합니다.")
    if not isinstance(filter_data, Matrix):
        raise TypeError("필터는 Matrix 객체여야 합니다.")
    if pattern.size != filter_data.size:
        raise ValueError("패턴과 필터의 크기가 일치해야 합니다.")

    total = 0
    for row in range(pattern.size):
        pattern_row = pattern.data[row]
        filter_row = filter_data.data[row]
        for col in range(pattern.size):
            total += pattern_row[col] * filter_row[col]

    if type(total) is float and not math.isfinite(total):
        raise ValueError("MAC 계산 결과가 유한하지 않습니다.")
    return total


def benchmark(size, repeats=100, rounds=5):
    pattern = Matrix(size)
    filter_data = Matrix(size)

    for row in range(size):
        for col in range(size):
            pattern.set_value(row, col, 1.0)
            filter_data.set_value(row, col, 1.0)

    flat_pattern = FlatMatrix(pattern)
    flat_filter = FlatMatrix(filter_data)

    methods = [
        ("original", mac_score, pattern, filter_data),
        ("direct_2d", mac_score_direct, pattern, filter_data),
        ("flat_1d", mac_score_flat, flat_pattern, flat_filter),
    ]

    # 正確性の確認と準備実行は計測から除外する。
    for name, function, first, second in methods:
        score = function(first, second)
        if score != size * size:
            raise AssertionError(f"{name}: 計算結果が一致しません。")

    elapsed = {name: 0.0 for name, _, _, _ in methods}

    for round_index in range(rounds):
        for iteration in range(repeats):
            # 順番を入れ替え、同じ方式が常に先にならないようにする。
            shift = (round_index + iteration) % len(methods)
            order = methods[shift:] + methods[:shift]

            for name, function, first, second in order:
                started = perf_counter()
                function(first, second)
                elapsed[name] += perf_counter() - started

    samples = repeats * rounds
    averages = {
        name: seconds * 1000 / samples
        for name, seconds in elapsed.items()
    }

    # 入力とフィルターの両方の変換時間を別に測定する。
    conversion_elapsed = 0.0
    for _ in range(samples):
        started = perf_counter()
        converted_pattern = FlatMatrix(pattern)
        converted_filter = FlatMatrix(filter_data)
        conversion_elapsed += perf_counter() - started

        # 検査と変換結果の解放は計測区間の外で行う。
        assert len(converted_pattern.data) == size * size
        assert len(converted_filter.data) == size * size
        del converted_pattern, converted_filter

    return {
        "size": size,
        "operations": size * size,
        "repeats_per_round": repeats,
        "rounds": rounds,
        "samples_per_method": samples,
        "original_ms": averages["original"],
        "direct_2d_ms": averages["direct_2d"],
        "flat_1d_ms": averages["flat_1d"],
        "conversion_pair_ms": conversion_elapsed * 1000 / samples,
        "original_to_flat_ratio": (
            averages["original"] / averages["flat_1d"]
            if averages["flat_1d"] > 0 else None
        ),
    }


def main():
    results = [benchmark(size) for size in (3, 5, 13, 25)]

    output = Path(__file__).resolve().parent / "docs"
    output.mkdir(exist_ok=True)
    destination = output / "bonus-flat-performance.json"

    report = {
        "data": "全要素が1.0の同一入力・同一フィルター",
        "timing": "変換・入出力を除くMAC関数呼び出し時間",
        "results": results,
    }
    destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("크기 | 기존(ms) | 직접2차원(ms) | 1차원(ms) | 변환2개(ms)")
    for result in results:
        print(
            f"{result['size']}x{result['size']} | "
            f"{result['original_ms']:.6f} | "
            f"{result['direct_2d_ms']:.6f} | "
            f"{result['flat_1d_ms']:.6f} | "
            f"{result['conversion_pair_ms']:.6f}"
        )

    print("각 방식: 준비 실행 제외, 100회 × 5묶음 = 500회 평균")
    print("저장 위치:", destination)


if __name__ == "__main__":
    main()