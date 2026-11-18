# 6. 확인 (verify) — 실제 브라우저로

**읽는 때**: 모든 구현·수정의 마지막. **다 하면**: 보고하고 끝.
코드를 읽는 것은 검증이 아니다. 화면을 띄워 **스크린샷을 Read 로 직접 보고**, 콘솔 오류를 센다.

## 도구

- 파이썬: Playwright가 설치된 환경 (프로젝트 `CLAUDE.md`에 경로가 있으면 그것)
- 브라우저: `~/.cache/ms-playwright/chromium-*` (설치된 playwright 와 버전이 다르면 `executable_path` 로 대체)
- Playwright MCP 는 쓰지 않는다. 스크립트 한 번 실행이 더 가볍고 반복 가능하다.

## 기준 패턴 — 프로젝트의 `tools/browser_check.py`

프로젝트에 `tools/browser_check.py` 가 있으면 **그것을 확장**한다 (새로 만들지 않는다). 없으면 아래 모양으로 만든다:
- 임시 DB·포트로 서버를 직접 띄우고 끝나면 정리 (실제 `data/` 는 건드리지 않음)
- 외부 LLM 은 가짜로 대체, 가짜 입력 파일로 실제 흐름을 눌러봄
- `check(이름, 조건, 상세)` 로 PASS/FAIL 출력, 마지막에 `n/m PASS`, 실패 시 종료코드 1
- `pageerror`·`console` 오류 수집 → "JS 오류 없음" 확인
- 화면 전체에 `null`·`undefined`·`NaN` 글자 없음 확인
- 단위 테스트가 못 잡는 것(동시 요청, 새로고침 후 상태)을 여기서 잡는다

## 매번 확인할 것

| 항목 | 방법 |
|---|---|
| 폭 3종 | `set_viewport_size` 390×844 / 768×1024 / 1280×900 각각 `screenshot(full_page=True)` |
| 다크모드 | `browser.new_context(color_scheme="dark")` 로 1280 폭 한 장 더 |
| 콘솔 오류 0 | `page.on("pageerror")` + `page.on("console")` (type == "error") |
| 깨진 값 노출 없음 | `inner_text("body")` 에 `null`·`undefined`·`NaN` 없음 |
| 가로 스크롤 없음 | `page.evaluate("document.documentElement.scrollWidth <= innerWidth")` (390 폭에서) |
| 상태들 | 빈 데이터 · 데이터 있음 · 에러 응답 · 로딩 중 (가능한 것만). 판정·경고 문구가 있으면 브리프 경계표의 경우(반례·이상치 포함)마다 데이터를 바꿔 넣고 **판정·색·정렬·집계가 표대로인지** 본다 |
| 핵심 과업 | 브리프의 주 과업을 실제로 클릭·입력해서 끝까지 — **처음 쓰는 실사용자로** (브리프의 쓰는 사람), 막힌 곳을 적는다 |
| 키보드 | Tab만으로 핵심 과업을 끝까지 — 포커스가 보이나, 순서가 보이는 순서와 맞나 (`page.keyboard.press("Tab")` 반복). 조작(Enter·Space) 직후 `document.activeElement`가 `BODY`면 실패. 포커스 링 없음·잘림은 아래 DETAIL_JS가 잰다 (눈으로 보라는 줄은 2회차에도 못 잡았다, D13) |

## 레이아웃 자동 측정 (눈으로 놓치는 것)

> 외부 계약: `논문 분석 프로젝트/tools/browser_check.py`가 이 블록을 LAYOUT_JS 블록(이름 뒤 등호와 큰따옴표 세 개로 여는 줄)을 이름으로 찾아 잘라 읽고, `다른 프로젝트/tools/layout_check.js`는
> 복사본이다. 이름·따옴표 형식을 바꾸지 않는다. 내용을 고치면 다른 프로젝트 복사본도 같이 (D10).

각 폭에서 아래를 `page.evaluate(LAYOUT_JS)` 로 돌려 결과가 비어 있는지 확인한다:
화면 밖으로 삐져나간 요소, 24px 미만 클릭 대상, 서로 겹친 클릭 대상.

