#!/usr/bin/env python3
"""
Добавляет цифру-бейдж поверх иконки блока WeDo2 (iconURI, inline base64 PNG)
прямо внутри src/vm/extensions/block/index.js, не трогая текст блоков.

Использование:
    python3 add_badge.py src/vm/extensions/block/index.js 3
"""
import sys, re, base64, io

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Нужен Pillow: pip install Pillow --break-system-packages")
    sys.exit(1)

path = sys.argv[1]
digit = sys.argv[2] if len(sys.argv) > 2 else '3'

src = open(path, encoding='utf-8').read()

m = re.search(r"iconURI\s*=\s*'(data:image/png;base64,[^']+)'", src)
if not m:
    print("Не нашёл iconURI вида  const iconURI = 'data:image/png;base64,...';")
    sys.exit(1)

data_url = m.group(1)
b64 = data_url.split(',', 1)[1]
raw = base64.b64decode(b64)

img = Image.open(io.BytesIO(raw)).convert('RGBA')
w, h = img.size
draw = ImageDraw.Draw(img)

badge_r = int(min(w, h) * 0.34)
cx, cy = int(w * 0.80), int(h * 0.80)
draw.ellipse(
    [cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r],
    fill=(220, 40, 40, 255),
    outline=(255, 255, 255, 255),
    width=max(2, badge_r // 8)
)

font = None
for fp in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
           "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"):
    try:
        font = ImageFont.truetype(fp, int(badge_r * 1.3))
        break
    except Exception:
        continue
if font is None:
    font = ImageFont.load_default()

bbox = draw.textbbox((0, 0), digit, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), digit, fill=(255, 255, 255, 255), font=font)

out = io.BytesIO()
img.save(out, format='PNG')
new_b64 = base64.b64encode(out.getvalue()).decode('ascii')
new_data_url = f'data:image/png;base64,{new_b64}'

src = src[:m.start(1)] + new_data_url + src[m.end(1):]
open(path, 'w', encoding='utf-8').write(src)
print(f'Готово: иконка помечена цифрой "{digit}"')