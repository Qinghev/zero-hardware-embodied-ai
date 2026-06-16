from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "video_01"
FRAMES_DIR = CONTENT_DIR / "final_frames"
CLIPS_DIR = CONTENT_DIR / "final_clips"
EXPORTS_DIR = ROOT / "exports"
WIDTH = 1920
HEIGHT = 1080
FPS = 30


@dataclass
class Scene:
    title: str
    subtitle: str
    bullets: list[str]
    narration: str
    layout: str


SCENES = [
    Scene(
        title="先别急着买机械臂",
        subtitle="第一步，先看懂机器人数据",
        bullets=["不用真实机器人", "不用 GPU", "先跑通一个能展示的项目"],
        narration="想入门具身智能，先别急着买机械臂。真的，第一步没必要上硬件。你更应该先搞清楚：机器人数据到底长什么样。",
        layout="hook",
    ),
    Scene(
        title="这条视频只跑一个很小的项目",
        subtitle="公开数据 -> 可视化图 -> 作品集项目",
        bullets=["不训练大模型", "不控制真实机器人", "先生成几张能看懂的图"],
        narration="这条视频我就跑一个很小的项目。不用真实机器人，不用 GPU，也不用你先把 LeRobot 全家桶装明白。我们先用公开数据，生成几张能看懂的图。",
        layout="collage",
    ),
    Scene(
        title="先搞清楚这三个词",
        subtitle="episode / observation / action",
        bullets=["episode：一次任务轨迹", "observation：看到或感知到的状态", "action：轨迹里记录的动作"],
        narration="这个项目解决的不是怎么训练一个机器人。它解决的是更前面一步：episode 是什么，observation 是什么，action 又是什么。这些东西你不先搞清楚，后面看模仿学习和 VLA 会很虚。",
        layout="concept",
    ),
    Scene(
        title="入口我做了两个",
        subtitle="Colab 能用就点开跑；不稳定就跑本地轻量版",
        bullets=["Colab：适合快速试", "本地轻量版：不装 LeRobot", "先把结果跑出来"],
        narration="我这里做了两个入口。能用 Colab，就直接点开跑。如果 Colab 抽风，或者你网络不稳定，就跑本地轻量版。轻量版不装 LeRobot，只下载一个很小的数据文件，先把结果跑出来。",
        layout="github",
    ),
    Scene(
        title="Colab 不用选 GPU",
        subtitle="我们现在只是读数据、画图、看轨迹",
        bullets=["Runtime 选 None", "下载 PushT 小数据文件", "生成三张可视化图"],
        narration="Colab 里也不用选 GPU。这里选 None 就行。因为我们现在不是训练模型，只是读数据、画图、看轨迹。这一步普通电脑也能跑。",
        layout="colab",
    ),
    Scene(
        title="输出 1：episode 首帧",
        subtitle="先看这条轨迹大概在做什么",
        bullets=["PushT 是二维推块任务", "首帧帮助理解任务场景", "不需要真实相机或机械臂"],
        narration="跑完以后，第一张图是 episode 的首帧。你可以先看一下，这条轨迹大概在做什么。比如 PushT 这个任务，就是一个二维推块任务。",
        layout="first_frame",
    ),
    Scene(
        title="输出 2：action 随时间变化",
        subtitle="先把动作轨迹看懂",
        bullets=["横轴是时间", "纵轴是动作数值", "两条线对应两个动作维度"],
        narration="第二张图是 action 随时间变化。横轴是时间，纵轴是动作数值。这两条线可以理解成两个动作维度在整条轨迹里的变化。不用一上来就理解所有算法，先把数据看懂。",
        layout="timeseries",
    ),
    Scene(
        title="输出 3：action 分布",
        subtitle="看范围、集中区间和异常值",
        bullets=["动作集中在哪些区间", "有没有特别奇怪的值", "后面可以扩展到数据质量检查"],
        narration="第三张图是 action 分布。这个图很基础，但挺有用。你能看到动作主要集中在哪些区间，有没有特别奇怪的值。后面做数据质量检查，其实就是从这种东西扩展出去。",
        layout="distribution",
    ),
    Scene(
        title="为什么这能写进简历？",
        subtitle="比“我学过 LeRobot”具体很多",
        bullets=["有 GitHub 仓库", "有可运行 notebook", "有输出图", "能解释自己分析了什么"],
        narration="那这个东西为什么能写进简历？因为它不是单纯看教程截图。你有 GitHub 仓库，有可运行 notebook，有输出图，也能解释自己到底分析了什么。这就已经比我学过 LeRobot 具体很多。",
        layout="portfolio",
    ),
    Scene(
        title="简历别写得太夸张",
        subtitle="具体、可解释，就够了",
        bullets=["实现 episode 读取", "实现 action 可视化分析", "理解 observation/action 和轨迹统计"],
        narration="简历上可以不用写得很夸张。你就写：基于 LeRobot 公开机器人数据集，实现 episode 读取和 action 可视化分析。然后补一句：理解 observation、action、轨迹统计和基础数据质量分析。这样就够了。",
        layout="resume",
    ),
    Scene(
        title="这只是第一步",
        subtitle="先跑通，再往后扩展",
        bullets=["项目 01：数据集分析与可视化", "项目 02：Behavior Cloning / ACT", "项目 03：VLA 推理与评测"],
        narration="当然，这只是第一步。它不负责让你一下子变成机器人算法工程师。但它能让你先跑通一个东西。跑通以后，再往 Behavior Cloning、ACT、VLA 这些方向扩展，就没那么飘了。",
        layout="roadmap",
    ),
    Scene(
        title="代码已经放 GitHub",
        subtitle="zero-hardware-embodied-ai",
        bullets=["Colab 能用就直接跑", "不能用 Colab 就跑本地轻量版", "先做出第一个作品集项目"],
        narration="代码我已经放 GitHub 了。能用 Colab 的，直接点开跑。不能用 Colab 的，就跑本地轻量版。如果你想做第一个具身智能作品集项目，可以先从这个开始。",
        layout="end",
    ),
]


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        found = shutil.which("ffmpeg")
        if not found:
            raise RuntimeError("ffmpeg not found. Install requirements-lite.txt first.")
        return found


