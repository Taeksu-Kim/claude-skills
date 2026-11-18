# 한국어 화면

**읽는 때**: 한국어 화면이면 입력·줄바꿈·숫자 규칙은 항상. 등락 색은 등락을 표시할 때만.

## 입력 (IME) — 필수

한글 조합 중 Enter 는 글자 확정이다. 이것을 제출로 처리하면 **두 번 전송되거나 마지막 글자가 잘린다**.

```js
input.addEventListener('keydown', e => {
  if (e.key !== 'Enter' || e.shiftKey || e.ctrlKey || e.metaKey || e.altKey) return;
  e.preventDefault();
  if (e.isComposing || e.keyCode === 229) return;   // 조합 중이면 무시
  submit();
});
```
`compositionend` 에서 제출하지 않는다. 가상 키보드를 위해 제출 버튼은 남긴다. 검색창·채팅·라벨 입력 모두 해당.

## 줄바꿈
- 한국어 문장이 단어 중간에서 끊기지 않게 본문·제목에 `word-break: keep-all` (긴 토큰이 섞이면 `overflow-wrap: anywhere` 병행).
- 한 글자만 다음 줄로 넘어가는 제목은 `text-wrap: balance`.

## 글꼴
- 한글 글꼴이 먼저 정해져야 한다 (라틴 글꼴 조합 목록은 한글에 소용없다). 웹 글꼴이면 쓰는 굵기만 로드.
- 시스템 글꼴 스택으로 충분한 경우가 많다: `-apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif`.

## 숫자·날짜
- 금액: `Intl.NumberFormat('ko-KR')` 천 단위 구분 + "원". 큰 값은 "만 원"·"억 원" 축약 가능, 표 안에서는 단위 통일.
- 숫자 열 오른쪽 정렬 + `font-variant-numeric: tabular-nums`.
- 날짜 `YYYY-MM-DD`, 시각이 의미 있으면 시간대 명시 (KST, 미국 장이면 ET).
  데이터가 이미 `2026-11-18` 문자열이면 그대로 쓴다. `Date` 객체면 `Intl.DateTimeFormat('sv-SE')` — `'ko-KR'`은
  `2026. 11. 18.`을 낸다. `toISOString().slice(0, 10)`은 UTC 기준이라 KST 00~09시에 전날이 된다.

## 등락 색 — 등락을 표시할 때만
- 한국 관례: **상승·증가 = 빨강, 하락·감소 = 파랑** (서구식 초록/빨강과 반대).
- 단 "지출 증가 = 나쁨"처럼 의미가 반대인 지표는 색을 등락이 아니라 **의미(좋음/나쁨)**에 맞춘다.
- 어느 쪽이든 화살표·부호(▲▼ +−)를 같이 써서 색에만 의존하지 않는다. 단 같은 프로젝트가 내려받는 보고서(docx·pdf)도 내면
  보고서 규칙(`문서 작성 프로젝트/design/GUIDE.md`: ▲▼ 대신 +9.5% 같은 부호)을 화면에도 써서 같은 사실을 같은 표현으로 (D11).
