from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent
SEED = ROOT / "source" / "character-seed.png"
ACTIONS = ROOT / "actions"
CELL_W, CELL_H = 192, 208
COLS = 8


def fit_sprite(sprite: Image.Image, max_w: int = 168, max_h: int = 164) -> Image.Image:
    scale = min(max_w / sprite.width, max_h / sprite.height)
    return sprite.resize(
        (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))),
        Image.Resampling.LANCZOS,
    )


BASE = fit_sprite(Image.open(SEED).convert("RGBA"))


def tint(img: Image.Image, mode: str | None) -> Image.Image:
    if mode == "dim":
        return ImageEnhance.Brightness(img).enhance(0.72)
    if mode == "warm":
        overlay = Image.new("RGBA", img.size, (255, 90, 90, 20))
        return Image.alpha_composite(img, overlay)
    if mode == "cool":
        overlay = Image.new("RGBA", img.size, (70, 130, 255, 22))
        return Image.alpha_composite(img, overlay)
    return img


def render_frame(
    *,
    flip: bool = False,
    sx: float = 1.0,
    sy: float = 1.0,
    angle: float = 0.0,
    dx: int = 0,
    dy: int = 0,
    tint_mode: str | None = None,
    shadow_scale: float = 1.0,
    cue: str | None = None,
) -> Image.Image:
    canvas = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    sw = int(92 * shadow_scale)
    sh = int(18 * max(0.55, shadow_scale))
    cx, cy = CELL_W // 2 + dx, 185 + max(0, dy // 3)
    draw.ellipse((cx - sw // 2, cy - sh // 2, cx + sw // 2, cy + sh // 2), fill=(0, 0, 0, 55))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(5)))

    sprite = BASE.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if flip else BASE.copy()
    sprite = tint(sprite, tint_mode)
    sprite = sprite.resize(
        (max(1, round(sprite.width * sx)), max(1, round(sprite.height * sy))),
        Image.Resampling.LANCZOS,
    )
    if angle:
        sprite = sprite.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)

    x = (CELL_W - sprite.width) // 2 + dx
    y = 184 - sprite.height + dy
    canvas.alpha_composite(sprite, (x, y))

    if cue:
        draw = ImageDraw.Draw(canvas)
        if cue == "wait":
            for index, radius in enumerate((4, 5, 6)):
                px, py = 137 + index * 12, 42 - index * 5
                draw.ellipse(
                    (px - radius, py - radius, px + radius, py + radius),
                    fill=(255, 255, 255, 225),
                    outline=(90, 70, 110, 190),
                    width=2,
                )
        elif cue == "work":
            for index in range(3):
                y0 = 50 + index * 12
                draw.line((143, y0, 169, y0 - 4), fill=(70, 130, 255, 210), width=4)
        elif cue == "review":
            draw.ellipse((142, 38, 166, 62), outline=(55, 95, 160, 230), width=5)
            draw.line((161, 58, 174, 72), fill=(55, 95, 160, 230), width=5)
        elif cue == "failed":
            points = []
            for index in range(10):
                radius = 11 if index % 2 == 0 else 5
                theta = -math.pi / 2 + index * math.pi / 5
                points.append((151 + radius * math.cos(theta), 43 + radius * math.sin(theta)))
            draw.polygon(points, fill=(255, 215, 70, 230), outline=(170, 100, 20, 220))
    return canvas


def blank() -> Image.Image:
    return Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))