def font_path(bold: bool = False) -> str:
    candidates = [
        Path(r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return "arial.ttf"


FONT_REGULAR = font_path(False)
FONT_BOLD = font_path(True)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


COLORS = {
    "ink": "#111827",
    "muted": "#475569",
    "subtle": "#6B7280",
    "teal": "#2F6F73",
    "teal_dark": "#17484C",
    "teal_soft": "#E7F1F0",
    "amber": "#D97706",
    "amber_soft": "#FFF4D6",
    "blue_soft": "#EAF2FF",
    "paper": "#FFFFFF",
    "canvas": "#F5F7FA",
    "line": "#D7E1EA",
    "footer": "#101827",
}


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9_./:%#+-]+|\s+|.", text)
    lines: list[str] = []
    line = ""
    for token in tokens:
        if token.isspace():
            token = " " if line and not line.endswith(" ") else ""
        candidate = line + token
        if candidate and text_width(draw, candidate.rstrip(), font) <= max_width:
            line = candidate
            continue
        if line:
            lines.append(line.rstrip())
            line = token.lstrip()
        if line and text_width(draw, line, font) > max_width:
            long_token = line
            line = ""
            for char in long_token:
                candidate = line + char
                if line and text_width(draw, candidate, font) > max_width:
                    lines.append(line)
                    line = char
                else:
                    line = candidate
    if line.strip():
        lines.append(line.rstrip())
    return lines or [""]


def line_height(font: ImageFont.FreeTypeFont, line_gap: int) -> int:
    return int(font.size * 1.18) + line_gap


def ellipsize(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    marker = "..."
    while text and text_width(draw, text + marker, font) > max_width:
        text = text[:-1]
    return text.rstrip() + marker if text else marker


def draw_fit_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    max_width: int,
    max_height: int,
    max_size: int,
    min_size: int,
    fill: str,
    bold: bool = False,
    line_gap: int = 8,
    max_lines: int | None = None,
) -> int:
    x, y = xy
    selected_font = load_font(min_size, bold)
    selected_lines = wrap_text(draw, text, selected_font, max_width)
    selected_height = line_height(selected_font, line_gap)
    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, bold)
        lines = wrap_text(draw, text, font, max_width)
        row_h = line_height(font, line_gap)
        total_h = len(lines) * row_h - line_gap
        if (max_lines is None or len(lines) <= max_lines) and total_h <= max_height:
            selected_font = font
            selected_lines = lines
            selected_height = row_h
            break
    allowed_lines = max(1, min(len(selected_lines), max_height // max(1, selected_height)))
    if max_lines is not None:
        allowed_lines = min(allowed_lines, max_lines)
    lines_to_draw = selected_lines[:allowed_lines]
    if len(selected_lines) > allowed_lines:
        lines_to_draw[-1] = ellipsize(draw, lines_to_draw[-1], selected_font, max_width)
    for line in lines_to_draw:
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += selected_height
    return y


def draw_centered_fit(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    max_size: int,
    min_size: int,
    fill: str,
    bold: bool = False,
) -> None:
    x1, y1, x2, y2 = box
    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, bold)
        lines = wrap_text(draw, text, font, x2 - x1 - 22)
        row_h = line_height(font, 2)
        if len(lines) * row_h <= y2 - y1 - 18:
            break
    else:
        font = load_font(min_size, bold)
        lines = wrap_text(draw, text, font, x2 - x1 - 22)[:2]
    total_h = len(lines) * line_height(font, 2) - 2
    y = y1 + (y2 - y1 - total_h) // 2
    for line in lines:
        x = x1 + (x2 - x1 - text_width(draw, line, font)) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height(font, 2)


def rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str,
    outline: str = "#D6DEE8",
    radius: int = 28,
    width: int = 2,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str = "#FFFFFF",
    outline: str = "#D7E1EA",
    radius: int = 28,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1 + 8, y1 + 10, x2 + 8, y2 + 10), radius=radius, fill="#E8EEF5")
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def trim_near_white(img: Image.Image, threshold: int = 246, margin: int = 10) -> Image.Image:
    rgb = img.convert("RGB")
    bg = Image.new("RGB", rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, bg).convert("L")
    mask = diff.point(lambda value: 255 if value > 255 - threshold else 0)
    box = mask.getbbox()
    if not box:
        return rgb
    x1, y1, x2, y2 = box
    x1 = max(0, x1 - margin)
    y1 = max(0, y1 - margin)
    x2 = min(rgb.width, x2 + margin)
    y2 = min(rgb.height, y2 + margin)
    return rgb.crop((x1, y1, x2, y2))


