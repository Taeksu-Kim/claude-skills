# 출처와 라이선스

이 스킬은 아래 공개 스킬들을 검토해 **우리 절차(단계 → 화면 종류 → 주제)에 맞게 한국어로 요약·재구성·수정**한 것이다
(2026-11-14). 원문을 그대로 복제하지 않았고, 엔진 바이너리·스크립트·데이터 파일은 포함하지 않는다.
라이선스 전문: `licenses/APACHE-2.0.txt`, `licenses/MIT-notices.txt`.

| 우리 파일 | 주로 가져온 원문 | 라이선스 |
|---|---|---|
| `stages/1-shape.md` | Impeccable `shape.md` + 모드 체계(SKILL.md Modes) | Apache-2.0 |
| `stages/2-build.md` | Impeccable `craft-floor.md`·`polish.md` 일부, Taste Skill 체크리스트의 "One system", frontend-design 선택자 충돌 주의 | Apache-2.0 / MIT |
| `stages/3-critique.md` | Impeccable `critique.md` (휴리스틱·인지부하·페르소나) | Apache-2.0 |
| `stages/4-refine.md` | Impeccable `distill.md`·`polish.md` | Apache-2.0 |
| `stages/5-check.md` | Vercel Web Interface Guidelines `command.md`, UI/UX Pro Max `ux-guidelines.csv` 일부 | MIT |
| `stages/6-verify.md` | 자체 (가계부 화면 프로젝트의 `browser_check.py` 패턴), 레이아웃 측정 항목은 Taste Skill 점검 개념 참고 | — |
| `modes/operate.md` | Impeccable `operate.md`·`mode-operate.md`·`craft-floor.md` | Apache-2.0 |
| `modes/read.md` | Impeccable `mode-read.md`, `typeset.md` 일부 | Apache-2.0 |
| `modes/persuade.md` | AI Design Skills `landing-page-design` PART A, Impeccable `mode-persuade.md` | MIT / Apache-2.0 |
| `topics/direction.md` | frontend-design (Anthropic) 설계 절차·기본값 경고 | Apache-2.0 |
| `topics/styles.md` | UI/UX Pro Max `styles.csv` 에서 추려 한 줄로 재작성 | MIT |
| `topics/copy.md` | frontend-design "writing in design", Impeccable `clarify.md`, Taste Skill 문구 점검 개념 | Apache-2.0 |
| `topics/layout-type-color.md` | Impeccable `layout.md`·`typeset.md`·`colorize.md`, AI Design Skills 중첩 반경 공식 | Apache-2.0 / MIT |
| `topics/harden.md` | Impeccable `harden.md` | Apache-2.0 |
| `topics/empty-onboard.md` | Impeccable `onboard.md` | Apache-2.0 |
| `topics/korean.md` | 자체, IME 규칙은 UI/UX Pro Max `ux-guidelines.csv` | MIT |
| `topics/craft.md` | 자체 (F1). AI 기본값 4·5는 frontend-design "calibration" 목록에서 줄여 옮김. 레퍼런스 규칙은 TDS·SEED·Primer 공개 문서를 우리 말로 요약하고 주소만 둠 (문서 복사 없음) | Apache-2.0 (frontend-design 부분) |
| `topics/color.md`, `scripts/palette.py` | 자체 (D18). OKLCH 변환식은 Björn Ottosson의 공개 OKLab 식. 회색·단계 근거는 TDS·SEED 공개 토큰을 측정 | — |
| `topics/value-density.md` | 자체. 사용자가 카드 게임 정보 표 작업(2026-11-14)에서 내린 수정 지시를 일반화 | — |

원문 위치
- Impeccable v4.9.0 — Paul Bakaus, https://github.com/pbakaus/impeccable (Apache-2.0)
- frontend-design — Anthropic, https://github.com/anthropics/skills (스킬 폴더 LICENSE.txt: Apache-2.0)
- Web Interface Guidelines — Vercel Labs, https://github.com/vercel-labs/web-interface-guidelines (MIT)
- UI/UX Pro Max — Next Level Builder, https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (MIT)
- AI Design Skills — Elaya, https://github.com/elayadesign/ai-design-skills (MIT)
- Taste Skill — https://github.com/Leonxlnx/taste-skill (MIT — 점검 개념만 참고, 문장은 옮기지 않음)

## 검토 후 쓰지 않은 것 (2026-11-14)
- Impeccable 엔진 바이너리·스크립트: 외부 통신(시각 방향 카탈로그, 텔레메트리 기본 켜짐), 라이브 모드는 HMR 필요
- UI/UX Pro Max 검색 스크립트·팔레트·글꼴 조합·차트표: 서드파티 코드 실행 필요, 추천이 유행 위주, 한글 글꼴 조합 1개뿐, 차트는 `dataviz` 와 중복
- Taste Skill 본문 규칙(사진 수·한 화면 한 섹션·보라색 금지 등)과 Stop 훅: 자체 취향을 강제 — "방향은 프로젝트마다" 원칙과 충돌
- AI Design Skills PART B (글꼴·색·히어로 그라데이션 지정): 자체 취향. figma-designer: Figma 필요
- Playwright MCP (스크립트로 충분), Figma MCP·21st.dev (계정·API 키 필요), Design to Motion (저장소에 없음)
