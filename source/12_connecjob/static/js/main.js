// ConnecJob 공통 스크립트 (03_javaScript ch05 함수, ch07 class, ch11 이벤트, ch12 fetch 참고)

// 서버에 fetch 요청을 보내고 결과 메시지를 alert로 보여주는 클래스
class Api{
  constructor(baseUrl){
    this.baseUrl = baseUrl;
  }
  request(path, method, body){
    const option = {method:method};
    if(body){
      option.headers = {'Content-Type':'application/json'}; // JSON을 보낸다고 서버에 알려 줌
      option.body = JSON.stringify(body);                     // 객체 → JSON 문자열
    }
    return fetch(this.baseUrl + path, option)
      .then(response => {
        if(!response.ok){
          throw new Error(`${response.status} ${response.statusText}`);
        }
        return response.text();
      });
  }
  put(path, body){ return this.request(path, 'PUT', body); }
  delete(path){ return this.request(path, 'DELETE'); }
}
const api = new Api('');

document.addEventListener('DOMContentLoaded', () => {
  // 1. 모바일 메뉴 열기/닫기
  const menuBtn = document.getElementById('menuBtn');
  if(menuBtn){
    menuBtn.addEventListener('click', () => {
      document.querySelector('header nav').classList.toggle('open');
    });
  }

  // 2. 현재 페이지 메뉴 표시
  document.querySelectorAll('header nav a').forEach(a => {
    if(a.getAttribute('href') !== '/' && location.pathname.startsWith(a.getAttribute('href'))){
      a.classList.add('active');
    }
  });

  // 3. 메인 문구 바꾸기 (setInterval)
  const rolling = document.getElementById('rolling');
  if(rolling){
    const words = ['공고에', '로드맵에', '자기소개서에'];
    let i = 0;
    setInterval(() => {
      i = (i + 1) % words.length;
      rolling.textContent = words[i];
    }, 2000);
  }

  // 4. 점수 막대 애니메이션 (setTimeout)
  setTimeout(() => {
    document.querySelectorAll('.bar span').forEach(span => {
      span.style.width = span.dataset.width + '%';
    });
  }, 100);

  // 5. 표의 행 클릭 시 이동 (data-href)
  document.querySelectorAll('tr[data-href]').forEach(tr => {
    tr.addEventListener('click', () => location.href = tr.dataset.href);
  });

  // 6. 경험 삭제 (fetch DELETE)
  document.querySelectorAll('.exp-delete').forEach(btn => {
    btn.addEventListener('click', function(){
      if(!confirm(`'${this.dataset.title}' 경험을 삭제할까요?`)) return;
      api.delete(`/exps/${this.dataset.id}`)
        .then(data => { alert(data); location.reload(); })
        .catch(err => alert(`실패 : ${err.message}`));
    });
  });

  // 7. 기술 입력 미리보기 : 쉼표로 나눠 칩으로 보여 줌 (keyup)
  document.querySelectorAll('input[name=skills]').forEach(input => {
    const preview = document.getElementById(input.dataset.preview);
    if(!preview) return;
    const draw = () => {
      preview.innerHTML = '';
      input.value.split(',').map(s => s.trim()).filter(s => s).forEach(s => {
        const span = document.createElement('span'); // 문서객체 생성 (ch10)
        span.className = 'chip';
        span.textContent = s;
        preview.appendChild(span);
      });
    };
    input.addEventListener('keyup', draw);
    draw();
  });
});