```python
LAYOUT_JS = """() => {
  const W = document.documentElement.clientWidth, out = {overflow: [], small: [], overlap: []};
  const vis = e => { const s = getComputedStyle(e), r = e.getBoundingClientRect();
    // checkVisibility: 접힌 <details> 안처럼 조상 때문에 안 보이는 요소도 거른다 (자기 스타일만 보면 겹침으로 오탐)
    return (!e.checkVisibility || e.checkVisibility({visibilityProperty: true})) && s.visibility !== 'hidden' && s.display !== 'none' && r.width > 0 && r.height > 0; };
  const name = e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + ' "' + (e.innerText || e.value || e.getAttribute('aria-label') || '').trim().slice(0, 20) + '"';
  for (const e of document.querySelectorAll('body *')) {
    if (!vis(e)) continue; const r = e.getBoundingClientRect();
    if (r.right > W + 1 && getComputedStyle(e.parentElement).overflowX === 'visible') out.overflow.push(name(e));
  }
  const hits = [...document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,[role=button],[onclick]')].filter(vis);
  const tiny = r => r.width < 24 || r.height < 24;
  for (const e of hits) {  // 연결된 라벨도 클릭 영역이므로, 컨트롤과 라벨이 둘 다 작을 때만 보고
    const r = e.getBoundingClientRect();
    const lab = e.closest('label') || (e.id && document.querySelector(`label[for="${e.id}"]`));
    if (tiny(r) && !(lab && vis(lab) && !tiny(lab.getBoundingClientRect())) && !e.closest('p,li,td'))
      out.small.push(name(e) + ` ${Math.round(r.width)}x${Math.round(r.height)}`); }
  for (let i = 0; i < hits.length; i++) for (let j = i + 1; j < hits.length; j++) {
    const a = hits[i].getBoundingClientRect(), b = hits[j].getBoundingClientRect();
    if (hits[i].contains(hits[j]) || hits[j].contains(hits[i])) continue;
    if (a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1) out.overlap.push(name(hits[i]) + ' ↔ ' + name(hits[j]));
  }
  return out;
}"""
```

결과는 판단 재료다. 문장 안 링크·의도한 아이콘 버튼처럼 정당한 예외는 이유를 적고 넘어간다.

## 디테일 자동 측정 — 디자이너의 꼼꼼함 (D10)

LAYOUT_JS가 "깨졌나"를 본다면 이건 "어디까지 챙겼나"를 본다. 일반 수준의 화면은 큰 그림은 맞추고 여기서 멈춘다.
1280 폭(라이트·다크 각각)에서 `page.evaluate(DETAIL_JS)`. 목표와 판정:

| 항목 | 목표 | 걸리면 |
|---|---|---|
| `fontSizeCount` 글자 크기 단계 | 6개 이하 (`layout-type-color` 글자 척도) | 같은 역할의 글은 같은 크기로 합친다 |
| `offGridSpacing` 간격 | 비어 있음 — 목표 체계는 4px 배수, 측정은 2px 배수가 아닌 값만 잡는다(브라우저 기본값 오탐 방지) | 간격 토큰으로 바꾼다 |
| `lowContrast` 글자 대비 | 비어 있음 (본문 4.5:1, 큰 글 3:1) | 색 토큰을 고친다. 배경 이미지 위 글은 측정 밖 — 눈으로 |
| `tabBackJumps` Tab 역행 | 비어 있음 | DOM 순서·`tabindex`를 고친다. 사이드바처럼 의도한 경우는 이유를 적는다 |
| `numericNotTabular` 숫자 칸 | 0 | 숫자 열에 `font-variant-numeric: tabular-nums` |
| `focusNoRing` 포커스 링 없음 | 비어 있음 | `:focus-visible`에 outline 또는 box-shadow |
| `focusRingClipped` 잘린 포커스 링 | 비어 있음 | `overflow`가 보이지 않는 묶음(분할 버튼·탭·카드) 안이면 `outline-offset`을 음수로(inset) |

