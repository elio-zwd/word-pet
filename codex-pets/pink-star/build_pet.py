from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
ACTIONS = ROOT / "actions"
CELL_W, CELL_H = 192, 208
COLS = 8
SCALE = 3


def blank() -> Image.Image:
    return Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))


def _ellipse(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], fill, outline=None, width=1):
    draw.ellipse(tuple(round(v * SCALE) for v in box), fill=fill, outline=outline, width=width * SCALE)


def _line(draw: ImageDraw.ImageDraw, points: Iterable[tuple[float, float]], fill, width: int):
    draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points], fill=fill, width=width * SCALE)


def character(
    *,
    facing: int = 1,
    squash_x: float = 1.0,
    squash_y: float = 1.0,
    angle: float = 0.0,
    dx: int = 0,
    dy: int = 0,
    mood: str = "normal",
    arm_wave: float = 0.0,
    cue: str | None = None,
) -> Image.Image:
    hi = Image.new("RGBA", (CELL_W * SCALE, CELL_H * SCALE), (0, 0, 0, 0))
    d = ImageDraw.Draw(hi)

    _ellipse(d, (54, 174, 140, 190), (0, 0, 0, 48))

    cx, cy = 96 + dx, 113 + dy
    body_w, body_h = 118 * squash_x, 110 * squash_y
    left, top = cx - body_w / 2, cy - body_h / 2
    right, bottom = cx + body_w / 2, cy + body_h / 2

    back = (41, 130, 91, 183) if facing > 0 else (101, 130, 151, 183)
    front = (111, 137, 178, 190) if facing > 0 else (14, 137, 81, 190)
    _ellipse(d, back, (177, 28, 65, 255), (125, 16, 42, 255), 2)

    wave = arm_wave * facing
    arm_left = (left - 14 - max(0, -wave), top + 25 - abs(wave) * 0.6, left + 25, top + 74)
    arm_right = (right - 25, top + 27 - abs(max(0, wave)) * 0.6, right + 14 + max(0, wave), top + 75)
    _ellipse(d, arm_left, (239, 91, 157, 255), (194, 55, 116, 255), 2)
    _ellipse(d, arm_right, (239, 91, 157, 255), (194, 55, 116, 255), 2)

    body_fill = (245, 128, 184, 255)
    if mood == "dim":
        body_fill = (198, 94, 139, 255)
    elif mood == "work":
        body_fill = (250, 121, 175, 255)
    elif mood == "review":
        body_fill = (238, 132, 192, 255)
    _ellipse(d, (left, top, right, bottom), body_fill, (201, 70, 133, 255), 2)
    _ellipse(d, front, (202, 35, 76, 255), (135, 18, 45, 255), 2)

    face_shift = 8 * facing
    ex1 = cx - 17 + face_shift
    ex2 = cx + 15 + face_shift
    ey = cy - 17
    for ex in (ex1, ex2):
        _ellipse(d, (ex - 8, ey - 19, ex + 8, ey + 22), (8, 11, 27, 255), (42, 4, 33, 255), 2)
        _ellipse(d, (ex - 5, ey - 15, ex + 4, ey - 2), (248, 252, 255, 255))
        _ellipse(d, (ex - 4, ey + 8, ex + 5, ey + 18), (32, 91, 223, 255))

    _ellipse(d, (cx - 38 + face_shift, cy + 10, cx - 19 + face_shift, cy + 22), (244, 83, 161, 180))
    _ellipse(d, (cx + 28 + face_shift, cy + 10, cx + 47 + face_shift, cy + 22), (244, 83, 161, 180))

    if mood == "failed":
        _line(d, ((cx - 3 + face_shift, cy + 28), (cx + 5 + face_shift, cy + 23), (cx + 12 + face_shift, cy + 28)), (119, 14, 45, 255), 3)
    else:
        _ellipse(d, (cx + face_shift - 5, cy + 23, cx + face_shift + 6, cy + 36), (145, 17, 48, 255))
        _ellipse(d, (cx + face_shift - 2, cy + 30, cx + face_shift + 4, cy + 36), (255, 91, 112, 255))

    if cue == "wait":
        for index, radius in enumerate((3, 4, 5)):
            _ellipse(d, (139 + index * 12 - radius, 45 - index * 7 - radius, 139 + index * 12 + radius, 45 - index * 7 + radius), (255, 255, 255, 230), (90, 70, 110, 220), 1)
    elif cue == "work":
        for index in range(3):
            _line(d, ((145, 48 + index * 12), (171, 44 + index * 12)), (52, 113, 246, 225), 3)
    elif cue == "review":
        _ellipse(d, (144, 36, 166, 58), (0, 0, 0, 0), (55, 95, 160, 235), 4)
        _line(d, ((161, 55), (174, 69)), (55, 95, 160, 235), 4)
    elif cue == "failed":
        points = []
        for index in range(10):
            radius = 11 if index % 2 == 0 else 5
            theta = -math.pi / 2 + index * math.pi / 5
            points.append((151 + radius * math.cos(theta), 42 + radius * math.sin(theta)))
        d.polygon([(round(x * SCALE), round(y * SCALE)) for x, y in points], fill=(255, 216, 70, 235), outline=(170, 100, 20, 230))

    if angle:
        hi = hi.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False, center=(cx * SCALE, cy * SCALE))
    return hi.resize((CELL_W, CELL_H), Image.Resampling.LANCZOS)