def paste_contain(
    canvas: Image.Image,
    path: Path,
    box: tuple[int, int, int, int],
    padding: int = 0,
    trim_white: bool = False,
) -> None:
    img = Image.open(path).convert("RGB")
    if trim_white:
        img = trim_near_white(img)
    x1, y1, x2, y2 = box
    x1 += padding
    y1 += padding
    x2 -= padding
    y2 -= padding
    scale = min((x2 - x1) / img.width, (y2 - y1) / img.height)
    size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
    img = img.resize(size, Image.Resampling.LANCZOS)
    canvas.paste(img, (x1 + (x2 - x1 - img.width) // 2, y1 + (y2 - y1 - img.height) // 2))


def paste_cover(canvas: Image.Image, path: Path, box: tuple[int, int, int, int]) -> None:
    img = Image.open(path).convert("RGB")
    x1, y1, x2, y2 = box
    img = ImageOps.fit(img, (x2 - x1, y2 - y1), Image.Resampling.LANCZOS)
    canvas.paste(img, (x1, y1))


def draw_header(draw: ImageDraw.ImageDraw, scene_no: int) -> None:
    draw.rectangle((0, 0, WIDTH, 18), fill=COLORS["teal"])
    draw.rectangle((0, HEIGHT - 78, WIDTH, HEIGHT), fill=COLORS["footer"])
    draw.text((72, HEIGHT - 51), "Zero-Hardware Embodied AI Project 01", font=load_font(25), fill="#E5E7EB")
    dots_x = WIDTH - 520
    for i in range(len(SCENES)):
        x = dots_x + i * 28
        fill = "#F59E0B" if i + 1 == scene_no else "#334155"
        draw.rounded_rectangle((x, HEIGHT - 44, x + 18, HEIGHT - 26), radius=9, fill=fill)
    draw.text((WIDTH - 152, HEIGHT - 51), f"{scene_no:02d}/{len(SCENES):02d}", font=load_font(25, True), fill="#CBD5E1")


def draw_background(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=COLORS["canvas"])
    draw.polygon([(0, 18), (620, 18), (520, HEIGHT - 78), (0, HEIGHT - 78)], fill="#F9FBFC")
    draw.rectangle((0, 18, WIDTH, 20), fill="#DBE8E8")
    draw.line((970, 116, 970, HEIGHT - 168), fill="#E4EBF2", width=2)


def draw_badge(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: str = "#E7F1F0") -> None:
    x, y = xy
    font = load_font(22, True)
    w = text_width(draw, text, font) + 34
    draw.rounded_rectangle((x, y, x + w, y + 38), radius=19, fill=fill, outline="#C5DDDA", width=1)
    draw.text((x + 17, y + 7), text, font=font, fill=COLORS["teal_dark"])


def draw_bullet_panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    bullets: list[str],
    heading: str = "本页要点",
) -> None:
    x1, y1, x2, y2 = box
    card(draw, box, "#FFFFFF")
    draw_badge(draw, (x1 + 34, y1 + 28), heading, "#FFF4D6")
    available_h = y2 - y1 - 112
    row_h = max(74, available_h // max(1, len(bullets)))
    for i, bullet in enumerate(bullets, start=1):
        row_y = y1 + 96 + (i - 1) * row_h
        draw.rounded_rectangle((x1 + 34, row_y + 6, x1 + 82, row_y + 54), radius=16, fill=COLORS["teal_soft"])
        draw.text((x1 + 51, row_y + 17), str(i), font=load_font(24, True), fill=COLORS["teal_dark"])
        draw_fit_text(
            draw,
            (x1 + 108, row_y + 4),
            bullet,
            x2 - x1 - 150,
            row_h - 8,
            34,
            25,
            "#293548",
            line_gap=4,
            max_lines=2,
        )


def draw_title_block(canvas: Image.Image, draw: ImageDraw.ImageDraw, scene: Scene, index: int) -> None:
    draw_badge(draw, (78, 78), f"PROJECT 01 · STEP {index:02d}")
    title_bottom = draw_fit_text(
        draw,
        (78, 140),
        scene.title,
        830,
        140,
        60,
        42,
        COLORS["ink"],
        bold=True,
        line_gap=4,
        max_lines=2,
    )
    subtitle_y = max(260, title_bottom + 16)
    subtitle_bottom = draw_fit_text(
        draw,
        (82, subtitle_y),
        scene.subtitle,
        820,
        92,
        34,
        25,
        COLORS["teal"],
        line_gap=4,
        max_lines=2,
    )
    bullet_top = max(392, subtitle_bottom + 26)
    draw_bullet_panel(canvas, draw, (74, bullet_top, 912, 842), scene.bullets)


def draw_note_strip(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fill: str = "#E7F1F0",
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=22, fill=fill, outline="#C5DDDA", width=1)
    draw_fit_text(draw, (x1 + 24, y1 + 17), text, x2 - x1 - 48, y2 - y1 - 24, 25, 18, COLORS["teal_dark"], bold=True, max_lines=2)


def draw_browser_mock(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    lines: list[str],
    note: str | None = None,
) -> None:
    x1, y1, x2, y2 = box
    card(draw, box, "#FFFFFF")
    draw.rounded_rectangle((x1, y1, x2, y1 + 68), radius=28, fill="#EEF3F8", outline="#D6DEE8", width=2)
    draw.ellipse((x1 + 28, y1 + 24, x1 + 44, y1 + 40), fill="#EF4444")
    draw.ellipse((x1 + 56, y1 + 24, x1 + 72, y1 + 40), fill="#F59E0B")
    draw.ellipse((x1 + 84, y1 + 24, x1 + 100, y1 + 40), fill="#22C55E")
    draw_fit_text(draw, (x1 + 130, y1 + 18), title, x2 - x1 - 160, 34, 24, 18, "#475569", max_lines=1)
    y = y1 + 104
    note_reserved = 104 if note else 0
    for i, line in enumerate(lines, start=1):
        if y + 66 > y2 - 32 - note_reserved:
            break
        row_fill = "#F8FAFC" if i % 2 else "#F1F5F9"
        draw.rounded_rectangle((x1 + 36, y, x2 - 36, y + 58), radius=16, fill=row_fill)
        draw.text((x1 + 58, y + 16), f"{i:02d}", font=load_font(20, True), fill="#94A3B8")
        draw_fit_text(draw, (x1 + 112, y + 12), line, x2 - x1 - 176, 34, 28, 20, "#172033", max_lines=1)
        y += 72
    if note:
        draw_note_strip(draw, (x1 + 36, y2 - 104, x2 - 36, y2 - 34), note)


def draw_terminal(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], lines: list[str]) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1 + 8, y1 + 10, x2 + 8, y2 + 10), radius=24, fill="#C7D2DE")
    draw.rounded_rectangle(box, radius=24, fill="#111827")
    draw.text((x1 + 28, y1 + 22), "PowerShell", font=load_font(22), fill="#94A3B8")
    y = y1 + 72
    for line in lines:
        draw_fit_text(draw, (x1 + 32, y), line, x2 - x1 - 64, 44, 25, 18, "#E5E7EB", max_lines=1)
        y += 48


