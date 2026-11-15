# 6단계. JSON 로드와 구조·크기 검증

## 1. 수행 목표

data.json을 읽고 케이스 식별자에서 배열 크기를 추출한다.

해당 크기의 필터와 패턴을 검증하여 MAC 계산에 사용할 Matrix 객체로 준비한다.

## 2. 학습 목표

- JSON의 딕셔너리와 리스트 구조를 이해한다.
- 파일 읽기 오류와 개별 케이스 오류를 구분한다.
- 식별자에서 크기를 추출한다.
- 외부 배열의 행·열 개수와 숫자 값을 검증한다.
- 원본을 변경하지 않고 계산용 자료를 만든다.

## 3. 확인한 원본 구조

최상위 항목:

```text
meta
filters
patterns
```

filters와 patterns는 딕셔너리이다.

크기별 필터:

| 크기 키 | 필터 키 | 배열 자료형 |
|---|---|---|
| size_5 | cross, x | list |
| size_13 | cross, x | list |
| size_25 | cross, x | list |

패턴은 6개이며, 각 항목에 input과 expected가 있다.

| 케이스 | 원본 expected | 정규화한 라벨 |
|---|---|---|
| size_5_1 | x | X |
| size_5_2 | + | Cross |
| size_13_1 | x | X |
| size_13_2 | + | Cross |
| size_25_1 | x | X |
| size_25_2 | + | Cross |

이 표는 기대값의 표현을 정리한 것이며 실제 판정 결과는 아니다.

## 4. 구현한 함수

main.py에 다음 함수를 추가했다.

| 함수 | 역할 |
|---|---|
| matrix_from_rows() | 외부 배열의 구조·값을 검사하고 Matrix로 변환 |
| load_json_data() | JSON 파일 읽기와 최상위 구조 확인 |
| parse_case_size() | size_N_idx 식별자에서 N 추출 |
| prepare_case() | 해당 케이스와 필터를 검증하고 계산용 자료 준비 |

## 5. 배열 변환과 검증

matrix_from_rows()는 다음 순서로 처리한다.

1. 지정한 크기가 양의 정수인지 확인한다.
2. 전체 배열이 리스트인지 확인한다.
3. 행 수가 N인지 확인한다.
4. 각 행이 리스트이고 열 수가 N인지 확인한다.
5. Matrix 객체를 생성한다.
6. 각 값을 검사하여 저장한다.
7. 완성된 Matrix를 반환한다.

잘못된 값은 자료 이름과 행·열 위치를 포함하여 오류로 알린다.

문자열, bool, NaN과 무한대는 숫자 원소로 허용하지 않는다.

변환한 Matrix를 수정해도 원본 리스트는 바뀌지 않도록 구성했다.

## 6. JSON 파일 읽기

기본 경로는 main.py와 같은 폴더의 data.json이다.

UTF-8 BOM이 있는 파일도 읽을 수 있도록 utf-8-sig를 사용했다.

파일 읽기 실패, 문자 해석 실패, JSON 문법 오류는 원인을 포함한 ValueError로 전달한다.

읽은 자료에서 다음 사항을 확인한다.

- 최상위 자료가 딕셔너리인지
- filters와 patterns가 존재하는지
- 두 항목이 딕셔너리인지

프로그램 전체의 오류 안내는 이후 실행 흐름에서 연결한다.

## 7. 케이스 크기와 필터 선택

parse_case_size()는 size_N_idx 형식을 확인한다.

예:

```text
size_13_1 → N은 13 → size_13 필터 선택
```

크기가 0 이하이거나 식별자 형식이 다르면 오류로 처리한다.

prepare_case()에서는 다음을 확인한다.

- 패턴 항목의 input과 expected 존재
- expected 라벨 정규화
- 해당 크기의 필터 묶음 존재
- 필터 키의 Cross/X 정규화
- 정규화 후 필터 이름 중복 여부
- Cross와 X 필터 모두 존재
- 필터와 패턴이 지정된 N×N 크기인지
- 배열 원소가 유효한 숫자인지

## 8. 실제 파일로 확인한 결과

원본 JSON을 새 함수로 읽은 결과:

```text
필터 크기: ['size_5', 'size_13', 'size_25']
패턴 수: 6
최상위 항목: ['meta', 'filters', 'patterns']
```

size_5의 cross 필터를 Matrix로 변환한 결과:

```text
변환된 자료형: Matrix
배열 크기: 5
첫 행: [0.0, 0.0, 1.0, 0.0, 0.0]
```

size_5_1을 prepare_case()로 준비한 결과:

```text
케이스: size_5_1
크기: 5
표준 필터 이름: ['Cross', 'X']
정규화한 기대값: X
패턴 자료형: Matrix
```

## 9. 자동 검증

test_json.py에 8개 테스트를 작성했다.

| 테스트 | 확인 내용 |
|---|---|
| test_matrix_conversion | 정상 변환과 원본 리스트의 독립성 |
| test_invalid_matrix_data | 행·열·자료형·숫자 오류와 위치 메시지 |
| test_case_identifier | 크기 추출과 잘못된 식별자 거절 |
| test_load_valid_json | BOM 포함 JSON 읽기와 파일 원본 유지 |
| test_load_errors | 파일 없음·손상·인코딩·최상위 구조 오류 |
| test_prepare_valid_sizes | 크기별 필터 선택과 원본 자료 유지 |
| test_invalid_patterns | 항목 누락·기대 라벨·패턴 크기 오류 |
| test_invalid_filters | 필터 누락·크기·이름·중복 오류 |

자동 검증은 임시 파일과 시험용 자료를 사용한다.
제공된 data.json을 수정하여 오류를 만드는 방식으로 검사하지 않았다.

## 10. 전체 검증 로그

실행 명령:

```powershell
python -m unittest -v test_matrix test_mac test_policies test_input test_json
```

기존 27개와 JSON 검사 8개를 합쳐 35개 테스트가 통과했다.

로그 파일:

```text
docs/06-json-test-log.txt
```

로그 저장을 위한 재실행 결과:

```text
Ran 35 tests in 0.050s

OK
```

검증 종료 코드는 0이다.
실행 시간은 환경과 반복 실행에 따라 달라질 수 있다.

## 11. 현재 구현 범위

JSON을 읽고 검증된 계산용 자료를 준비하는 기능까지 구현했다.

현재 함수는 검증 실패를 예외로 전달한다.
이를 케이스별 FAIL로 기록하고 다음 케이스를 계속 분석하는 기능은 7단계에서 연결한다.

원본 6개 패턴 전체의 MAC 점수와 PASS/FAIL은 아직 확인하지 않았다.

자동 검증 35개 통과와 원본 JSON 분석의 6개 케이스 결과는 서로 다른 확인 항목이다.

## 12. 진행 상태

- [x] 원본 필터 자료형과 expected 표현 확인
- [x] 외부 배열의 구조·숫자 검증과 Matrix 변환
- [x] JSON 읽기와 최상위 구조 확인
- [x] 케이스 식별자에서 크기 추출
- [x] 해당 크기의 필터 선택
- [x] 라벨 정규화와 필터 누락·중복 검사
- [x] 실제 size_5_1의 계산용 자료 준비 확인
- [x] 오류 상황과 원본 유지 자동 검증
- [x] 기존 기능 포함 자동 검증 35개 통과
- [x] 검증 로그 저장과 내용 확인
- [x] 6단계 수행 문서 작성
- [x] README와 요구사항 체크리스트 갱신
- [ ] 6단계 코드·검증·문서 커밋
6단계 구현 커밋: 7f2cef8
커밋 메시지: Feat: JSON 로드와 구조 크기 검증 구현