# Console tour

[English](#english) | [한국어](#한국어)

## English

**Verified on Redis Cloud console, free plan, 2026-11-07.**

Source for the site walkthrough at `/cloud/`: the page text in [`page.json`](./page.json) (four
languages), the generator [`scripts/build-lang-page.py`](../../scripts/build-lang-page.py) that writes `docs/cloud.md`, and the
capture manifest [`manifest.json`](./manifest.json) for
[`scripts/capture-console.mjs`](../../scripts/capture-console.mjs).

### Run

```bash
# Chrome already logged in to cloud.redis.io, started with --remote-debugging-port=9222
npm i playwright@1.48
cp .env.example .env          # your mask terms; gitignored
# copy manifest.json and put your database and subscription IDs into the paths, then:
node ../../scripts/capture-console.mjs manifest.json
python3 ../../scripts/build-lang-page.py page.json
```

The script attaches to that Chrome, opens its own tab, emulates dark mode and English there
(the account's theme setting is not changed), masks identifying text in the DOM, and refuses to
write a file when a leak term is still visible. A fault test on 2026-11-07 (a visible menu label
added to `LEAK_TERMS`) stopped the run with `still visible after masking`.

### What was observed

- Screens 01–06, 08 and 09 were one-time states: the empty account, the three create forms,
  the first-visit dialog, and the database under load. They are not in the manifest and cannot
  be retaken on the same account. Screen 04 is in light mode for that reason: the free form
  cannot be reopened once the free database exists.
- Masked on every screen: name, e-mail, account number, subscription and database IDs,
  endpoint host and port, IP addresses, API keys. Patterns live in the script; personal terms in
  `.env`.
- Not masked on purpose: the database name `notes-on-redis-free`, dates, plan limits, prices.

### Not run / caveats

- Paid screens (Essentials database pages, backups, Pro) wait for the budget issues.
- Captures are 1440×765 CSS pixels at 2x; tall pages are captured by growing the viewport to the
  scroll height.

| | |
|---|---|
| Plan needed | Free for the free-plan screens; paid screens need the Essentials budget issue |
| Verified on | Redis Cloud console, free plan, 2026-11-07 |

## 한국어

**확인: Redis Cloud 콘솔, 무료 플랜, 2026-11-07.**

사이트 `/cloud/` 안내 글의 원천이다. 네 언어 본문 [`page.json`](./page.json),
`docs/cloud.md`를 만드는 [`scripts/build-lang-page.py`](../../scripts/build-lang-page.py),
[`scripts/capture-console.mjs`](../../scripts/capture-console.mjs)용 캡처 매니페스트
[`manifest.json`](./manifest.json).

### 실행

```bash
# cloud.redis.io에 로그인된 Chrome을 --remote-debugging-port=9222로 띄워 둔다
npm i playwright@1.48
cp .env.example .env          # 가릴 문자열. gitignore 대상
# manifest.json을 복사해 경로에 DB·구독 ID를 넣은 뒤:
node ../../scripts/capture-console.mjs manifest.json
python3 ../../scripts/build-lang-page.py page.json
```

스크립트는 그 Chrome에 붙어 자기 탭을 열고, 그 탭에서만 다크 모드와 영어를 흉내 낸다(계정의
테마 설정은 바꾸지 않는다). DOM에서 식별 정보를 가리고, 누출 문자열이 화면에 남아 있으면 파일을
쓰지 않는다. 2026-11-07에 보이는 메뉴 이름을 `LEAK_TERMS`에 넣는 결함 시험을 했고,
`still visible after masking`으로 멈췄다.

### 관찰한 것

- 01–06, 08, 09번은 한 번뿐인 상태다. 빈 계정, 생성 양식 세 개, 첫 방문 안내 창, 부하 중인 DB.
  매니페스트에 없고 같은 계정에서 다시 찍을 수 없다. 04번이 밝은 테마인 이유도 같다.
  무료 DB가 생기면 무료 양식을 다시 열 수 없다.
- 모든 화면에서 가린 것: 이름, 이메일, 계정 번호, 구독·DB ID, 엔드포인트 호스트와 포트, IP 주소,
  API 키. 패턴은 스크립트에, 개인 문자열은 `.env`에 있다.
- 일부러 가리지 않은 것: DB 이름 `notes-on-redis-free`, 날짜, 플랜 한도, 가격.

### 미실행 / 주의

- 유료 화면(Essentials DB 화면, 백업, Pro)은 예산 이슈를 기다린다.
- 캡처는 CSS 픽셀 1440×765의 2배다. 긴 페이지는 뷰포트를 스크롤 높이만큼 늘려 찍는다.

| | |
|---|---|
| 필요한 플랜 | 무료 플랜 화면은 Free, 유료 화면은 Essentials 예산 이슈가 필요 |
| 확인한 버전 | Redis Cloud 콘솔, 무료 플랜, 2026-11-07 |