def draw_flow(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], labels: list[str]) -> None:
    x1, y1, x2, y2 = box
    card(draw, box, "#FFFFFF")
    draw_badge(draw, (x1 + 38, y1 + 34), "学习路径")
    step_w = max(164, (x2 - x1 - 160) // len(labels))
    gap = 28
    start_x = x1 + 56
    y = y1 + (y2 - y1 - 124) // 2 + 42
    for i, label in enumerate(labels):
        sx = start_x + i * (step_w + gap)
        draw.rounded_rectangle((sx, y, sx + step_w, y + 120), radius=24, fill="#EAF2F1", outline="#A8C9C7", width=2)
        draw_centered_fit(draw, (sx + 12, y + 18, sx + step_w - 12, y + 102), label, 29, 18, "#2F6F73", True)
        if i < len(labels) - 1:
            ax = sx + step_w + 12
            draw.line((ax, y + 60, ax + gap - 24, y + 60), fill="#64748B", width=4)
            draw.polygon([(ax + gap - 24, y + 50), (ax + gap - 24, y + 70), (ax + gap - 8, y + 60)], fill="#64748B")


def draw_image_card(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    path: Path,
    label: str,
    trim_white: bool = True,
    caption: str | None = None,
) -> None:
    x1, y1, x2, y2 = box
    card(draw, box, "#FFFFFF")
    draw_fit_text(draw, (x1 + 28, y1 + 20), label, x2 - x1 - 56, 36, 26, 18, COLORS["muted"], bold=True, max_lines=1)
    content_bottom = y2 - 116 if caption else y2 - 24
    paste_contain(canvas, path, (x1 + 24, y1 + 70, x2 - 24, content_bottom), 4, trim_white=trim_white)
    if caption:
        draw_note_strip(draw, (x1 + 28, y2 - 98, x2 - 28, y2 - 28), caption, "#FFF4D6")


def render_scene(scene: Scene, index: int, output: Path) -> None:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), COLORS["canvas"])
    draw = ImageDraw.Draw(canvas)
    draw_background(draw)

    if scene.layout in {"hook", "end"}:
        paste_cover(canvas, CONTENT_DIR / "avatar_tech_narrator.png", (0, 18, WIDTH, HEIGHT - 78))
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (248, 250, 252, 0))
        od = ImageDraw.Draw(overlay)
        od.rectangle((0, 18, 1020, HEIGHT - 78), fill=(248, 250, 252, 240))
        od.rectangle((0, 18, 1020, HEIGHT - 78), outline=(214, 225, 234, 255), width=2)
        canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(canvas)
        draw_badge(draw, (84, 92), "零硬件具身智能项目包")
        draw_fit_text(
            draw,
            (84, 168),
            scene.title,
            820,
            170,
            66,
            44,
            COLORS["ink"],
            bold=True,
            max_lines=2,
        )
        draw_fit_text(
            draw,
            (88, 372),
            scene.subtitle,
            800,
            88,
            34,
            24,
            COLORS["teal"],
            max_lines=2,
        )
        draw_bullet_panel(canvas, draw, (84, 520, 898, 818), scene.bullets, "你会得到")
        if scene.layout == "end":
            draw_terminal(
                draw,
                (1068, 666, 1804, 824),
                ["github.com/Qinghev/zero-hardware-embodied-ai"],
            )
    else:
        draw_title_block(canvas, draw, scene, index)
        panel = (1014, 128, 1834, 842)
        if scene.layout == "collage":
            card(draw, panel, "#F8FAFC")
            draw_image_card(canvas, draw, (1050, 184, 1384, 486), ROOT / "assets" / "demo_first_frame.png", "episode first frame", False)
            draw_image_card(canvas, draw, (1410, 184, 1798, 486), ROOT / "assets" / "demo_action_timeseries.png", "action time series", True)
            draw_image_card(canvas, draw, (1050, 528, 1798, 812), ROOT / "assets" / "demo_action_distribution.png", "action distribution", True)
        elif scene.layout == "concept":
            draw_flow(draw, panel, ["episode", "observation", "action"])
        elif scene.layout == "github":
            draw_browser_mock(
                draw,
                panel,
                "github.com/Qinghev/zero-hardware-embodied-ai",
                [
                    "# Zero-Hardware Embodied AI",
                    "Open in Colab",
                    "Local lite: requirements-lite.txt",
                    "scripts/visualize_pusht_lite.py",
                    "assets/demo_action_timeseries.png",
                ],
                note="双入口的目的：Colab 适合快速试，本地轻量版负责兜底。",
            )
        elif scene.layout == "colab":
            draw_browser_mock(
                draw,
                panel,
                "colab.research.google.com",
                [
                    "Runtime: None",
                    "%pip install -q -r requirements-lite.txt",
                    "!python scripts/visualize_pusht_lite.py",
                    "Generated: first frame / action plots",
                ],
                note="这个项目只读数据和画图，所以不用 GPU，也不需要先训练模型。",
            )
        elif scene.layout == "first_frame":
            draw_image_card(
                canvas,
                draw,
                panel,
                ROOT / "assets" / "demo_first_frame.png",
                "PushT episode first frame",
                False,
                "先看首帧，确认任务场景和轨迹对象，再继续分析 action。",
            )
        elif scene.layout == "timeseries":
            draw_image_card(
                canvas,
                draw,
                panel,
                ROOT / "assets" / "demo_action_timeseries.png",
                "action[0] / action[1] over time",
                True,
                "这张图回答一个问题：动作值是平滑变化，还是有明显跳变？",
            )
        elif scene.layout == "distribution":
            draw_image_card(
                canvas,
                draw,
                panel,
                ROOT / "assets" / "demo_action_distribution.png",
                "action distribution",
                True,
                "分布图适合做数据质量检查：范围、集中区间、异常值。",
            )
        elif scene.layout == "portfolio":
            draw_flow(draw, panel, ["GitHub", "notebook", "plots", "summary"])
        elif scene.layout == "resume":
            draw_browser_mock(
                draw,
                panel,
                "Resume project snippet",
                [
                    "LeRobot dataset analysis",
                    "Episode loading + action visualization",
                    "Observation/action structure",
                    "Trajectory statistics",
                ],
                note="简历表达不要写大词，写清楚你读了什么数据、产出了什么图。",
            )
        elif scene.layout == "roadmap":
            draw_flow(draw, panel, ["Project 01", "BC / ACT", "VLA eval"])
        else:
            card(draw, panel, "#FFFFFF")

    draw_header(draw, index)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def run(command: list[str], timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=True, timeout=timeout)