def build_rows() -> tuple[list[list[Image.Image]], list[Image.Image]]:
    rows: list[list[Image.Image]] = []

    idle = []
    for i in range(6):
        phase = 2 * math.pi * i / 6
        idle.append(character(squash_x=1 + 0.018 * math.sin(phase), squash_y=1 - 0.018 * math.sin(phase), dy=round(-2 * math.sin(phase))))
    rows.append(idle + [character(), blank()])

    right, left = [], []
    for i in range(8):
        phase = 2 * math.pi * i / 8
        sx = 1 + 0.05 * math.cos(phase * 2)
        sy = 1 - 0.06 * math.cos(phase * 2)
        hop = round(-8 * abs(math.sin(phase)))
        right.append(character(facing=1, squash_x=sx, squash_y=sy, angle=-5 + 3 * math.sin(phase), dx=4 + round(5 * math.sin(phase)), dy=hop))
        left.append(character(facing=-1, squash_x=sx, squash_y=sy, angle=5 - 3 * math.sin(phase), dx=-4 - round(5 * math.sin(phase)), dy=hop))
    rows.extend([right, left])

    waving = [character(arm_wave=v, angle=a, dx=round(v / 4), dy=-2 if v else 0) for v, a in ((0, -3), (16, 4), (6, -2), (18, 5))]
    rows.append(waving + [blank() for _ in range(4)])

    jumping = [
        character(squash_x=1.08, squash_y=0.90, dy=4),
        character(squash_x=0.98, squash_y=1.07, dy=-13),
        character(squash_x=0.94, squash_y=1.10, dy=-29),
        character(squash_x=0.98, squash_y=1.05, dy=-15),
        character(squash_x=1.09, squash_y=0.89, dy=4),
    ]
    rows.append(jumping + [blank() for _ in range(3)])

    failed = []
    for i in range(8):
        t = i / 7
        failed.append(character(squash_x=1 - 0.10 * t, squash_y=1 - 0.08 * t, angle=5 + 32 * t, dx=round(12 * t), dy=round(8 * t), mood="failed" if i >= 2 else "dim", cue="failed" if i >= 4 else None))
    rows.append(failed)

    waiting, working, review = [], [], []
    for i in range(6):
        phase = 2 * math.pi * i / 6
        waiting.append(character(angle=2.5 * math.sin(phase), dx=round(2 * math.sin(phase)), dy=round(-2 * math.cos(phase)), cue="wait"))
        working.append(character(squash_x=1 + 0.025 * math.sin(phase * 2), squash_y=1 - 0.025 * math.sin(phase * 2), angle=-3 + 2 * math.sin(phase), dx=3, dy=round(-4 * abs(math.sin(phase))), mood="work", cue="work"))
        review.append(character(angle=3 * math.sin(phase), dx=round(2 * math.cos(phase)), dy=round(-2 * math.sin(phase)), mood="review", cue="review"))
    rows.extend([waiting + [blank(), blank()], working + [blank(), blank()], review + [blank(), blank()]])

    looks = []
    for i in range(16):
        theta = math.radians(i * 22.5)
        facing = 1 if math.cos(theta) >= 0 else -1
        looks.append(character(facing=facing, dx=round(5 * math.cos(theta)), dy=round(4 * math.sin(theta)), angle=round(2.2 * math.cos(theta), 2)))
    rows.extend([looks[:8], looks[8:]])
    return rows, looks


def make_sheet(rows: list[list[Image.Image]], row_count: int) -> Image.Image:
    sheet = Image.new("RGBA", (CELL_W * COLS, CELL_H * row_count), (0, 0, 0, 0))
    for row in range(row_count):
        for col in range(COLS):
            sheet.alpha_composite(rows[row][col], (col * CELL_W, row * CELL_H))
    return sheet


def save_gif(name: str, frames: list[Image.Image], duration: int) -> None:
    frames[0].save(ACTIONS / f"{name}.gif", save_all=True, append_images=frames[1:], duration=duration, loop=0, disposal=2)


def main() -> None:
    ACTIONS.mkdir(parents=True, exist_ok=True)
    rows, looks = build_rows()
    assert len(rows) == 11 and all(len(row) == 8 for row in rows)

    v2 = make_sheet(rows, 11)
    v1 = make_sheet(rows, 9)
    v2.save(ROOT / "spritesheet.png", optimize=True)
    v1.save(ROOT / "spritesheet-v1.png", optimize=True)

    specs = [
        ("idle", rows[0][:6], 180),
        ("running-right", rows[1], 85),
        ("running-left", rows[2], 85),
        ("waving", rows[3][:4], 150),
        ("jumping", rows[4][:5], 110),
        ("failed", rows[5], 120),
        ("waiting", rows[6][:6], 190),
        ("working", rows[7][:6], 110),
        ("review", rows[8][:6], 150),
        ("look-directions", looks, 120),
    ]
    for name, frames, duration in specs:
        save_gif(name, frames, duration)

    report = {
        "spriteVersionNumber": 2,
        "v2": {"file": "spritesheet.png", "size": list(v2.size), "grid": [8, 11]},
        "v1": {"file": "spritesheet-v1.png", "size": list(v1.size), "grid": [8, 9]},
        "cell": [CELL_W, CELL_H],
        "actions": [name for name, _, _ in specs],
    }
    (ROOT / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
