# Build the interactive K2O festival map from Pun's layered Illustrator file.
#
# The .ai is saved with PDF compatibility, so each Illustrator layer is a PDF
# optional-content group. This script renders each layer on its own, crops the
# map area (the headline moves to the side panel), finds every map pin and
# classifies it by template-matching it against the icons in the map's own
# legend, then writes:
#   public/media/01-k2o-map-{bg,aw,pins,exits,sponsors}-{1200,2400}.webp
#   public/media/01-k2o-map-headline-{480,960}.webp
#   public/media/01-k2o-map-icons.webp       legend icons, one 64x80 cell each
#   src/data/k2o-map.json                    pin positions + categories
#
# usage:
#   pip install pymupdf opencv-python-headless scipy pillow
#   python scripts/map/build-k2o-map.py assets-src/map/k2o_festival-map_4x5.ai
import json
import sys

import cv2
import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage

SRC = sys.argv[1]
MEDIA, DATA = 'public/media', 'src/data/k2o-map.json'

PAGE_W, PAGE_H = 2000, 2500
CROP = (0, 160, 2000, 2400)  # map area in pt; the headline (top) moves to the panel
LEGEND_TOP, LEGEND_LEFT = 2150, 1140  # legend block in the pin layer, bottom right

# Illustrator layer name -> our id, bottom to top (the stacking order in the file)
LAYERS = [('map/bg', 'bg'), ('aw', 'aw'), ('Map pin', 'pins'), ('Emergency Exit', 'exits'), ('K2O sponsors', 'sponsors'), ('headline', 'headline')]

# Legend icons (pt boxes) and labels exactly as printed in the legend, in its column order
LEGEND = [
    ('top-up', 'Top up', (1170, 2170, 1207, 2223)),
    ('first-aid', 'First aid', (1169, 2244, 1208, 2296)),
    ('food', 'Food zone', (1170, 2317, 1207, 2370)),
    ('locker', 'Locker', (1166, 2390, 1207, 2447)),
    ('toilet', 'Toilet', (1340, 2172, 1376, 2222)),
    ('atm', 'ATM', (1338, 2244, 1378, 2296)),
    ('mart', 'S2O Mart', (1338, 2318, 1378, 2370)),
    ('wristband', 'Wristband pickup', (1339, 2391, 1378, 2443)),
    ('bar', 'Bar', (1486, 2170, 1524, 2223)),
    ('pickup', 'Pick-up / drop off', (1486, 2244, 1525, 2296)),
    ('info', 'Information', (1488, 2316, 1525, 2369)),
    ('media', 'Media', (1486, 2391, 1525, 2443)),
    ('smoking', 'Smoking area', (1650, 2170, 1688, 2223)),
    ('charger', 'Charger', (1650, 2240, 1692, 2296)),
    ('lost-found', 'Lost & found', (1650, 2318, 1690, 2370)),
    ('meeting', 'Meeting point', (1650, 2391, 1690, 2443)),
    ('security', 'Security', (1807, 2170, 1846, 2223)),
    ('help-desk', 'Help desk', (1806, 2244, 1844, 2296)),
    ('walkway', 'Walk way', (1807, 2318, 1846, 2370)),
]
EXIT_ICON = (1807, 2397, 1849, 2439)
# Pins that are on the map but not in the legend: left out rather than guessed.
IGNORE = [(750, 624)]  # navy "e" pin near the wristband pickup

doc0 = pymupdf.open(SRC)
OCG = {v['name']: x for x, v in doc0.get_ocgs().items()}


def render(layer, scale):
    """RGBA render of one Illustrator layer (all other layers switched off)."""
    d = pymupdf.open(SRC)
    cat = d.pdf_catalog()
    on = OCG[layer]
    d.xref_set_key(cat, 'OCProperties/D/ON', f'[{on} 0 R]')
    d.xref_set_key(cat, 'OCProperties/D/OFF', '[' + ' '.join(f'{x} 0 R' for x in OCG.values() if x != on) + ']')
    pm = pymupdf.open('pdf', d.tobytes())[0].get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=True)
    return Image.frombytes('RGBA', (pm.width, pm.height), pm.samples)


def crop_pt(im, box, k):
    return im.crop(tuple(round(v * k) for v in box))


def blobs(alpha, k, min_pt):
    lab, _ = ndimage.label(ndimage.binary_dilation(alpha, iterations=3))
    out = []
    for s in ndimage.find_objects(lab):
        y0, y1, x0, x1 = s[0].start / k, s[0].stop / k, s[1].start / k, s[1].stop / k
        if (x1 - x0) * (y1 - y0) >= min_pt ** 2:
            out.append((x0, y0, x1, y1))
    return out


# 1. layers: 2400 px wide master (k = 1.2 px/pt) and 1200 px
K = 2400 / PAGE_W
masters = {}
for name, lid in LAYERS:
    im = render(name, K)
    if lid == 'pins':  # the legend moves to the panel
        a = np.array(im)
        a[round(LEGEND_TOP * K):, round(LEGEND_LEFT * K):] = 0
        im = Image.fromarray(a)
    if lid == 'headline':
        im = im.crop(im.getbbox())
        headline = {'w': im.width, 'h': im.height}
        for w in (480, 960):
            im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(f'{MEDIA}/01-k2o-map-headline-{w}.webp', quality=90, method=6)
        continue
    im = crop_pt(im, CROP, K)
    masters[lid] = im
    for w in (1200, 2400):
        r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        (r.convert('RGB') if lid == 'bg' else r).save(f'{MEDIA}/01-k2o-map-{lid}-{w}.webp', quality=82 if lid == 'bg' else 86, method=6)
    print('layer', lid, im.size)

