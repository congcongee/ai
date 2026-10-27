# ConnecJob 웹 (1차 초안)

경험을 공고에 연결하는 취업 매칭 서비스. 발표 자료 「커넥잡 발표 시안」의 색·글꼴·화면 구성을 그대로 웹으로 옮김.

## 실행
```bash
pip install -r requirements.txt
flask run --debug        # 또는 python app.py → http://127.0.0.1:5000
```
테스트 계정 : `hong` / `1234`

## 화면
| URL | 화면 | 사용한 수업 내용 |
|---|---|---|
| `/` | 메인 (표지·목표·시나리오) | 시멘틱 태그, CSS 선택자, 반응형(@media), setInterval |
| `/join`, `/login` | 회원가입·로그인 | form, 정규표현식 유효성검사, fetch(keyup) 아이디 중복확인, session |
| `/exps` | 내 경험 입력·목록 | Flask CRUD, PUT/DELETE fetch(JSON), 문서객체 생성 |
| `/results` | 공고 추천 + 근거 | Jinja2 for/if/include, 필터(select onchange) |
| `/roadmap` | 부족 기술 준비 로드맵 | 표, setTimeout 애니메이션 |
| `/cover-letter/<id>` | 자소서 초안 (문장별 출처 경험) | |
| `/jobs`, `/jobs/<id>` | 공고 목록·원문 | 404 errorhandler |
| `/api/recommend` | 추천 JSON | jsonify |

## 1차 초안의 한계 → 다음 단계
- 데이터는 `repository.py` 딕셔너리(메모리) → 서버 재시작 시 초기화. 공고 8건은 모두 **예시 데이터**
- 추천은 **기술 키워드 일치 규칙**(기술 일치율 70% + 직무 일치 30%) → 임베딩 + 벡터DB(Chroma) + LLM(RAG)로 교체 예정
- 자소서는 규칙 기반 문장 → LLM 생성 + 출처 경험 ID 유지
- 회원/경험 저장 → SQLite 또는 MySQL (10_flask ch5·ch6 방식)
