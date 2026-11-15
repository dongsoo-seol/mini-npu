# 7단계. JSON 케이스별 판정과 결과 집계

## 1. 수행 목표

JSON의 각 패턴에 MAC 계산과 epsilon 판정을 적용한다.

정규화한 expected와 비교하여 PASS/FAIL을 출력하고, 전체 결과와 실패 사유를 집계한다.

## 2. 학습 목표

- 모양 판정과 PASS/FAIL의 차이를 이해한다.
- 케이스 오류를 기록하고 다음 분석을 계속한다.
- 계산 불가와 동점을 구분한다.
- 부동소수점과 epsilon이 판정에 미치는 영향을 설명한다.
- 자동 검증 결과와 원본 분석 결과를 구분한다.

## 3. 구현 내용

main.py에 다음 함수를 추가했다.

| 함수 | 역할 |
|---|---|
| analyze_case() | 케이스 하나의 검증·계산·판정·기대값 비교 |
| analyze_all_cases() | 전체 케이스 분석과 통과·실패 집계 |
| print_case_result() | 점수·판정·기대값·결과·실패 사유 출력 |
| print_summary() | 전체 집계와 실패 목록 출력 |
| run_json_mode() | 파일 읽기부터 분석·출력까지 연결 |

## 4. 케이스 처리 순서

```text
케이스 구조·크기·라벨 검증
→ Cross 점수 계산
→ X 점수 계산
→ epsilon을 적용한 판정
→ 정규화한 expected와 비교
→ PASS 또는 FAIL과 사유 반환
```

Cross 점수를 compare_scores()의 첫 번째 인수로 전달한다.
X 점수는 두 번째 인수로 전달한다.

비교 결과를 다음처럼 연결한다.

- A → Cross
- B → X
- UNDECIDED → UNDECIDED

## 5. 오류와 동점 구분

구조 검증이나 계산에 실패하면 해당 케이스를 FAIL로 기록하고 사유를 남긴다.

계산하지 못한 점수는 0으로 꾸미지 않고 None으로 보관한다.
화면에서는 계산 불가로 표시한다.

판정의 None은 계산하지 못한 상태이다.
UNDECIDED는 점수를 계산했지만 epsilon 기준으로 동점인 상태이다.

개별 케이스의 검증·계산 오류를 처리한 뒤 다음 케이스를 계속 분석한다.

파일 자체를 읽거나 해석하지 못한 경우에는 분석 불가 메시지를 출력한다.
이를 정상 분석의 0 FAIL로 표시하지 않는다.

## 6. 원본 데이터의 실제 분석 결과

실행 명령:

```powershell
python -c "from main import run_json_mode; run_json_mode()"
```

| 케이스 | Cross 점수 | X 점수 | 판정 | 기대값 | 결과 |
|---|---:|---:|---|---|---|
| size_5_1 | 0.9 | 0.8999999999999999 | UNDECIDED | X | FAIL |
| size_5_2 | 8.9 | 0.1 | Cross | Cross | PASS |
| size_13_1 | 0.3 | 14.700000000000008 | X | X | PASS |
| size_13_2 | 7.499999999999997 | 7.5 | UNDECIDED | Cross | FAIL |
| size_25_1 | 4.9 | 4.899999999999999 | UNDECIDED | X | FAIL |
| size_25_2 | 52.9 | 0.1 | Cross | Cross | PASS |

원본의 expected x와 +는 각각 X와 Cross로 정규화하여 비교했다.

## 7. 세 실패 케이스의 원인

현재 epsilon은 1e-9이다.

동점 기준:

```text
abs(Cross 점수 - X 점수) < 1e-9
```

### size_5_1

두 점수는 0.9와 0.8999999999999999이다.
차이가 epsilon보다 작아 UNDECIDED로 판정했다.
기대값은 X이므로 FAIL이다.

### size_13_2

두 점수는 7.499999999999997과 7.5이다.
차이가 epsilon보다 작아 UNDECIDED로 판정했다.
기대값은 Cross이므로 FAIL이다.
### size_25_1

두 점수는 4.9와 4.899999999999999이다.
차이가 epsilon보다 작아 UNDECIDED로 판정했다.
기대값은 X이므로 FAIL이다.

