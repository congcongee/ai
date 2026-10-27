from typing import List, Optional  # 타입 힌트용
from werkzeug.security import generate_password_hash, check_password_hash  # 비밀번호 암호화(Flask 설치 시 함께 설치됨)

# ------------------------------------------------------------------
# 1차 초안 : DB 대신 딕셔너리(메모리)에 저장 → 서버를 끄면 초기화됨
# 이후 단계 : 회원/경험은 SQLite(MySQL), 공고는 벡터DB(Chroma)로 교체
# ------------------------------------------------------------------

# 채용공고 샘플 (회사명·내용은 모두 예시 데이터)
job_data = {
  1:{'id':1, 'company':'가나전자(예시)', 'size':'대기업', 'job':'백엔드',
     'title':'커머스 플랫폼 백엔드 개발자',
     'skills':['Python', 'Django', 'MySQL', 'Docker', 'AWS'],
     'duties':'주문·결제 API 설계 및 개발, 대용량 트래픽 처리',
     'requirements':'Python 웹 프레임워크(Django/Flask) 개발 경험, RDBMS 설계 경험',
     'preferred':'Docker 기반 배포 경험, AWS 운영 경험',
     'deadline':'2026-11-30',
     'questions':['지원 동기와 입사 후 포부', '가장 도전적이었던 프로젝트 경험']},
  2:{'id':2, 'company':'다라소프트(예시)', 'size':'중견', 'job':'백엔드',
     'title':'사내 업무 시스템 웹 개발자',
     'skills':['Python', 'Flask', 'Oracle', 'JavaScript', 'Git'],
     'duties':'사내 그룹웨어 기능 개발 및 유지보수',
     'requirements':'Flask 또는 Django 개발 경험, SQL 작성 능력',
     'preferred':'Oracle 사용 경험, 협업 툴(Git) 사용 경험',
     'deadline':'2026-11-20',
     'questions':['협업 중 갈등을 해결한 경험', '본인의 강점과 직무 연관성']},
  3:{'id':3, 'company':'Global Tech Korea(예시)', 'size':'외국계', 'job':'백엔드',
     'title':'Backend Engineer (Python)',
     'skills':['Python', 'FastAPI', 'Docker', 'Kubernetes', 'English'],
     'duties':'Microservice API development, CI/CD pipeline 운영',
     'requirements':'Python 기반 API 개발 경험, 영어 커뮤니케이션 가능자',
     'preferred':'Kubernetes 운영 경험',
     'deadline':'2026-12-05',
     'questions':['Why do you want to join us?', '기술적 문제를 해결한 경험']},
  4:{'id':4, 'company':'마바금융(예시)', 'size':'대기업', 'job':'데이터',
     'title':'데이터 분석가',
     'skills':['Python', 'SQL', 'Pandas', 'Tableau', '통계'],
     'duties':'고객 데이터 분석 및 대시보드 구축',
     'requirements':'SQL·Pandas를 활용한 데이터 분석 경험',
     'preferred':'통계 지식, 시각화 툴(Tableau) 사용 경험',
     'deadline':'2026-11-25',
     'questions':['데이터로 문제를 해결한 경험', '지원 동기']},
  5:{'id':5, 'company':'사아물류(예시)', 'size':'중견', 'job':'데이터',
     'title':'물류 수요예측 데이터 엔지니어',
     'skills':['Python', 'SQL', 'scikit-learn', 'Airflow', 'Docker'],
     'duties':'수요예측 모델 데이터 파이프라인 구축',
     'requirements':'Python 데이터 처리 경험, 머신러닝 기초',
     'preferred':'Airflow·Docker 사용 경험',
     'deadline':'2026-12-10',
     'questions':['가장 자신 있는 프로젝트', '입사 후 목표']},
  6:{'id':6, 'company':'자차AI랩(예시)', 'size':'중견', 'job':'AI',
     'title':'LLM 서비스 개발자',
     'skills':['Python', 'LangChain', 'RAG', 'PyTorch', 'Flask'],
     'duties':'RAG 기반 챗봇 및 문서 검색 서비스 개발',
     'requirements':'LLM API 활용 경험, 벡터DB 사용 경험',
     'preferred':'PyTorch 모델 학습 경험, 웹 서비스 배포 경험',
     'deadline':'2026-11-28',
     'questions':['AI 서비스를 만들어 본 경험', '지원 동기와 포부']},
  7:{'id':7, 'company':'카타모빌리티(예시)', 'size':'대기업', 'job':'AI',
     'title':'머신러닝 엔지니어',
     'skills':['Python', 'PyTorch', 'scikit-learn', 'Docker', 'AWS'],
     'duties':'예측 모델 개발 및 서빙',
     'requirements':'머신러닝/딥러닝 모델 개발 경험',
     'preferred':'모델 서빙(Docker, AWS) 경험',
     'deadline':'2026-12-01',
     'questions':['모델 성능을 개선한 경험', '입사 후 포부']},
  8:{'id':8, 'company':'Pacific Data(예시)', 'size':'외국계', 'job':'데이터',
     'title':'Data Analyst',
     'skills':['SQL', 'Python', 'Tableau', 'English', '통계'],
     'duties':'Business KPI 분석, 리포트 작성',
     'requirements':'SQL 능숙, 영어 리포트 작성 가능',
     'preferred':'Tableau 대시보드 경험',
     'deadline':'2026-11-22',
     'questions':['Describe a data project you led', '지원 동기']},
}

