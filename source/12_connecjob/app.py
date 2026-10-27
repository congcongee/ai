from flask import (Flask, request, render_template, redirect, url_for,
                   abort, session, jsonify)
from repository import (id_exists, join_member, login_check,
                        normalize_skills, get_exps, get_exp, create_exp, update_exp, delete_exp,
                        get_jobs, get_job, recommend, roadmap, cover_letter)
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'connecjob123!')  # 세션 암호화 키

JOBS = ['백엔드', '데이터', 'AI']          # 직무 카테고리
SIZES = ['대기업', '중견', '외국계']        # 기업 규모

@app.context_processor
def common():
  "모든 템플릿에서 쓰는 공통 변수"
  return dict(JOBS=JOBS, SIZES=SIZES)

def login_required(func):
  "로그인이 필요한 페이지에 붙이는 데코레이터 (ch2 ex3_decorator 참고)"
  @wraps(func)
  def wrapper(*args, **kwargs):
    if not session.get('user_id'):
      return redirect(url_for('login', next=request.path))
    return func(*args, **kwargs)
  return wrapper

# ---------------------------- 메인 ----------------------------
@app.route('/')
def index():
  "메인 : 서비스 소개 + 경험 입력 시작"
  return render_template('index.html')

# ---------------------------- 회원 ----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'GET':
    return render_template('member/login.html', next=request.args.get('next', ''))
  member = login_check(request.form.get('id', ''), request.form.get('pw', ''))
  if not member:
    return render_template('member/login.html', msg='아이디 또는 비밀번호를 확인하세요',
                           next=request.form.get('next', ''))
  session['user_id'] = member['id']
  session['user_name'] = member['name']
  next_url = request.form.get('next', '')
  return redirect(next_url if next_url.startswith('/') else url_for('exps'))

@app.route('/logout')
def logout():
  session.pop('user_id', None)
  session.pop('user_name', None)
  return redirect(url_for('index'))

@app.route('/join', methods=['GET', 'POST'])
def join():
  if request.method == 'GET':
    return render_template('member/join.html')
  if join_member(request.form.to_dict()):
    return render_template('member/login.html', msg='가입되었습니다. 로그인하세요')
  return render_template('member/join.html', msg='이미 사용 중인 아이디입니다')

@app.route('/idConfirm')
def id_confirm():
  "아이디 중복 확인 (03_javaScript ch12 fetch keyup 예제의 서버 쪽)"
  id = request.args.get('id', '')
  return '사용 중인 아이디입니다' if id_exists(id) else '사용 가능한 아이디입니다'

# ---------------------------- 경험 CRUD ----------------------------
@app.route('/exps')
@login_required
def exps():
  "내 경험 목록 + 입력 폼"
  return render_template('exp/exps.html', exps=get_exps(session['user_id']))

@app.route('/exps', methods=['POST'])
@login_required
def exp_create():
  exp = {'title':request.form['title'], 'content':request.form['content'],
         'skills':normalize_skills(request.form.get('skills', ''))}
  create_exp(session['user_id'], exp)
  return redirect(url_for('exps'))

@app.route('/exps/<int:id>', methods=['GET'])
@login_required
def exp_update_page(id):
  exp = get_exp(session['user_id'], id)
  if exp:
    return render_template('exp/update.html', exp=exp)
  return abort(404, description=f'{id}번 경험은 존재하지 않습니다')

@app.route('/exps/<int:id>', methods=['PUT'])
@login_required
def exp_update(id):
  "fetch가 body에 JSON으로 보낸 데이터로 수정"
  data = request.get_json(silent=True) or {}
  exp = {'id':id, 'title':data.get('title', ''), 'content':data.get('content', ''),
         'skills':normalize_skills(data.get('skills', ''))}
  return update_exp(session['user_id'], exp)

@app.route('/exps/<int:id>', methods=['DELETE'])
@login_required
def exp_delete(id):
  return delete_exp(session['user_id'], id)

# ---------------------------- 추천 / 로드맵 / 자소서 ----------------------------
@app.route('/results')
@login_required
def results():
  "추천 결과 (희망 직무·기업 규모 필터)"
  job = request.args.get('job', '')
  size = request.args.get('size', '')
  my_exps = get_exps(session['user_id'])
  recs = recommend(my_exps, job=job, size=size)
  exp_titles = {e['id']:e['title'] for e in my_exps}
  return render_template('job/results.html', recs=recs, job=job, size=size,
                         exp_titles=exp_titles, has_exp=bool(my_exps))

@app.route('/jobs')
def jobs():
  "전체 공고 목록"
  return render_template('job/jobs.html',
                         jobs=get_jobs(request.args.get('job', ''), request.args.get('size', '')),
                         job=request.args.get('job', ''), size=request.args.get('size', ''))

@app.route('/jobs/<int:id>')
def job(id):
  "공고 상세 (원문)"
  j = get_job(id)
  if j:
    return render_template('job/job.html', j=j)
  return abort(404, description=f'{id}번 공고는 존재하지 않습니다')

@app.route('/roadmap')
@login_required
def roadmap_page():
  job = request.args.get('job') or JOBS[0]
  items = roadmap(get_exps(session['user_id']), job=job)
  return render_template('job/roadmap.html', items=items, job=job)

@app.route('/cover-letter/<int:job_id>')
@login_required
def cover_letter_page(job_id):
  my_exps = get_exps(session['user_id'])
  letter = cover_letter(my_exps, job_id)
  if not letter:
    return abort(404, description=f'{job_id}번 공고는 존재하지 않습니다')
  return render_template('job/cover_letter.html', letter=letter,
                         exp_titles={e['id']:e['title'] for e in my_exps})

# ---------------------------- JSON API (이후 RAG 연결 지점) ----------------------------
@app.route('/api/recommend')
@login_required
def api_recommend():
  recs = recommend(get_exps(session['user_id']),
                   job=request.args.get('job', ''), size=request.args.get('size', ''))
  return jsonify(recs)

@app.errorhandler(404)
def not_found(error):
  return render_template('page_not_found.html', error=error), 404

# flask run --debug  (또는 python app.py)
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