def media_duration(path: Path) -> float:
    proc = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", str(path)], text=True, capture_output=True)
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", proc.stderr)
    if not match:
        raise RuntimeError(f"Could not read duration from {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def clean_voice(input_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    filters = (
        "silenceremove=start_periods=1:start_duration=0.2:start_threshold=-45dB,"
        "pan=mono|c0=0.5*c0+0.5*c1,"
        "highpass=f=75,lowpass=f=13500,"
        "afftdn=nf=-28,"
        "dynaudnorm=f=150:g=7:m=8,"
        "loudnorm=I=-16:TP=-1.5:LRA=11"
    )
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-hide_banner",
        "-i",
        str(input_path),
        "-af",
        filters,
        "-ar",
        "48000",
        "-ac",
        "1",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)


def allocate_durations(total_duration: float) -> list[float]:
    weights = [max(1, len(scene.narration)) for scene in SCENES]
    total_weight = sum(weights)
    raw = [total_duration * weight / total_weight for weight in weights]
    min_duration = 8.0
    durations = [max(min_duration, item) for item in raw]
    scale = total_duration / sum(durations)
    return [item * scale for item in durations]


def srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - math.floor(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(durations: list[float], output_path: Path) -> None:
    lines: list[str] = []
    cursor = 0.0
    for index, (scene, duration) in enumerate(zip(SCENES, durations), start=1):
        lines.append(str(index))
        lines.append(f"{srt_time(cursor)} --> {srt_time(cursor + duration)}")
        lines.append(scene.narration)
        lines.append("")
        cursor += duration
    output_path.write_text("\n".join(lines), encoding="utf-8")


def render_video(durations: list[float], frame_paths: list[Path], output_path: Path) -> Path:
    concat_path = CONTENT_DIR / "final_concat.txt"
    lines: list[str] = []
    for frame_path, duration in zip(frame_paths, durations):
        lines.append(f"file '{frame_path.as_posix()}'")
        lines.append(f"duration {duration:.3f}")
    lines.append(f"file '{frame_paths[-1].as_posix()}'")
    concat_path.write_text("\n".join(lines), encoding="utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-hide_banner",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_path),
        "-vf",
        f"fps={FPS},format=yuv420p",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "22",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)
    return output_path


