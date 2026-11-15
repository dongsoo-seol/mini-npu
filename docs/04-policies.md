# 4단계. 라벨 정규화와 epsilon 판정

## 1. 수행 목표

같은 의미의 라벨을 Cross와 X로 통일한다.

점수 비교에 허용오차를 적용하여 근소한 차이를 동점으로 처리한다.

## 2. 학습 목표

- 원본 표현과 표준 라벨을 구분한다.
- 문자열의 공백과 대소문자를 처리한다.
- 딕셔너리로 별칭과 표준값을 연결한다.
- epsilon 기반 비교와 경계 조건을 이해한다.
- 모양 라벨과 판정 보류 상태를 구분한다.

## 3. 구현 내용

main.py에 다음 항목을 추가했다.

| 항목 | 역할 |
|---|---|
| normalize_label() | 원본 표현을 Cross 또는 X로 변환 |
| EPSILON | 기본 허용오차 1e-9 |
| compare_scores() | A/B/UNDECIDED 반환 |

기존 Matrix 클래스와 mac_score()는 유지했다.

## 4. 라벨 정규화

처리 순서:

1. 문자열인지 확인한다.
2. strip()으로 앞뒤 공백을 제거한다.
3. casefold()로 대소문자 차이를 줄인다.
4. 별칭 딕셔너리에서 표준 라벨을 찾는다.
5. 알 수 없는 라벨은 오류로 알린다.

직접 실행하여 확인한 결과:

```text
'+' -> Cross
'cross' -> Cross
'Cross' -> Cross
'x' -> X
'X' -> X
' cross ' -> Cross
```

UNDECIDED는 모양의 이름이 아니라 판정 보류 상태이다.
따라서 normalize_label()에서 정상 모양 라벨로 받아들이지 않는다.

## 5. epsilon 비교 정책

기본값:

```python
EPSILON = 1e-9
```

동점 조건:

```python
abs(score_a - score_b) < epsilon
```

동점이면 UNDECIDED를 반환한다.
동점이 아니면 높은 점수에 따라 A 또는 B를 반환한다.

차이가 epsilon과 같으면 이번 정책에서는 동점이 아니다.

직접 확인한 결과:

| A 점수 | B 점수 | 결과 |
|---|---|---|
| 5 | 1 | A |
| 1 | 5 | B |
| 1 | 1 | UNDECIDED |
| 0 | 5e-10 | UNDECIDED |
| 0 | 1e-9 | B |

경계 검증에서는 0과 EPSILON을 사용하여 비교 기준을 확인했다.

## 6. 잘못된 값 처리

compare_scores()는 다음 조건을 확인한다.

- 점수와 epsilon은 정수 또는 실수여야 한다.
- bool은 숫자 인수로 받아들이지 않는다.
- NaN과 양·음의 무한대는 허용하지 않는다.
- epsilon은 0보다 커야 한다.

기본 epsilon 외에 다른 양의 유한한 epsilon을 전달할 수도 있다.

## 7. 모드별 결과 연결 계획

현재 compare_scores()는 공통 비교 결과만 반환한다.

사용자 입력 모드:

- A → A
- B → B
- UNDECIDED → 판정 불가

JSON 모드:

- Cross 필터 점수를 첫 번째 인수로 전달한다.
- X 필터 점수를 두 번째 인수로 전달한다.
- A → Cross
- B → X
- UNDECIDED → UNDECIDED

사용자가 입력하는 필터 A가 반드시 십자가라고 가정하지 않는다.
JSON 모드에서는 표준 라벨을 기준으로 필터와 비교 결과를 연결한다.

모드별 출력과 expected 비교는 후속 단계에서 구현한다.

## 8. 자동 검증

test_policies.py에 8개 테스트를 작성했다.

| 테스트 | 확인 내용 |
|---|---|
| test_label_normalization | 별칭, 공백, 대소문자와 표준값 재변환 |
| test_invalid_labels | 알 수 없는 라벨과 잘못된 자료형 |
| test_larger_score | 양수·음수 점수의 우세 판정 |
| test_ties | 같은 점수와 epsilon 미만의 차이 |
| test_epsilon_boundary | epsilon 경계와 그 이상의 차이 |
| test_custom_epsilon | 전달한 허용오차 적용 |
| test_invalid_scores | 잘못된 점수 자료형과 유한하지 않은 값 |
| test_invalid_epsilon | 잘못된 자료형, 0, 음수, 유한하지 않은 값 |

실행 명령:

```powershell
python -m unittest -v test_matrix test_mac test_policies
```

기존 배열 5개, MAC 7개, 정책 8개를 합쳐 20개 테스트가 통과했다.

## 9. 검증 로그

로그 파일:

```text
docs/04-policy-test-log.txt
```

로그 저장을 위한 재실행 결과:

```text
Ran 20 tests in 0.006s

OK
```

검증 종료 코드는 0이다.
테스트 실행 시간은 환경에 따라 달라지며 MAC 성능 측정값과는 다르다.

## 10. 현재 구현 범위

라벨 정규화와 점수 비교 함수를 구현하고 검증했다.

실제 data.json의 각 케이스에 적용한 결과는 아직 확인하지 않았다.
따라서 현재 테스트 통과를 JSON 분석의 전체 PASS로 해석하지 않는다.

사용자 입력, JSON 검증·분석, 성능 측정과 최종 결과 요약은 후속 단계에서 연결한다.

## 11. 진행 상태

- [x] 라벨 정규화 함수 구현
- [x] 필수 별칭과 공백·대소문자 처리 검증
- [x] 알 수 없는 라벨 거절 검증
- [x] epsilon 점수 비교 구현
- [x] 정확한 동점과 근소한 차이 검증
- [x] epsilon 경계와 사용자 지정값 검증
- [x] 잘못된 점수와 epsilon 거절 검증
- [x] 기존 기능 포함 자동 검증 20개 통과
- [x] 검증 로그 저장과 내용 확인
- [x] 4단계 수행 문서 작성
- [x] README와 요구사항 체크리스트 갱신
- [x] 4단계 코드·검증·문서 커밋
4단계 구현 커밋: d7ffd6d
커밋 메시지: Feat: 라벨 정규화와 epsilon 점수 판정 구현