시험(2026-11-18): 위반을 심은 페이지에서 5가지 모두 잡고, 깨끗한 페이지에서 0건, 다크 동일, 가계부 화면 프로젝트 실제 화면에서 오류 없이 돎.
포커스 두 항목 시험(같은 날, D13): 심은 페이지(분할 버튼 안 바깥 링·`outline:none`)에서 둘 다 잡고, inset·그림자 링 페이지에서 0건, 루프의 실제 화면 3개 모두 정렬 버튼 잘림을 잡음(평가자가 눈으로 찾은 것과 같음), 라이트·다크 동일. 요소를 실제로 포커스하므로 포커스 때 열리는 메뉴가 있으면 열릴 수 있다 — 측정 뒤 원래 포커스·스크롤로 되돌린다.

```python
DETAIL_JS = """() => {
  const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && parseFloat(s.opacity) > 0; };
  const hasText = el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 0);
  const textEls = [...document.querySelectorAll('body *')].filter(el => hasText(el) && vis(el));
  // 1) 글자 크기 단계
  const sizes = [...new Set(textEls.map(el => Math.round(parseFloat(getComputedStyle(el).fontSize))))].sort((a, b) => a - b);
  // 2) 간격이 2px 단위에서 벗어난 값 (margin·padding·gap, 0과 1px 제외)
  const props = ['marginTop','marginBottom','marginLeft','marginRight','paddingTop','paddingBottom','paddingLeft','paddingRight','rowGap','columnGap'];
  const off = new Map(); let spacingTotal = 0;
  for (const el of document.querySelectorAll('body *')) { if (!vis(el)) continue; const s = getComputedStyle(el);
    for (const p of props) { const v = parseFloat(s[p]); if (!v || Math.abs(v) <= 1) continue; spacingTotal++;
      const r = Math.round(Math.abs(v) * 10) / 10; if (r % 2 !== 0) off.set(r, (off.get(r) || 0) + 1); } }
  // 3) 글자 대비 (가장 가까운 불투명 배경 기준, 배경 이미지는 건너뜀)
  const rgb = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const bgOf = el => { for (let e = el; e; e = e.parentElement) { const s = getComputedStyle(e);
      if (s.backgroundImage && s.backgroundImage !== 'none') return null; const c = rgb(s.backgroundColor); if (c && c.a >= 0.99) return c; }
    return { r: 255, g: 255, b: 255, a: 1 }; };
  const lowContrast = [];
  for (const el of textEls) { const s = getComputedStyle(el); const fg = rgb(s.color); const bg = bgOf(el); if (!fg || !bg) continue;
    const L1 = lum(fg), L2 = lum(bg); const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const px = parseFloat(s.fontSize), bold = parseInt(s.fontWeight) >= 700; const large = px >= 24 || (bold && px >= 18.66);
    const need = large ? 3 : 4.5;
    if (ratio < need) lowContrast.push({ text: el.textContent.trim().slice(0, 30), ratio: Math.round(ratio * 100) / 100, need }); }
  // 4) Tab 순서 vs 보이는 순서 (위로 20px 넘게 거슬러 오르는 이동)
  const focusSel = 'a[href],button,input,select,textarea,[tabindex],summary,[contenteditable="true"]';
  const foc = [...document.querySelectorAll(focusSel)].filter(el => vis(el) && el.tabIndex >= 0 && !el.disabled);
  const ordered = [...foc.filter(e => e.tabIndex > 0).sort((a, b) => a.tabIndex - b.tabIndex), ...foc.filter(e => e.tabIndex === 0)];
  const backJumps = [];
  for (let i = 1; i < ordered.length; i++) { const a = ordered[i - 1].getBoundingClientRect(), b = ordered[i].getBoundingClientRect();
    if (b.top < a.top - 20) backJumps.push({ from: (ordered[i - 1].textContent || ordered[i - 1].getAttribute('aria-label') || ordered[i - 1].tagName).trim().slice(0, 20),
                                             to: (ordered[i].textContent || ordered[i].getAttribute('aria-label') || ordered[i].tagName).trim().slice(0, 20) }); }
  // 5) 숫자 열: 숫자로만 된 칸이 tabular-nums 인가
  const numCells = textEls.filter(el => /^[\s\-+−₩,.\d원%▲▼]+$/.test(el.textContent.trim()) && /\d/.test(el.textContent));
  const notTabular = numCells.filter(el => !getComputedStyle(el).fontVariantNumeric.includes('tabular-nums')).length;
  // 6) 포커스 링: 포커스했을 때 링이 없거나, overflow로 잘리는 조상 안에서 링이 그 경계를 넘는가
  const ringOf = el => { const s = getComputedStyle(el); const ow = s.outlineStyle !== 'none' ? parseFloat(s.outlineWidth) || 0 : 0;
    return { ow, off: parseFloat(s.outlineOffset) || 0, shadow: s.boxShadow && s.boxShadow !== 'none' }; };
  const prevActive = document.activeElement, sx = scrollX, sy = scrollY;
  const noRing = [], clipped = [];
  for (const el of ordered.slice(0, 200)) {
    const before = ringOf(el); el.focus({ preventScroll: true }); if (document.activeElement !== el) continue;
    const r = ringOf(el), label = (el.textContent || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 20);
    const changed = r.ow !== before.ow || r.shadow !== before.shadow || r.off !== before.off;
    if (!(r.ow > 0 || r.shadow) || !changed && !(r.ow > 0)) { noRing.push(label); continue; }
    const ext = r.ow > 0 ? r.ow + r.off : 0; if (ext <= 0) continue;   // inset 링·그림자만 쓰는 경우는 잘림 측정 밖
    const b = el.getBoundingClientRect();
    for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) { const as = getComputedStyle(a);
      if (as.overflowX === 'visible' && as.overflowY === 'visible') continue;
      const ar = a.getBoundingClientRect(), bl = parseFloat(as.borderLeftWidth), br = parseFloat(as.borderRightWidth),
            bt = parseFloat(as.borderTopWidth), bb = parseFloat(as.borderBottomWidth);
      const cut = (b.left - ext < ar.left + bl - 0.5) || (b.right + ext > ar.right - br + 0.5) || (b.top - ext < ar.top + bt - 0.5) || (b.bottom + ext > ar.bottom - bb + 0.5);
      if (cut) { clipped.push(label); break; } } }
  if (prevActive && prevActive.focus) prevActive.focus({ preventScroll: true }); else document.activeElement.blur(); scrollTo(sx, sy);
  return { fontSizes: sizes, fontSizeCount: sizes.length,
           offGridSpacing: [...off.entries()].map(([v, n]) => `${v}px×${n}`), offGridRatio: spacingTotal ? Math.round([...off.values()].reduce((a, b) => a + b, 0) / spacingTotal * 100) / 100 : 0,
           lowContrast: lowContrast.slice(0, 10), lowContrastCount: lowContrast.length,
           focusables: ordered.length, tabBackJumps: backJumps.slice(0, 5),
           numericCells: numCells.length, numericNotTabular: notTabular,
           focusNoRing: noRing.slice(0, 10), focusRingClipped: clipped.slice(0, 10) };
}"""
```