def build_rows() -> tuple[list[list[Image.Image]], list[Image.Image]]:
    rows: list[list[Image.Image]] = []

    idle = []
    for index in range(6):
        phase = 2 * math.pi * index / 6
        idle.append(
            render_frame(
                sx=1.0 + 0.015 * math.sin(phase),
                sy=1.0 - 0.012 * math.sin(phase),
                dy=round(-2 * math.sin(phase)),
                shadow_scale=1.0 - 0.05 * math.sin(phase),
            )
        )
    rows.append(idle + [render_frame(), blank()])

    running_right = []
    running_left = []
    for index in range(8):
        phase = 2 * math.pi * index / 8
        common = {
            "sx": 1.0 + 0.045 * math.cos(phase * 2),
            "sy": 1.0 - 0.055 * math.cos(phase * 2),
            "dy": round(-7 * abs(math.sin(phase))),
            "shadow_scale": 0.90 + 0.08 * abs(math.sin(phase)),
        }
        running_right.append(
            render_frame(
                **common,
                angle=-5 + 3 * math.sin(phase),
                dx=4 + round(5 * math.sin(phase)),
                cue="work" if index in (1, 5) else None,
            )
        )
        running_left.append(
            render_frame(
                **common,
                flip=True,
                angle=5 - 3 * math.sin(phase),
                dx=-4 - round(5 * math.sin(phase)),
            )
        )
    rows.extend([running_right, running_left])

    waving = [
        render_frame(angle=-5, dx=-2),
        render_frame(angle=4, dx=2, dy=-3),
        render_frame(angle=-3, dx=-1, dy=-1),
        render_frame(angle=6, dx=3, dy=-3),
    ]
    rows.append(waving + [blank() for _ in range(4)])

    jump_params = [
        (1.07, 0.92, 0, 5),
        (0.96, 1.07, -14, 0),
        (0.93, 1.10, -30, -2),
        (0.98, 1.04, -16, 0),
        (1.09, 0.90, 3, 7),
    ]
    jumping = [
        render_frame(sx=sx, sy=sy, dy=dy, angle=angle, shadow_scale=max(0.55, 1 + dy / 55))
        for sx, sy, dy, angle in jump_params
    ]
    rows.append(jumping + [blank() for _ in range(3)])

    failed = []
    for index in range(8):
        progress = index / 7
        failed.append(
            render_frame(
                sx=1.0 - 0.10 * progress,
                sy=1.0 - 0.08 * progress,
                angle=5 + 34 * progress,
                dx=round(12 * progress),
                dy=round(8 * progress),
                tint_mode="dim" if index >= 3 else None,
                shadow_scale=1.0 + 0.12 * progress,
                cue="failed" if index >= 4 else None,
            )
        )
    rows.append(failed)

    waiting = []
    working = []
    review = []
    for index in range(6):
        phase = 2 * math.pi * index / 6
        waiting.append(
            render_frame(
                angle=2.5 * math.sin(phase),
                dx=round(2 * math.sin(phase)),
                dy=round(-2 * math.cos(phase)),
                cue="wait",
            )
        )
        working.append(
            render_frame(
                sx=1.0 + 0.025 * math.sin(phase * 2),
                sy=1.0 - 0.025 * math.sin(phase * 2),
                angle=-3 + 2 * math.sin(phase),
                dx=3,
                dy=round(-4 * abs(math.sin(phase))),
                tint_mode="warm" if index % 2 == 0 else None,
                cue="work",
            )
        )
        review.append(
            render_frame(
                angle=3 * math.sin(phase),
                dx=round(2 * math.cos(phase)),
                dy=round(-2 * math.sin(phase)),
                tint_mode="cool" if index in (1, 2, 4, 5) else None,
                cue="review",
            )
        )
    rows.extend(
        [
            waiting + [blank(), blank()],
            working + [blank(), blank()],
            review + [blank(), blank()],
        ]
    )

    look_frames = []
    for index in range(16):
        theta = math.radians(index * 22.5)
        look_frames.append(
            render_frame(
                dx=round(5 * math.cos(theta)),
                dy=round(4 * math.sin(theta)),
                angle=round(2.2 * math.cos(theta), 2),
                flip=math.cos(theta) < -0.15,
                shadow_scale=0.98,
            )
        )
    rows.extend([look_frames[:8], look_frames[8:]])
    return rows, look_frames


def make_sheet(rows: list[list[Image.Image]], row_count: int) -> Image.Image:
    sheet = Image.new("RGBA", (CELL_W * COLS, CELL_H * row_count), (0, 0, 0, 0))
    for row in range(row_count):
        for column in range(COLS):
            sheet.alpha_composite(rows[row][column], (column * CELL_W, row * CELL_H))
    return sheet


def save_gif(name: str, frames: list[Image.Image], duration: int) -> None:
    frames[0].save(
        ACTIONS / f"{name}.gif",
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        disposal=2,
        transparency=0,
    )


def main() -> None:
    ACTIONS.mkdir(parents=True, exist_ok=True)
    rows, look_frames = build_rows()
    assert len(rows) == 11 and all(len(row) == 8 for row in rows)

    v2 = make_sheet(rows, 11)
    v1 = make_sheet(rows, 9)
    v2.save(ROOT / "spritesheet.webp", "WEBP", quality=78, method=4)
    v1.quantize(colors=128, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(
        ROOT / "spritesheet-v1.png", optimize=True, compress_level=9
    )

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
        ("look-directions", look_frames, 120),
    ]
    for name, frames, duration in specs:
        save_gif(name, frames, duration)

    report = {
        "spriteVersionNumber": 2,
        "v2": {"file": "spritesheet.webp", "size": list(v2.size), "grid": [8, 11]},
        "v1": {"file": "spritesheet-v1.png", "size": list(v1.size), "grid": [8, 9]},
        "cell": [CELL_W, CELL_H],
        "actions": [name for name, _, _ in specs],
    }
    (ROOT / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