def render_motion_video(durations: list[float], frame_paths: list[Path], output_path: Path) -> Path:
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    clip_paths: list[Path] = []
    for index, (frame_path, duration) in enumerate(zip(frame_paths, durations), start=1):
        clip_path = CLIPS_DIR / f"scene_{index:02d}.mp4"
        # A very light push-in keeps the no-face edit from feeling like static slides.
        filter_graph = (
            "scale=2000:1125,"
            "zoompan=z='min(zoom+0.00028,1.035)':"
            "d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"fps={FPS}:s={WIDTH}x{HEIGHT},"
            "format=yuv420p"
        )
        cmd = [
            ffmpeg_exe(),
            "-y",
            "-hide_banner",
            "-loop",
            "1",
            "-i",
            str(frame_path),
            "-t",
            f"{duration:.3f}",
            "-vf",
            filter_graph,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "21",
            str(clip_path),
        ]
        subprocess.run(cmd, check=True)
        clip_paths.append(clip_path)

    concat_path = CONTENT_DIR / "final_motion_concat.txt"
    concat_path.write_text(
        "\n".join(f"file '{clip_path.as_posix()}'" for clip_path in clip_paths),
        encoding="utf-8",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-hide_banner",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_path),
        "-c",
        "copy",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)
    return output_path


