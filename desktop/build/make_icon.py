"""Generate the app icon (build/icon.png, build/icon.ico, assets/icon.png). Run with the project venv."""
from pathlib import Path

from PIL import Image, ImageDraw

S = 1024
here = Path(__file__).resolve().parent

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([40, 40, S - 40, S - 40], radius=220, fill=(27, 103, 255, 255))

# Annotation bounding-box corners
def box(x0, y0, x1, y1):
    d.rectangle([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill="white")


w, m, L = 44, 190, 170  # stroke width, margin, arm length
for x, y, dx, dy in [(m, m, 1, 1), (S - m, m, -1, 1), (m, S - m, 1, -1), (S - m, S - m, -1, -1)]:
    box(x, y, x + dx * L, y + dy * w)  # horizontal arm
    box(x, y, x + dx * w, y + dy * L)  # vertical arm

# Play triangle
c = S // 2
d.polygon([(c - 120, c - 170), (c - 120, c + 170), (c + 180, c)], fill="white")

img = img.resize((512, 512), Image.LANCZOS)
img.save(here / "icon.png")
img.save(here / "icon.ico", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
(here.parent / "assets").mkdir(exist_ok=True)
img.save(here.parent / "assets" / "icon.png")
print("icons written")