# 기술명 정규화 사전 (예: 파이썬 → Python)
skill_dict = {
  '파이썬':'Python', 'python':'Python', '장고':'Django', 'django':'Django',
  '플라스크':'Flask', 'flask':'Flask', 'mysql':'MySQL', '오라클':'Oracle',
  'oracle':'Oracle', '도커':'Docker', 'docker':'Docker', 'aws':'AWS',
  '자바스크립트':'JavaScript', 'js':'JavaScript', 'javascript':'JavaScript',
  'git':'Git', '깃':'Git', 'sql':'SQL', 'pandas':'Pandas', '판다스':'Pandas',
  'sklearn':'scikit-learn', 'scikit-learn':'scikit-learn', '사이킷런':'scikit-learn',
  'pytorch':'PyTorch', '파이토치':'PyTorch', 'langchain':'LangChain', '랭체인':'LangChain',
  'rag':'RAG', 'fastapi':'FastAPI', 'kubernetes':'Kubernetes', 'k8s':'Kubernetes',
  'tableau':'Tableau', '태블로':'Tableau', 'airflow':'Airflow', '영어':'English',
  'english':'English', '통계':'통계',
}

# 회원 (비밀번호는 해시로 저장)
member_data = {
  'hong':{'id':'hong', 'name':'홍길동', 'pw':generate_password_hash('1234')},
}

# 사용자 경험 : {회원id : {경험id : 경험}}
exp_data = {
  'hong':{
    1:{'id':1, 'title':'따릉이 수요예측 프로젝트', 'skills':['Python', 'Pandas', 'scikit-learn'],
       'content':'서울시 따릉이 대여 데이터를 분석해 시간대별 수요를 예측하는 회귀 모델을 만들었다.'},
    2:{'id':2, 'title':'Flask To-Do 웹 서비스', 'skills':['Python', 'Flask', 'JavaScript', 'Git'],
       'content':'Flask와 Jinja2로 할 일 관리 웹을 만들고 fetch로 수정·삭제 기능을 구현해 Vercel에 배포했다.'},
  }
}

# ---------------------------- 회원 ----------------------------
def id_exists(id:str) -> bool:
  '아이디 중복 여부'
  return id in member_data

def join_member(member:dict) -> bool:
  '회원가입 (성공시 True)'
  if id_exists(member['id']):
    return False
  member_data[member['id']] = {'id':member['id'], 'name':member['name'],
                               'pw':generate_password_hash(member['pw'])}
  exp_data[member['id']] = {}
  return True

def login_check(id:str, pw:str) -> Optional[dict]:
  '로그인 성공시 회원정보(비밀번호 제외) 반환, 실패시 None'
  member = member_data.get(id)
  if member and check_password_hash(member['pw'], pw):
    return {'id':member['id'], 'name':member['name']}
  return None

# ---------------------------- 경험 ----------------------------
def normalize_skills(text:str) -> List[str]:
  '쉼표로 구분된 기술 문자열을 표준 기술명 리스트로 (중복 제거)'
  result = []
  for s in text.split(','):
    s = s.strip()
    if not s:
      continue
    s = skill_dict.get(s.lower(), s)
    if s not in result:
      result.append(s)
  return result

def get_exps(user_id:str) -> List[dict]:
  '경험 목록'
  return list(exp_data.get(user_id, {}).values())

def get_exp(user_id:str, id:int) -> Optional[dict]:
  '경험 하나'
  exp = exp_data.get(user_id, {}).get(id)
  return exp.copy() if exp else None

def create_exp(user_id:str, exp:dict):
  '경험 추가'
  exps = exp_data.setdefault(user_id, {})
  exp['id'] = max(exps.keys(), default=0) + 1
  exps[exp['id']] = exp