# 2. pins: match each blob of the pin layer against the legend icons (the round head part)
k = 2
pins_rgba = np.array(render('Map pin', k)).astype(np.float32)
a = pins_rgba[..., 3:4] / 255
flat = (pins_rgba[..., :3] * a + 40 * (1 - a)).astype(np.uint8)  # over dark grey
heads = {}
for cid, _, (x0, y0, x1, y1) in LEGEND:
    t = flat[y0 * k:y1 * k, x0 * k:x1 * k]
    heads[cid] = t[: int(t.shape[0] * 0.62)]
scales = [0.93, 1.0, 1.08, 1.18, 1.28, 1.4, 1.55, 1.75, 1.95, 2.2, 2.5]
cands = []
for x0, y0, x1, y1 in blobs(pins_rgba[..., 3] > 20, k, 30):
    if y0 >= LEGEND_TOP - 10:
        continue
    P = 12
    X0, Y0 = max(0, int(x0 * k) - P), max(0, int(y0 * k) - P)
    win = flat[Y0:int(y1 * k) + P, X0:int(x1 * k) + P]
    for cid, h in heads.items():
        for sc in scales:
            th = cv2.resize(h, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
            if th.shape[0] > win.shape[0] or th.shape[1] > win.shape[1]:
                continue
            r = cv2.matchTemplate(win, th, cv2.TM_CCOEFF_NORMED)
            peak = (r == cv2.dilate(r, np.ones((9, 9), np.uint8))) & (r > 0.55)
            for y, x in zip(*np.where(peak)):
                cands.append((float(r[y, x]), cid, (X0 + x) / k, (Y0 + y) / k, th.shape[1] / k, th.shape[0] / k / 0.62))
cands.sort(reverse=True)
pins = []
for sc, cid, x, y, w, h in cands:  # best match wins, overlapping weaker matches drop out
    cx, cy = x + w / 2, y + h / 2
    if all(abs(cx - (p[2] + p[4] / 2)) > max(w, p[4]) * 0.5 or abs(cy - (p[3] + p[5] / 2)) > max(h, p[5]) * 0.5 for p in pins):
        pins.append((sc, cid, x, y, w, h))
pins = [p for p in pins if not any(abs(p[2] - ix) < 10 and abs(p[3] - iy) < 10 for ix, iy in IGNORE)]
pins.sort(key=lambda p: (p[3], p[2]))
print(len(pins), 'pins')

# 3. exits and sponsor markers are whole layers: just count them
counts = {cid: sum(p[1] == cid for p in pins) for cid, _, _ in LEGEND}
counts['exits'] = len(blobs(np.array(masters['exits'])[..., 3] > 20, K, 12))
spons = blobs(np.array(masters['sponsors'])[..., 3] > 20, K, 12)

# 4. icon sprite (64x80 px cells): legend icons, exit icon, one sponsor marker
CW, CH = 64, 80
legend_im = Image.fromarray(np.array(render('Map pin', 4)))
icons = [crop_pt(legend_im, box, 4) for _, _, box in LEGEND] + [crop_pt(legend_im, EXIT_ICON, 4)]
sx0, sy0, sx1, sy1 = min(spons, key=lambda b: b[1])
icons.append(masters['sponsors'].crop(tuple(round(v * K) for v in (sx0, sy0, sx1, sy1))))
sheet = Image.new('RGBA', (CW * len(icons), CH))
for i, ic in enumerate(icons):
    ic = ic.crop(ic.getbbox())
    f = min((CW - 4) / ic.width, (CH - 4) / ic.height)
    ic = ic.resize((max(1, round(ic.width * f)), max(1, round(ic.height * f))), Image.LANCZOS)
    sheet.alpha_composite(ic, (i * CW + (CW - ic.width) // 2, (CH - ic.height) // 2))
sheet.save(f'{MEDIA}/01-k2o-map-icons.webp', quality=92, method=6)

# 5. data
cw, ch = CROP[2] - CROP[0], CROP[3] - CROP[1]
pct = lambda v, total: round(v / total * 100, 3)
cats = [{'id': cid, 'label': label, 'icon': i, 'kind': 'pins', 'count': counts[cid]} for i, (cid, label, _) in enumerate(LEGEND) if counts[cid]]
cats.append({'id': 'exits', 'label': 'Emergency exit', 'icon': len(LEGEND), 'kind': 'layer', 'count': counts['exits']})
# sponsor markers in the food zone touch each other, so no reliable count for them
cats.append({'id': 'sponsors', 'label': 'Sponsors', 'icon': len(LEGEND) + 1, 'kind': 'layer', 'count': None})
data = {
    'source': 'k2o_festival-map_4x5.ai',
    'width': cw,
    'height': ch,
    'headline': headline,
    'iconCell': [CW, CH],
    'iconCount': len(icons),
    'layers': [{'id': lid, 'name': name} for name, lid in LAYERS],
    'categories': cats,
    'pins': [{'cat': cid, 'x': pct(x - CROP[0], cw), 'y': pct(y - CROP[1], ch), 'w': pct(w, cw), 'h': pct(h, ch)} for _, cid, x, y, w, h in pins],
}
json.dump(data, open(DATA, 'w'), indent=1)
print('categories', {c['id']: c['count'] for c in cats})