## 가치·밀도 점검 (기술 점검과 별개, 생략 금지)

스크린샷을 보기 전에 `../topics/value-density.md` 를 읽고, 스크린샷을 보면서 그 항목에 답한다.
기술 항목이 모두 PASS 여도 이 점검에서 걸리면 고친 뒤 다시 본다. 빠른 확인(작은 수정)일 때는 A·C만.
**고치고 다시 보기는 2회까지** — 그래도 걸리는 것은 더 고치지 말고 보고에 "남은 문제 + 고칠 방향"으로 낸다
(수정 회차가 끝없이 늘거나, 반대로 자기 화면을 후하게 보고 넘기는 것을 둘 다 막는다, D4).

스크린샷은 **반드시 Read 로 열어 본다.** 한 번 볼 때 여러 문제를 모아서 고치고 다시 본다
(수정할 때마다 찍지 않는다). 겹침·잘림·정렬 어긋남·대비 부족·빈 공간 이상을 본다.

## 빠른 확인 (작은 수정일 때)

서버를 띄우고 해당 화면 1280 폭 스크린샷 1장 + 390 폭 1장 + 콘솔 오류 확인. 프로젝트에 `browser_check.py` 가
있으면 그냥 그것을 돌린다.

## 보고

`n/m PASS`, 실패 항목, DETAIL_JS 결과(목표를 못 넘은 항목과 이유), 스크린샷 경로, 가치·밀도 점검 결과(핵심 가치 문장 + 고친 항목 + 2회 뒤 남은 문제), 그리고
스크린샷을 보고 발견한 시각 문제(있으면). 측정한 것만 쓴다.