def mux_audio(video_path: Path, audio_path: Path, output_path: Path, duration: float) -> Path:
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-hide_banner",
        "-i",
        str(video_path),
        "-i",
        str(audio_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-t",
        f"{duration:.3f}",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)
    return output_path


def default_voice_path() -> Path:
    candidates = sorted((ROOT / "assets").glob("录音机-*.wav"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        return candidates[0]
    raise FileNotFoundError("No voice recording found under assets/录音机-*.wav")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create final video 01 with user's real voice.")
    parser.add_argument("--voice", default=None, help="Path to the raw voice recording.")
    args = parser.parse_args()

    raw_voice = Path(args.voice) if args.voice else default_voice_path()
    if not raw_voice.is_absolute():
        raw_voice = ROOT / raw_voice

    clean_voice_path = EXPORTS_DIR / "video_01_voice_clean_trimmed.wav"
    clean_voice(raw_voice, clean_voice_path)
    duration = media_duration(clean_voice_path)
    durations = allocate_durations(duration)

    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    frame_paths: list[Path] = []
    for index, scene in enumerate(SCENES, start=1):
        frame = FRAMES_DIR / f"scene_{index:02d}.png"
        render_scene(scene, index, frame)
        frame_paths.append(frame)

    cover = CONTENT_DIR / "cover_v2.png"
    Image.open(frame_paths[0]).save(cover)
    write_srt(durations, CONTENT_DIR / "bilibili_video_01_final_subtitles.srt")

    silent_video = EXPORTS_DIR / "bilibili_video_01_final_silent_v2.mp4"
    final_video = EXPORTS_DIR / "bilibili_video_01_final_your_voice.mp4"
    render_motion_video(durations, frame_paths, silent_video)
    mux_audio(silent_video, clean_voice_path, final_video, duration)

    mp3_path = EXPORTS_DIR / "video_01_voice_clean_trimmed.mp3"
    subprocess.run(
        [
            ffmpeg_exe(),
            "-y",
            "-hide_banner",
            "-i",
            str(clean_voice_path),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "160k",
            str(mp3_path),
        ],
        check=True,
    )

    metadata = {
        "raw_voice_name": raw_voice.name,
        "clean_voice": str(clean_voice_path),
        "duration_seconds": round(duration, 3),
        "final_video": str(final_video),
        "cover": str(cover),
        "subtitles": str(CONTENT_DIR / "bilibili_video_01_final_subtitles.srt"),
    }
    (CONTENT_DIR / "final_build_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