세 실패는 모두 동점 판정과 기대값의 불일치이다.
이 실행에서는 구조 오류나 계산 불가로 실패한 케이스는 없었다.

PASS 수를 늘리기 위해 원본 데이터나 epsilon을 바꾸지 않았다.

## 8. 전체 집계

실제 출력:

```text
전체 테스트 수: 6
통과 수: 3
실패 수: 3
```

전체 수 6은 통과 수 3과 실패 수 3의 합과 일치한다.

실패 목록:

```text
size_5_1: 판정 UNDECIDED와 기대값 X가 일치하지 않습니다.
size_13_2: 판정 UNDECIDED와 기대값 Cross가 일치하지 않습니다.
size_25_1: 판정 UNDECIDED와 기대값 X가 일치하지 않습니다.
```

## 9. 자동 검증

test_analysis.py에 9개 테스트를 작성했다.

| 테스트 | 확인 내용 |
|---|---|
| test_matching_labels | 정규화와 Cross/X 판정, 원본 자료 유지 |
| test_mismatch_and_tie | 기대값 불일치와 동점의 FAIL 처리 |
| test_invalid_case_continues | 크기 오류 이후 다음 케이스 처리 |
| test_invalid_case_details | 식별자·항목·필터·라벨 오류의 FAIL 집계 |
| test_file_error_no_summary | 파일 오류 안내와 가짜 정상 요약 방지 |
| test_mode_output_summary | 계산 불가 표시, 출력 순서와 집계 |
| test_mode_zero_failures | 실패 없는 경우의 집계와 없음 표시 |
| test_epsilon_in_json_analysis | 실제 MAC 점수에 epsilon 적용 |
| test_provided_data_report | 원본 6개 결과와 파일 유지 |

시험용 오류는 별도 자료와 임시 파일로 만들었다.
제공 원본을 훼손하지 않고 검사했다.

## 10. 전체 검증과 로그

실행 명령:

```powershell
python -m unittest -v test_matrix test_mac test_policies test_input test_json test_analysis
```

기존 35개와 새 분석 검사 9개를 합쳐 44개가 통과했다.

로그 파일:

```text
docs/07-analysis-test-log.txt
```

로그 저장을 위한 재실행 결과:

```text
Ran 44 tests in 0.089s

OK
```

검증 종료 코드는 0이다.
실행 시간은 환경에 따라 달라질 수 있다.

자동 검증 44개 통과와 원본 분석의 PASS 3개·FAIL 3개는 다른 결과이다.
자동 검증에서는 원본의 세 FAIL도 요구된 정책에 맞게 나오는지 확인한다.

## 11. 남은 작업

현재 JSON 모드는 케이스별 결과 후 전체 요약을 출력한다.

성능 분석 단계에서 두 출력 사이에 네 크기의 성능 표를 연결해야 한다.

아직 남은 기능:

- 크기별 최소 10회 MAC 시간 측정
- 평균 시간(ms)과 N² 표
- 사용자 입력 모드의 3×3 성능 분석
- 프로그램 시작 메뉴와 최종 실행 흐름
- 성능 결과를 포함한 최종 README 리포트

현재 테스트 실행 시간은 MAC 성능 분석값이 아니다.

## 12. 진행 상태

- [x] 케이스별 MAC 계산과 표준 라벨 판정
- [x] 정규화한 expected와 PASS/FAIL 비교
- [x] 계산 불가와 동점 상태 구분
- [x] 오류 케이스의 FAIL 처리와 다음 케이스 진행
- [x] 파일 오류 안내와 분석 불가 처리
- [x] 케이스별 결과와 실패 사유 출력
- [x] 전체 수·통과 수·실패 수 집계
- [x] 실패 식별자와 사유 목록 출력
- [x] 원본 6개 분석 결과 확인
- [x] 세 실패 케이스의 epsilon 원인 분석
- [x] 기존 기능 포함 자동 검증 44개 통과
- [x] 검증 로그 저장과 내용 확인
- [x] 7단계 수행 문서 작성
- [x] README와 요구사항 체크리스트 갱신
- [ ] 7단계 코드·검증·문서 커밋
