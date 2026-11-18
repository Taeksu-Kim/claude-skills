# 5. 점검 (check) — 화면 코드 점검표

**읽는 때**: 완성 후·공개 전, 또는 큰 수정 뒤. **다 하면**: `6-verify.md` (코드 점검은 실제 화면 확인을 대신하지 못한다).

바뀐 화면 파일(HTML·CSS·JS)을 읽고 아래 규칙 위반을 `파일:줄 - 문제` 형식으로 짧게 보고한다. 설명은 고치는 법이
뻔하지 않을 때만. 문제 없는 파일은 `✓ 통과`. React/Next 전용 규칙은 뺐다 — 필요하면 원문 참조
(https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md).

## 접근성
- 아이콘만 있는 버튼에 `aria-label`. 폼 컨트롤에 `<label>` 또는 `aria-label`.
- 동작은 `<button>`, 이동은 `<a>`. 클릭 핸들러 달린 `<div>`·`<span>` 금지.
- 이미지 `alt` (장식이면 `alt=""`), 장식 아이콘 `aria-hidden="true"`.
- 비동기 갱신(토스트·검증 결과)에 `aria-live="polite"`. 제목 위계 `h1`→`h6` 순서.
- 시맨틱 HTML(`button`·`a`·`label`·`table`) 먼저, ARIA 는 그다음.

## 포커스
- 모든 상호작용 요소에 보이는 포커스. 대체 없이 `outline: none` 금지. `:focus` 보다 `:focus-visible`.
- 고정 헤더·오버레이가 포커스된 요소를 가리지 않는다.

## 폼
- 입력에 의미 있는 `name`, 맞는 `type`·`inputmode`. 붙여넣기 막기 금지.
- 라벨 클릭 시 컨트롤 선택 (`for` 또는 감싸기). 체크박스·라디오는 라벨과 한 덩어리 클릭 영역.
- 제출 버튼은 요청 시작 전까지 활성, 요청 중 로딩 표시. 에러는 필드 옆, 제출 시 첫 에러로 포커스.
- 저장 안 한 변경이 있으면 이동 전 경고.

## 상태·내용
- 긴 텍스트 처리 (`text-overflow`, `line-clamp`, `overflow-wrap`). flex 자식은 `min-width: 0`.
- 빈 문자열·빈 배열에서 깨진 화면을 그리지 않는다. 짧은·보통·아주 긴 입력을 모두 가정.
- 화면에 `null`·`undefined`·`NaN`·`[object Object]` 가 노출될 경로가 없는지.
- 삭제 등 되돌릴 수 없는 동작은 확인 또는 되돌리기 창. 즉시 실행 금지.
- 필터·탭·페이지 같은 상태는 가능하면 URL(쿼리)에 반영해 새로고침해도 유지.

## 모션
- `prefers-reduced-motion` 존중. `transform`·`opacity` 위주. `transition: all` 금지 — 속성을 명시.
- 애니메이션은 사용자 입력으로 중단 가능.

## 글자·숫자
- 숫자 열·비교 숫자에 `font-variant-numeric: tabular-nums`.
- 날짜·숫자는 `Intl.DateTimeFormat`·`Intl.NumberFormat` (하드코딩 포맷 금지). 한국어 화면의 날짜 표기는 `../topics/korean.md`.
- 로딩 문구는 "불러오는 중…" 처럼 `…`.

## 성능
- 50행 넘는 목록은 가상화 또는 `content-visibility: auto` 검토.
- 렌더 중 레이아웃 읽기(`getBoundingClientRect`, `offsetHeight`) 반복 금지. DOM 읽기·쓰기 묶기.
- `<img>` 에 `width`·`height` (레이아웃 밀림 방지).

## 다크모드·레이아웃
- 다크 테마면 `color-scheme: dark` (스크롤바·입력창 색). 네이티브 `<select>` 에 배경·글자색 명시.
- 원치 않는 가로 스크롤 없음. 레이아웃은 JS 측정 대신 flex/grid.

## 호버·상호작용
- 버튼·링크에 hover 피드백. hover·active·focus 가 평상시보다 더 눈에 띄게.

## 문구
- 버튼은 구체적 동작 ("저장", "파일 가져오기" — "확인"·"다음" 지양). 에러는 해결 방법까지.
- 개수는 숫자로 ("8건").

## 자주 놓치는 것
- **한글 IME**: Enter 처리에서 `e.isComposing || e.keyCode === 229` 면 무시 (조합 중 Enter 로 두 번 전송·글자 잘림). `../topics/korean.md`
- z-index 는 정한 단계(10/20/30/50)만. 9999 같은 임의 값 금지.
- 가맹점명·URL·ID 같은 긴 토큰: `overflow-wrap: anywhere` + 부모 flex/grid 자식 `min-width: 0`. 본문 전체에 `break-all` 금지.
- 핵심 텍스트(제목·동작·에러·구분용 이름)는 카드 높이를 맞추려고 말줄임하지 않는다. 자르면 전체를 볼 길을 준다.
- 필터 칩·배지 묶음: 한 줄에서 잘려 숨지 않게 줄바꿈 또는 조작 가능한 "+n".
- 폼 제출 실패: 상단 오류 요약(`role="alert"`, 포커스 이동, 각 항목이 해당 필드로 링크) + 필드 옆 오류 유지.
- 개수 배지 갱신: 맨숫자 대신 "3건 선택됨" 같은 하나의 `role="status"` 메시지.
- 상태 전환 애니메이션: 연속 클릭 시 이전 것을 취소하고 최종 상태를 직접 설정 (`transitionend` 에 정확성 의존 금지).
- 클릭 영역 최소 24×24px (WCAG 2.2), 터치 위주 화면은 44px 권장. 인접 대상과 간격 확보.
- 완료 확인은 실제 전송·저장이 끝난 뒤에만 표시.

## 반드시 잡을 안티패턴
`user-scalable=no`·`maximum-scale=1` (확대 막기) · 붙여넣기 차단 · `transition: all` ·
대체 없는 `outline: none` · 클릭 핸들러 단 `div` · 크기 없는 이미지 · 라벨 없는 입력 ·
`aria-label` 없는 아이콘 버튼 · 하드코딩 날짜·숫자 포맷 · 키보드 대안 없는 제스처 전용 동작
