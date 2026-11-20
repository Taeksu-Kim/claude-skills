"""색 체계 도구 (ui-design topics/color.md). 표준 라이브러리 + (area 만) Pillow.

  python palette.py scale --hue 171 --chroma 0.07 [--neutral-hue 171 --neutral-chroma 0.02]
      주 색 1벌과 회색 1벌을 OKLCH 밝기 단계(0~10)로 만든다. 회색 채도는 단계마다 비율로 (바탕 쪽 거의 0, 가운데가 가장 큼).
  python palette.py roles --hue 171 --chroma 0.07 --neutral-hue 171 --neutral-chroma 0.02 [--css]
      단계에서 역할(바탕·면·선·글자·주 색)을 고르고 역할 쌍 대비를 함께 낸다. --css 면 :root 변수로.
  python palette.py check '#ffffff' '#1d5646' ...      두 색씩 짝지어 WCAG 대비
  python palette.py info '#3182f6' ...                 OKLCH (L, C, H)
  python palette.py area shot.png [--top 8]            스크린샷의 색 면적 비율 (비슷한 색끼리 묶음)
"""
import argparse, math, sys

def _lin(c): c /= 255; return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def _gam(x): x = max(0.0, min(1.0, x)); return round(255 * (12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055))
def rgb(h): h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]
def hexs(r): return '#%02x%02x%02x' % tuple(r)

def oklch(h):
    r, g, b = [_lin(c) for c in rgb(h)]
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360

def from_oklch(L, C, H):
    """범위 밖(sRGB에 없는 색)이면 채도를 줄여 맞춘다."""
    for _ in range(40):
        a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
        l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
        m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
        s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
        rr = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
        gg = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
        bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
        if all(-1e-4 <= x <= 1 + 1e-4 for x in (rr, gg, bl)):
            return hexs([_gam(x) for x in (rr, gg, bl)])
        C *= 0.92
    return hexs([_gam(x) for x in (rr, gg, bl)])

def lum(h): r, g, b = [_lin(c) for c in rgb(h)]; return 0.2126 * r + 0.7152 * g + 0.0722 * b
def contrast(a, b): x, y = sorted([lum(a), lum(b)]); return (y + 0.05) / (x + 0.05)

# 밝기 단계 0~10 (0 = 가장 밝은 바탕). TDS·SEED 회색 측정(2026-11-20)과 비슷한 간격.
STEPS_L = [0.985, 0.965, 0.935, 0.895, 0.845, 0.75, 0.63, 0.53, 0.43, 0.33, 0.23]
# 회색 채도 비율: 바탕 쪽은 거의 0, 가운데가 가장 크다 (TDS: 0.002 → 0.028 → 0.020)
N_RATIO = [0.08, 0.12, 0.2, 0.32, 0.5, 0.75, 0.9, 1.0, 1.0, 0.95, 0.8]
# 주 색 채도 비율: 양 끝은 낮게
B_RATIO = [0.12, 0.22, 0.38, 0.58, 0.8, 0.95, 1.0, 1.0, 0.92, 0.82, 0.7]

def scales(hue, chroma, nhue, nchroma):
    neutral = [from_oklch(L, nchroma * k, nhue) for L, k in zip(STEPS_L, N_RATIO)]
    brand = [from_oklch(L, chroma * k, hue) for L, k in zip(STEPS_L, B_RATIO)]
    return neutral, brand

def roles(hue, chroma, nhue, nchroma, brand_step=None):
    n, b = scales(hue, chroma, nhue, nchroma)
    # 주 색: 흰 글자와 4.5:1 이상인 가장 밝은 단계 (지정하면 그 단계)
    bs = brand_step if brand_step is not None else next(i for i in range(5, 11) if contrast(b[i], '#ffffff') >= 4.5)
    R = {'--bg': n[1], '--panel': '#ffffff', '--panel-2': n[2], '--line': n[3], '--line-strong': n[4],
         '--text-3': n[7], '--text-2': n[8], '--text': n[10],
         '--brand': b[bs], '--brand-hover': b[min(bs + 1, 10)], '--brand-soft': b[1], '--brand-line': b[4], '--brand-ink': '#ffffff'}
    # 메타 글자는 바탕에서 4.5:1 — 모자라면 한 단계 어둡게. 보조 글자는 메타보다 한 단계 이상 진하게
    i3 = 7
    while contrast(n[i3], R['--bg']) < 4.5 and i3 < 9: i3 += 1
    R['--text-3'] = n[i3]; R['--text-2'] = n[max(8, i3 + 1)]
    pairs = [('--text', '--panel'), ('--text-2', '--panel'), ('--text-3', '--bg'), ('--text-3', '--panel-2'),
             ('--brand-ink', '--brand'), ('--brand', '--panel'), ('--brand', '--brand-soft')]
    return R, [(a, c, round(contrast(R[a], R[c]), 2)) for a, c in pairs], n, b, bs

def area(path, top=8):
    from PIL import Image
    im = Image.open(path).convert('RGB'); im.thumbnail((480, 480))
    px = list(im.get_flattened_data() if hasattr(im, 'get_flattened_data') else im.getdata()); tot = len(px); buckets = {}
    for r, g, b in px:   # 비슷한 색끼리 (채널 12단계로 묶음)
        k = (r // 22, g // 22, b // 22); e = buckets.setdefault(k, [0, 0, 0, 0]); e[0] += 1; e[1] += r; e[2] += g; e[3] += b
    out = sorted(buckets.values(), reverse=True)[:top]
    return [(hexs([e[1] // e[0], e[2] // e[0], e[3] // e[0]]), round(100 * e[0] / tot, 1)) for e in out]

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    for c in ('scale', 'roles'):
        p = sp.add_parser(c); p.add_argument('--hue', type=float, required=True); p.add_argument('--chroma', type=float, required=True)
        p.add_argument('--neutral-hue', type=float); p.add_argument('--neutral-chroma', type=float, default=0.012)
        p.add_argument('--brand-step', type=int); p.add_argument('--css', action='store_true')
    p = sp.add_parser('check'); p.add_argument('colors', nargs='+')
    p = sp.add_parser('info'); p.add_argument('colors', nargs='+')
    p = sp.add_parser('area'); p.add_argument('png'); p.add_argument('--top', type=int, default=8)
    a = ap.parse_args()
    if a.cmd in ('scale', 'roles'):
        nh = a.hue if a.neutral_hue is None else a.neutral_hue
        if a.cmd == 'scale':
            n, b = scales(a.hue, a.chroma, nh, a.neutral_chroma)
            print('neutral', ' '.join(f'{i}:{h}' for i, h in enumerate(n))); print('brand  ', ' '.join(f'{i}:{h}' for i, h in enumerate(b)))
        else:
            R, pairs, n, b, bs = roles(a.hue, a.chroma, nh, a.neutral_chroma, a.brand_step)
            if a.css: print(':root { ' + ' '.join(f'{k}: {v};' for k, v in R.items()) + ' }')
            else: [print(f'{k:14} {v}') for k, v in R.items()]
            print('/* 대비 */ ' + ' · '.join(f'{x} on {y} {c}' for x, y, c in pairs), file=sys.stderr)
    elif a.cmd == 'check':
        cs = a.colors
        for i in range(0, len(cs) - 1, 2): print(cs[i], cs[i + 1], round(contrast(cs[i], cs[i + 1]), 2))
    elif a.cmd == 'info':
        for h in a.colors: L, C, H = oklch(h); print(f'{h} L{L:.3f} C{C:.3f} H{H:.0f}')
    elif a.cmd == 'area':
        for h, p in area(a.png, a.top): print(f'{h} {p}%')