def update_exp(user_id:str, exp:dict) -> str:
  '경험 수정 후 결과 메시지 반환'
  exps = exp_data.get(user_id, {})
  if exp['id'] in exps:
    exps[exp['id']] = exp
    return f"{exp['id']}번 경험 '{exp['title']}'을(를) 수정하였습니다."
  return f"{exp['id']}번 경험을 찾을 수 없습니다."

def delete_exp(user_id:str, id:int) -> str:
  '경험 삭제 후 결과 메시지 반환'
  exps = exp_data.get(user_id, {})
  if id in exps:
    del exps[id]
    return f"{id}번 경험을 삭제하였습니다."
  return f"{id}번 경험을 삭제할 수 없습니다."

# ---------------------------- 공고 ----------------------------
def get_jobs(job:str='', size:str='') -> List[dict]:
  '직무·기업 규모로 필터링한 공고 목록'
  return [j for j in job_data.values()
          if (not job or j['job'] == job) and (not size or j['size'] == size)]

def get_job(id:int) -> Optional[dict]:
  '공고 하나'
  return job_data.get(id)

# ---------------------------- 추천 ----------------------------
# 1차 초안 : 기술 키워드 일치로 점수 계산 (규칙 기반)
# 이후 단계 : 경험·공고 임베딩 → 벡터DB 유사도 검색 → LLM이 근거 생성 (RAG)
W_SKILL, W_JOB = 0.7, 0.3   # 추천 점수 가중치 (임시값)

def recommend(exps:List[dict], job:str='', size:str='', top_k:int=5) -> List[dict]:
  '경험 목록으로 공고를 추천하고 근거(일치/부족 기술, 근거 경험)를 함께 반환'
  my_skills = {s for e in exps for s in e['skills']}
  results = []
  for j in get_jobs(size=size):  # 기업 규모는 필터
    matched = [s for s in j['skills'] if s in my_skills]
    missing = [s for s in j['skills'] if s not in my_skills]
    skill_rate = len(matched) / len(j['skills'])
    job_match = 1 if (not job or j['job'] == job) else 0
    score = round((skill_rate * W_SKILL + job_match * W_JOB) * 100)
    # 근거 : 일치한 기술마다 그 기술을 쓴 내 경험 id
    evidence = [{'skill':s, 'exp_ids':[e['id'] for e in exps if s in e['skills']]}
                for s in matched]
    results.append({**j, 'score':score, 'matched':matched,
                    'missing':missing, 'evidence':evidence})
  results.sort(key=lambda r: r['score'], reverse=True)
  return results[:top_k]

def roadmap(exps:List[dict], job:str='') -> List[dict]:
  '희망 직무 공고에서 요구 비율이 높은 순으로 부족 기술 정리'
  my_skills = {s for e in exps for s in e['skills']}
  jobs = get_jobs(job=job)
  counts = {}
  for j in jobs:
    for s in j['skills']:
      counts[s] = counts.get(s, 0) + 1
  items = [{'skill':s, 'rate':round(c / len(jobs) * 100), 'have':s in my_skills}
           for s, c in counts.items()]
  items.sort(key=lambda x: (x['have'], -x['rate']))  # 부족 기술 먼저, 요구 비율 높은 순
  return items

def cover_letter(exps:List[dict], job_id:int) -> Optional[dict]:
  '공고 문항별 자기소개서 초안 (문장마다 출처 경험 id 표기)'
  j = get_job(job_id)
  if not j:
    return None
  answers = []
  for q in j['questions']:
    # 공고 기술과 많이 겹치는 경험부터 사용
    ranked = sorted(exps, key=lambda e: len(set(e['skills']) & set(j['skills'])), reverse=True)
    sentences = []
    for e in ranked[:2]:
      common = [s for s in e['skills'] if s in j['skills']]
      skill_txt = ', '.join(common) if common else ', '.join(e['skills'])
      sentences.append({'text':f"'{e['title']}'에서 {skill_txt}을(를) 활용해 {e['content']}",
                        'exp_id':e['id']})
    if not sentences:
      sentences.append({'text':'정보 없음 : 문항에 쓸 경험을 먼저 등록하세요.', 'exp_id':None})
    answers.append({'question':q, 'sentences':sentences})
  return {'job':j, 'answers':answers}


if __name__ == '__main__':
  print(normalize_skills('파이썬, 장고 , Docker, 파이썬'))
  print([(r['company'], r['score']) for r in recommend(get_exps('hong'), job='백엔드')])
  print(roadmap(get_exps('hong'), job='백엔드'))
# 실행방법 : python repository.py
