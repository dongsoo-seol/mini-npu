# 1단계. 요구사항과 개발 환경 준비

## 1. 수행 목표

미션 2와 디스코드 봇 작업에서 분리된 공간에 미션 3 프로젝트를 준비한다.

Python과 Git의 실행을 확인하고, 초기 파일과 요구사항 문서를 준비한다.

## 2. 학습 목표

- 작업 폴더와 현재 위치의 의미를 이해한다.
- Python 실행 환경을 확인할 수 있다.
- 표준 라이브러리와 외부 라이브러리를 구분한다.
- Git이 변경 이력을 관리하는 도구임을 이해한다.
- 실제 수행 결과와 앞으로 할 작업을 구분하여 기록한다.

## 3. 확인한 개발 환경

| 항목 | 확인 결과 |
|---|---|
| 명령 실행 환경 | Windows PowerShell |
| Python | 3.12.10 |
| Git | 2.56.0.windows.4 |
| 프로젝트 위치 | C:\Users\User\mini-npu |
| 과제의 Python 조건 | Python 3.8 이상 |
| 외부 라이브러리 | 사용 금지 |

Python 3.12.10은 과제의 Python 버전 조건을 충족한다.
## 4. Git 설치와 실행 경로 문제 해결

처음에는 git 명령을 실행할 수 없었다.

설치 기록을 확인했다.

```powershell
winget list --id Git.Git -e --source winget
```

결과:

```text
입력 조건과 일치하는 설치된 패키지를 찾을 수 없습니다.
```

다음 명령으로 Git을 설치했다.

```powershell
winget install --id Git.Git -e --source winget
```

설치 성공 후에도 git 명령을 찾지 못하여 실행 파일의 존재를 확인했다.

```powershell
Test-Path "C:\Program Files\Git\cmd\git.exe"
```

결과:

```text
True
```

실행 파일을 직접 지정하여 확인했다.

```powershell
& "C:\Program Files\Git\cmd\git.exe" --version
```

결과:

```text
git version 2.56.0.windows.4
```

현재 PowerShell의 PATH에 Git 경로를 추가한 뒤, 기존 사용자 PATH를 유지하면서 사용자 환경 변수에도 저장했다.

새 PowerShell 창에서 다음 명령이 정상 실행되는 것을 확인했다.

```powershell
git --version
```

결과:

```text
git version 2.56.0.windows.4
```

Git 설치와 실행 경로 연결을 완료했다.

## 5. 작업 폴더 준비

기존 폴더가 있는지 확인했다.

```powershell
Test-Path "$HOME\mini-npu"
```

결과:

```text
False
```

새 폴더를 만들고 이동했다.

```powershell
mkdir "$HOME\mini-npu"
cd "$HOME\mini-npu"
Get-Location
```

확인한 위치:

```text
C:\Users\User\mini-npu
```

## 6. Python 실행 확인

```powershell
python --version
```

결과:

```text
Python 3.12.10
```

실제 코드 실행도 확인했다.

```powershell
python -c "print('Mini NPU 준비 완료')"
```

결과:

```text
Mini NPU 준비 완료
```
## 7. 초기 파일 준비

### .gitignore

Python 자동 생성 파일 등을 Git 관리 대상에서 제외하도록 작성했다.

```text
__pycache__/
*.py[cod]
.venv/
venv/
```

처음에는 여러 줄 명령이 역순으로 입력되어 파일이 생성되지 않았다.

한 줄 명령으로 다시 작성하고 Get-Content로 내용을 확인했다.

data.json은 분석에 필요한 자료이므로 제외 목록에 넣지 않았다.

### README.md

다음 내용을 초기 README에 작성했다.

- 프로젝트 개요와 개발 환경
- 구현 예정 기능
- 라벨 정규화와 epsilon 판정 계획
- 성능 측정 계획
- 실행 방법과 데이터 파일 배치 계획
- 결과 리포트 작성 기준
- 현재 진행 상태

아직 구현하지 않은 기능은 완료로 표시하지 않았다.

## 8. 사용할 표준 라이브러리

| 라이브러리 | 사용 목적 |
|---|---|
| json | JSON 데이터 읽기 |
| pathlib | 파일 경로 관리 |
| time | 연산 시간 측정 |
| unittest | 자동 검증 |
| re | 케이스 식별자 해석 |

외부 라이브러리는 설치하지 않고, MAC 연산은 반복문으로 직접 구현한다.
## 9. 현재 파일 구조

```text
mini-npu/
├─ .gitignore
├─ README.md
└─ docs/
   └─ 01-setup.md
```

## 10. 진행 상태

- [x] Git 설치와 실행 확인
- [x] Git 사용자 PATH 설정과 새 창 실행 확인
- [x] 별도 프로젝트 폴더 준비
- [x] Python 버전과 코드 실행 확인
- [x] .gitignore 작성과 내용 확인
- [x] 초기 README 작성과 앞부분 확인
- [x] 환경 기록 문서 작성
- [x] 요구사항 체크리스트 작성
- [x] 제공된 data.json 확보와 구조 확인
- [ ] Git 저장소 초기화
- [ ] 첫 커밋

미완료 항목은 실제 수행하고 결과를 확인한 뒤 갱신한다.
## 11. 요구사항 체크리스트와 데이터 준비

docs/requirements-checklist.md를 작성했다.

다운로드 폴더에서 data.json을 찾아 프로젝트 폴더로 복사했다.
다운로드 폴더의 원본은 그대로 유지했다.

프로젝트의 data.json을 읽어 JSON 문법과 기본 구조를 확인했다.

확인 결과:

- 최상위 자료형: dict
- 최상위 키: meta, filters, patterns
- filters 자료형: dict
- 필터 크기 키: size_5, size_13, size_25
- 각 크기의 필터 키: cross, x
- patterns 자료형: dict
- 패턴 수: 6개
- 첫 패턴의 항목: input, expected

패턴 식별자:

```text
size_5_1
size_5_2
size_13_1
size_13_2
size_25_1
size_25_2
```

현재 확인한 것은 파일 읽기와 기본 구조이다.
전체 패턴의 필수 항목, 배열 크기, 숫자 값과 라벨 검증은 이후 구현 단계에서 수행한다.
MAC 계산 결과와 PASS/FAIL도 아직 확인하지 않았다.
