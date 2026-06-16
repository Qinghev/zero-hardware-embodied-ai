from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


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


def draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    max_width: int,
    line_gap: int = 12,
) -> int:
    x, y = xy
    line = ""
    lines: list[str] = []
    for char in text:
        candidate = line + char
        if line and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
            lines.append(line)
            line = char
        else:
            line = candidate
    if line:
        lines.append(line)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_gap
    return y


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, outline: str = "#D6DEE8") -> None:
    draw.rounded_rectangle(box, radius=28, fill=fill, outline=outline, width=2)


def paste_contain(canvas: Image.Image, path: Path, box: tuple[int, int, int, int], padding: int = 0) -> None:
    img = Image.open(path).convert("RGB")
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
    draw.rectangle((0, 0, WIDTH, 22), fill="#2F6F73")
    draw.rectangle((0, HEIGHT - 88, WIDTH, HEIGHT), fill="#101827")
    draw.text((72, HEIGHT - 58), "Zero-Hardware Embodied AI Project 01", font=load_font(28), fill="#E5E7EB")
    draw.text((WIDTH - 230, HEIGHT - 58), f"{scene_no:02d}/{len(SCENES):02d}", font=load_font(28), fill="#CBD5E1")


def draw_bullets(draw: ImageDraw.ImageDraw, bullets: list[str], x: int, y: int, width: int) -> None:
    bullet_font = load_font(36)
    for bullet in bullets:
        draw.ellipse((x, y + 12, x + 20, y + 32), fill="#D97706")
        y = draw_text(draw, (x + 42, y), bullet, bullet_font, "#293548", width - 42, 12) + 14


def draw_title_block(draw: ImageDraw.ImageDraw, scene: Scene) -> None:
    draw_text(draw, (82, 80), scene.title, load_font(64, True), "#101827", 930, 16)
    draw_text(draw, (86, 238), scene.subtitle, load_font(35), "#2F6F73", 920, 10)
    draw_bullets(draw, scene.bullets, 92, 342, 840)


def draw_browser_mock(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, lines: list[str]) -> None:
    x1, y1, x2, y2 = box
    rounded(draw, box, "#FFFFFF")
    draw.rounded_rectangle((x1, y1, x2, y1 + 66), radius=28, fill="#EEF3F8", outline="#D6DEE8", width=2)
    draw.ellipse((x1 + 28, y1 + 24, x1 + 44, y1 + 40), fill="#EF4444")
    draw.ellipse((x1 + 56, y1 + 24, x1 + 72, y1 + 40), fill="#F59E0B")
    draw.ellipse((x1 + 84, y1 + 24, x1 + 100, y1 + 40), fill="#22C55E")
    draw.text((x1 + 130, y1 + 20), title, font=load_font(24), fill="#475569")
    y = y1 + 110
    for line in lines:
        draw.text((x1 + 48, y), line, font=load_font(30), fill="#172033")
        y += 52


def draw_terminal(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], lines: list[str]) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=24, fill="#111827")
    draw.text((x1 + 28, y1 + 24), "PowerShell", font=load_font(24), fill="#94A3B8")
    y = y1 + 80
    mono = load_font(28)
    for line in lines:
        draw.text((x1 + 32, y), line, font=mono, fill="#E5E7EB")
        y += 48


def draw_flow(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], labels: list[str]) -> None:
    x1, y1, x2, y2 = box
    rounded(draw, box, "#FFFFFF")
    step_w = 190
    gap = 50
    start_x = x1 + 70
    y = y1 + 220
    for i, label in enumerate(labels):
        sx = start_x + i * (step_w + gap)
        draw.rounded_rectangle((sx, y, sx + step_w, y + 120), radius=22, fill="#EAF2F1", outline="#A8C9C7", width=2)
        draw.text((sx + 22, y + 38), label, font=load_font(30, True), fill="#2F6F73")
        if i < len(labels) - 1:
            ax = sx + step_w + 12
            draw.line((ax, y + 60, ax + gap - 24, y + 60), fill="#64748B", width=4)
            draw.polygon([(ax + gap - 24, y + 50), (ax + gap - 24, y + 70), (ax + gap - 8, y + 60)], fill="#64748B")


def render_scene(scene: Scene, index: int, output: Path) -> None:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "#F8FAFC")
    draw = ImageDraw.Draw(canvas)
    draw_header(draw, index)

    if scene.layout in {"hook", "end"}:
        paste_cover(canvas, CONTENT_DIR / "avatar_tech_narrator.png", (0, 22, WIDTH, HEIGHT - 88))
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (248, 250, 252, 0))
        od = ImageDraw.Draw(overlay)
        od.rectangle((0, 22, 980, HEIGHT - 88), fill=(248, 250, 252, 236))
        canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(canvas)
        draw_header(draw, index)
        draw_title_block(draw, scene)
        if scene.layout == "end":
            draw_terminal(
                draw,
                (1080, 650, 1800, 810),
                ["github.com/Qinghev/zero-hardware-embodied-ai"],
            )
    else:
        draw_title_block(draw, scene)
        card = (1030, 160, 1810, 835)
        if scene.layout == "collage":
            rounded(draw, card, "#FFFFFF")
            paste_contain(canvas, ROOT / "assets" / "demo_first_frame.png", (1080, 205, 1330, 455), 8)
            paste_contain(canvas, ROOT / "assets" / "demo_action_timeseries.png", (1340, 205, 1770, 455), 8)
            paste_contain(canvas, ROOT / "assets" / "demo_action_distribution.png", (1080, 505, 1770, 785), 8)
        elif scene.layout == "concept":
            draw_flow(draw, card, ["episode", "observation", "action"])
        elif scene.layout == "github":
            draw_browser_mock(
                draw,
                card,
                "github.com/Qinghev/zero-hardware-embodied-ai",
                [
                    "# Zero-Hardware Embodied AI Project 01",
                    "[Open in Colab]",
                    "Local lite: requirements-lite.txt",
                    "assets/demo_action_timeseries.png",
                ],
            )
        elif scene.layout == "colab":
            draw_browser_mock(
                draw,
                card,
                "colab.research.google.com",
                [
                    "Runtime: None",
                    "%pip install -q -r requirements-lite.txt",
                    "!python scripts/visualize_pusht_lite.py",
                    "Generated: first frame / action plots",
                ],
            )
        elif scene.layout == "first_frame":
            rounded(draw, card, "#FFFFFF")
            paste_contain(canvas, ROOT / "assets" / "demo_first_frame.png", card, 70)
        elif scene.layout == "timeseries":
            rounded(draw, card, "#FFFFFF")
            paste_contain(canvas, ROOT / "assets" / "demo_action_timeseries.png", card, 50)
        elif scene.layout == "distribution":
            rounded(draw, card, "#FFFFFF")
            paste_contain(canvas, ROOT / "assets" / "demo_action_distribution.png", card, 50)
        elif scene.layout == "portfolio":
            draw_flow(draw, card, ["GitHub", "notebook", "plots", "summary"])
        elif scene.layout == "resume":
            draw_browser_mock(
                draw,
                card,
                "Resume project snippet",
                [
                    "LeRobot dataset analysis",
                    "Episode loading + action visualization",
                    "Observation/action structure",
                    "Trajectory statistics",
                ],
            )
        elif scene.layout == "roadmap":
            draw_flow(draw, card, ["Project 01", "BC / ACT", "VLA eval"])
        else:
            rounded(draw, card, "#FFFFFF")

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
