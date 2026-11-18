"""한국어 글의 셀 수 있는 AI 패턴을 센다. 판정은 하지 않고 위치만 보여 준다.
사용: python check.py 글.txt [원문.txt]   (원문을 주면 숫자·고유명사 보존과 분량 비율도 본다)
"""
import re
import sys
from statistics import mean, pstdev

PATTERNS = {
    # 이름: (정규식, 설명)
    "대시": (r"[—–]", "두 문장 관계를 대시로 이음"),
    "A가아니라B": (r"(?:이|가|은|는)?\s?아니라[, ]", "아무도 주장하지 않은 A를 부정하는 대구일 수 있음"),
    "에있어": (r"에\s?있어(?:서)?\b", "번역투"),
    "이중피동": (r"되어지|되어진|지게 되", "번역투"),
    "를통해": (r"(?:을|를)\s?통해", "번역투 (몰리면)"),
    "에대해": (r"에\s?대(?:해|한)", "번역투 (몰리면)"),
    "다음과같": (r"다음과 같", "열거 도입"),
    "광고어": (r"혁신|획기|완벽|강력한|압도|놀라운|게임 ?체인저", "광고 문구"),
    "강조부사": (r"정말|매우|대단히|굉장히|너무나", "겹치는 수식"),
    "볼드": (r"\*\*", "마크다운 볼드"),
    "헤딩": (r"(?m)^#{1,6}\s", "마크다운 헤딩"),
    "화살표": (r"→|⇒", "화살표 기호"),
    "핵심은": (r"핵심은|중요한 (?:것|건|점)은|관건은", "격언·주어 돌림"),
    "결론적으로": (r"결론적으로|요약하면|정리하자면|종합하면", "AI 관용구"),
    "시사": (r"시사하는 바|주목할 만|눈여겨볼", "내용 없는 상투구"),
}

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


def sentences(text):
    parts = re.split(r"(?<=[.!?。])\s+|\n+", text)
    return [p.strip() for p in parts if len(p.strip()) > 1]


def ending(s):
    s = s.rstrip(" .!?)\"'")
    if re.search(r"(?:요|죠)$", s):
        return "해요"
    if re.search(r"(?:니다|니까)$", s):
        return "합쇼"
    if re.search(r"다$", s):
        return "해라"
    return "기타"


def main(path, orig=None):
    text = open(path, encoding="utf-8").read()
    print(f"# {path}")
    for name, (rx, why) in PATTERNS.items():
        hits = [m.start() for m in re.finditer(rx, text)]
        if hits:
            ctx = [text[max(0, h - 12): h + 14].replace("\n", " ") for h in hits[:3]]
            print(f"  {name:10} {len(hits)}회  ({why})  예: {' | '.join(ctx)}")
    em = EMOJI.findall(text)
    if em:
        print(f"  이모지     {len(em)}개  {''.join(em[:10])}")
    ss = sentences(text)
    ends = [ending(s) for s in ss]
    kinds = {k: ends.count(k) for k in set(ends)}
    print(f"  문장 {len(ss)}개 · 어미 {kinds}")
    run, best, prev = 1, 1, None
    for e in ends:
        run = run + 1 if e == prev else 1
        best, prev = max(best, run), e
    print(f"  같은 어미 최장 연속 {best}")
    lens = [len(s) for s in ss]
    if len(lens) > 2:
        print(f"  문장 길이 평균 {mean(lens):.0f}자 · 표준편차 {pstdev(lens):.0f} · 변동계수 {pstdev(lens)/mean(lens):.2f}")
    # 명령·URL처럼 한글이 없는 줄은 문장 줄이 아니므로 줄 지표에서 뺀다
    lines = [l.strip() for l in text.splitlines() if re.search("[가-힣]", l)]
    if len(lines) > 3:
        single = sum(1 for l in lines if len(sentences(l.replace(". ", ".\n"))) == 1)
        ll = [len(l) for l in lines]
        print(f"  줄 {len(lines)}개 · 한 줄 한 문장 {single/len(lines):.0%} · 줄 길이 변동계수 {pstdev(ll)/mean(ll):.2f}"
              "  (한 줄 한 문장이 대부분이고 변동계수가 낮으면 줄을 같은 틀로 채운 것 — F2)")
    if orig:
        o = open(orig, encoding="utf-8").read()
        nums = lambda t: set(re.findall(r"\d[\d,.]*%?", t))
        lost, added = nums(o) - nums(text), nums(text) - nums(o)
        strip = lambda t: len(re.sub(r"[#*|>\-\s]", "", t))
        print(f"  분량 {strip(text)/max(1, strip(o)):.0%} · 사라진 숫자 {sorted(lost) or '없음'} · 새 숫자 {sorted(added) or '없음'}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
