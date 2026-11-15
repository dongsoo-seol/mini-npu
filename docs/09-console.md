# 9단계. 시작 메뉴와 최종 실행 흐름

## 1. 수행 목표

python main.py로 프로그램을 실행하고 두 분석 모드를 선택할 수 있도록 한다.

분석 후 메뉴 복귀, 잘못된 메뉴 입력, 입력 중단과 종료를 처리한다.

## 2. 학습 목표

- 프로그램의 시작 지점을 이해한다.
- 메뉴 반복과 종료 조건을 구분한다.
- 함수 불러오기와 직접 실행의 차이를 이해한다.
- 개별 함수 검증과 실행 파일 검증을 구분한다.
- 임시 폴더에서 제출 파일의 독립 실행을 확인한다.

## 3. 구현 내용

main.py에 다음 함수를 추가했다.

| 함수 | 역할 |
|---|---|
| show_menu() | 입력 방식과 종료 메뉴 표시 |
| read_menu_choice() | 공백 제거와 메뉴 번호 검증 |
| main() | 두 모드 실행과 메뉴 반복 |

직접 실행할 때만 시작하도록 다음 조건을 추가했다.

```python
if __name__ == "__main__":
```

KeyboardInterrupt와 EOFError를 처리하여 안내 후 종료한다.

## 4. 최종 실행 방법

```powershell
python main.py
```

메뉴:

```text
=== Mini NPU 시뮬레이터 ===
1. 사용자 입력 분석 (3x3)
2. data.json 분석
0. 종료
```

분석이 끝나면 메뉴로 돌아간다.
0을 선택하면 프로그램을 종료한다.

## 5. 직접 확인한 메뉴 오류 처리

abc, 빈 입력, 9를 순서대로 입력했다.

각 경우에 다음 안내 후 재입력받았다.

```text
입력 오류: 0, 1, 2 중 하나를 입력하세요.
```

이후 2를 입력하여 JSON 분석을 정상 실행했다.

분석 후 메뉴가 다시 표시되었고 0으로 종료했다.

## 6. 직접 확인한 사용자 입력 모드

최종 실행 명령으로 프로그램을 시작하고 1을 선택했다.

입력 자료:

- 필터 A: 3×3 십자가
- 필터 B: 3×3 X
- 패턴: 3×3 십자가

확인한 순서:

```text
필터 A 입력
→ 필터 B 입력
→ 저장 내용 출력
→ 패턴 입력
→ 점수와 판정
→ 3×3 성능 표
→ 메뉴 복귀
→ 0으로 종료
```

실제 결과:

```text
필터 A MAC 점수: 5
필터 B MAC 점수: 1
판정 결과: A
```

해당 실행의 성능 출력:

```text
3x3 | 0.017100 | 9 | 10 | 사용자 입력 패턴 / 필터 A
```

시간 단위는 ms이며, 이 값은 해당 실행 시점의 기록이다.
공통 측정용 배열의 성능 표와 입력 조건이 다르다.

## 7. 직접 확인한 JSON 모드

최종 실행 명령으로 프로그램을 시작하고 2를 선택했다.

확인한 순서:

```text
필터와 패턴 읽기·검증
→ 케이스별 점수·판정·PASS/FAIL
→ 네 크기의 성능 표
→ 전체 집계
→ 실패 목록
→ 메뉴 복귀
→ 0으로 종료
```

원본 분석 결과:

```text
전체 테스트 수: 6
통과 수: 3
실패 수: 3
```

실패 케이스:

- size_5_1
- size_13_2
- size_25_1

세 케이스 모두 epsilon에 따른 UNDECIDED와 기대값이 달라 FAIL이었다.

실행 때마다 시간이 달라질 수 있으며, 문서의 기준 성능 표는 docs/08-performance-results.json에 저장한 측정값을 사용한다.

## 8. 실행 파일 자동 검증

test_console.py에 10개 테스트를 작성했다.

| 테스트 | 확인 내용 |
|---|---|
| test_menu_validation_and_exit | 잘못된 메뉴 입력과 정상 종료 |
| test_manual_mode | 사용자 모드 전체 흐름 |
| test_json_mode | JSON 결과·성능·요약 순서와 원본 유지 |
| test_manual_input_errors | 실행 파일에서 행 재입력 |
| test_invalid_case_continues | 오류 케이스 이후 분석 계속 |
| test_json_file_errors | 파일 오류 안내와 메뉴 복귀 |
| test_eof_exit | 메뉴·분석 중 입력 종료 |
| test_keyboard_interrupt_exit | 모의 KeyboardInterrupt 처리 |
| test_other_working_directory | 다른 작업 위치에서도 JSON 읽기 |
| test_import_without_menu | import 시 메뉴가 시작되지 않음 |

임시 폴더에 main.py와 data.json만 복사하여 별도 Python 프로세스로 실행했다.

제공 원본을 직접 손상시키지 않고 복사본으로 오류 상황을 검증했다.

KeyboardInterrupt는 자동 검사에서 모의한 것이다.
실제 키보드의 Ctrl+C 조작을 직접 확인한 것으로 기록하지 않는다.

## 9. 전체 자동 검증과 로그

실행 명령:

```powershell
python -m unittest -v test_matrix test_mac test_policies test_input test_json test_analysis test_performance test_console
```

기존 52개와 새 실행 검사 10개를 합쳐 62개가 통과했다.

로그 파일:

```text
docs/09-console-test-log.txt
```

로그 저장을 위한 재실행 결과:

```text
Ran 62 tests in 2.222s

OK
```

검증 종료 코드는 0이다.

자동 검증 62개 통과, 원본 분석 PASS 3개·FAIL 3개, MAC 평균 시간은 서로 다른 결과이다.

## 10. 남은 작업

- README의 실행 방법과 현재 상태 갱신
- 요구사항 체크리스트 최종 대조
- 단계별 기록과 최종 제출 설명 구분
- 제출 파일과 재현 절차 최종 확인

## 11. 진행 상태

- [x] python main.py 시작 메뉴 구현
- [x] 잘못된 메뉴 입력 재입력
- [x] 두 모드 선택과 메뉴 복귀
- [x] 정상 종료 직접 확인
- [x] 사용자 모드 최종 실행 직접 확인
- [x] JSON 모드 최종 실행 직접 확인
- [x] EOF와 모의 KeyboardInterrupt 자동 검증
- [x] 다른 작업 위치에서 실행 검증
- [x] import 시 메뉴 미실행 검증
- [x] 기존 기능 포함 자동 검증 62개 통과
- [x] 검증 로그 저장과 내용 확인
- [x] 9단계 수행 문서 작성
- [x] README와 요구사항 체크리스트 갱신
- [ ] 9단계 코드·검증·문서 커밋