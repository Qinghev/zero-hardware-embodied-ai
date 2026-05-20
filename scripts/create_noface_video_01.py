from __future__ import annotations

import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "video_01"
FRAMES_DIR = CONTENT_DIR / "frames"
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
    duration: int
    image: str | None = None
    code: str | None = None


SCENES = [
    Scene(
        title="不用买机械臂，也能做具身智能项目",
        subtitle="Zero-Hardware Embodied AI Project 01",
        bullets=["不用真实机器人", "不用 GPU", "用公开机器人数据生成可展示结果"],
        narration="很多人想入门具身智能，第一反应是买机械臂。但第一个项目，其实可以先从机器人数据开始。",
        duration=12,
    ),
    Scene(
        title="第一个项目先学会读懂机器人数据",
        subtitle="episode / observation / action",
        bullets=[
            "episode：一次完整任务轨迹",
            "observation：机器人看到或感知到的状态",
            "action：轨迹中记录的动作",
        ],
        narration="这个项目不训练大模型，也不控制真实机器人。它只做一件关键的事：读懂机器人数据。",
        duration=13,
    ),
    Scene(
        title="免费版已经支持三种入口",
        subtitle="GitHub + Colab + 本地轻量版",
        bullets=[
            "Colab：点开就能跑",
            "本地轻量版：适合 Colab 不稳定的用户",
            "完整 LeRobot 版：作为进阶路径",
        ],
        narration="为了降低环境门槛，免费版做了三个入口。能用 Colab 就直接跑，Colab 不稳定就用本地轻量版。",
        duration=13,
    ),
    Scene(
        title="Colab 不需要 GPU",
        subtitle="Hardware accelerator: None",
        bullets=[
            "clone GitHub 仓库",
            "安装轻量依赖",
            "下载 PushT 小数据文件",
            "生成三张可视化图",
        ],
        narration="项目零一不需要 GPU。在 Colab 里选择 None 就可以。它会下载一个很小的 PushT 数据集样例，然后生成可视化结果。",
        duration=15,
        code=(
            "%pip install -q -r requirements-lite.txt\n"
            "!python scripts/visualize_pusht_lite.py --episode-index 0"
        ),
    ),
    Scene(
        title="如果不能用 Colab，也可以本地跑",
        subtitle="Windows 普通笔记本可运行",
        bullets=[
            "创建 venv",
            "安装 requirements-lite.txt",
            "运行 visualize_pusht_lite.py",
        ],
        narration="如果你所在网络不能稳定访问 Colab，也可以在本地跑轻量版。这个版本不安装 LeRobot，只处理小型 parquet 和 mp4 文件。",
        duration=16,
        code=(
            "python -m venv .venv\n"
            ".\\.venv\\Scripts\\activate\n"
            "pip install -r requirements-lite.txt\n"
            "python scripts/visualize_pusht_lite.py --episode-index 0"
        ),
    ),
    Scene(
        title="输出 1：episode 首帧",
        subtitle="先确认这条轨迹在做什么",
        bullets=["PushT 是一个二维推块任务", "首帧能帮助理解任务场景", "不需要真实相机或机械臂"],
        narration="第一张图是 episode 的首帧。它能让你快速确认这条机器人轨迹对应的任务场景。",
        duration=13,
        image="assets/demo_first_frame.png",
    ),
    Scene(
        title="输出 2：action 随时间变化",
        subtitle="看懂动作轨迹",
        bullets=["横轴是时间", "纵轴是 action 数值", "两条曲线对应两个动作维度"],
        narration="第二张图是 action 随时间变化。你可以看到两个动作维度在整条轨迹里的变化趋势。",
        duration=16,
        image="assets/demo_action_timeseries.png",
    ),
    Scene(
        title="输出 3：action 分布",
        subtitle="检查范围、集中区间和异常值",
        bullets=["动作是否集中在少数区间", "是否存在异常尖峰", "后续可扩展到数据质量检查"],
        narration="第三张图是 action 分布。它可以帮助我们检查动作范围、集中区间和潜在异常值。",
        duration=15,
        image="assets/demo_action_distribution.png",
    ),
    Scene(
        title="为什么这能成为简历项目？",
        subtitle="不是教程截图，而是可复现项目资产",
        bullets=[
            "有 GitHub 仓库",
            "有可运行 notebook",
            "有数据分析图",
            "有可解释的项目总结",
        ],
        narration="它不是简单看教程，而是一个可复现的项目资产。有仓库、有 notebook、有图表，也有可以解释的数据分析结果。",
        duration=15,
    ),
    Scene(
        title="中文简历描述",
        subtitle="可以先这样写",
        bullets=[
            "基于 LeRobot 公开机器人数据集实现 episode 数据读取与 action 可视化分析",
            "完成 observation/action 数据结构理解、轨迹统计和基础可视化结果输出",
        ],
        narration="简历上可以这样写：基于 LeRobot 公开机器人数据集实现 episode 数据读取与 action 可视化分析，完成机器人数据结构理解和轨迹统计。",
        duration=16,
    ),
    Scene(
        title="这个免费版只解决第一步",
        subtitle="先跑通，再扩展",
        bullets=[
            "项目 01：数据集分析与可视化",
            "项目 02：Behavior Cloning baseline",
            "项目 03：VLA 推理与评测",
        ],
        narration="免费版先解决第一步：跑通数据分析与可视化。后续可以继续扩展到模仿学习 baseline 和 VLA 推理评测。",
        duration=14,
    ),
    Scene(
        title="免费代码已经放在 GitHub",
        subtitle="zero-hardware-embodied-ai",
        bullets=[
            "支持 Colab quick start",
            "支持本地轻量版",
            "适合做第一个具身智能作品集项目",
        ],
        narration="免费代码已经放在 GitHub。适合想入门具身智能、机器人学习，或者准备作品集项目的同学。",
        duration=13,
        code="https://github.com/Qinghev/zero-hardware-embodied-ai",
    ),
]


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


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    return int(draw.textbbox((0, 0), text, font=font)[2])


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        if char == "\n":
            lines.append(current)
            current = ""
            continue
        candidate = current + char
        if current and text_width(draw, candidate, font) > max_width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    max_width: int,
    line_spacing: int = 12,
) -> int:
    x, y = xy
    for line in wrap_text(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_spacing
    return y


def draw_code(draw: ImageDraw.ImageDraw, code: str, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=22, fill="#111827")
    font = load_font(34, False)
    y = y1 + 34
    for line in code.splitlines():
        draw.text((x1 + 34, y), line, font=font, fill="#E5E7EB")
        y += 52


def paste_image(canvas: Image.Image, image_path: str, box: tuple[int, int, int, int]) -> None:
    path = ROOT / image_path
    if path.suffix.lower() == ".svg":
        return
    img = Image.open(path).convert("RGB")
    x1, y1, x2, y2 = box
    max_w = x2 - x1
    max_h = y2 - y1
    scale = min(max_w / img.width, max_h / img.height)
    new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    px = x1 + (max_w - img.width) // 2
    py = y1 + (max_h - img.height) // 2
    canvas.paste(img, (px, py))


def render_scene(scene: Scene, index: int) -> Path:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "#F8FAFC")
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0, 0, WIDTH, 22), fill="#2F6F73")
    draw.rectangle((0, HEIGHT - 96, WIDTH, HEIGHT), fill="#111827")
    draw.text((80, HEIGHT - 62), "Zero-Hardware Embodied AI Project 01", font=load_font(28), fill="#E5E7EB")
    draw.text((WIDTH - 260, HEIGHT - 62), f"{index:02d}/{len(SCENES):02d}", font=load_font(28), fill="#CBD5E1")

    title_font = load_font(66, True)
    subtitle_font = load_font(36)
    bullet_font = load_font(38)

    draw_wrapped(draw, (88, 82), scene.title, title_font, "#0F172A", 900, 16)
    draw_wrapped(draw, (92, 245), scene.subtitle, subtitle_font, "#2F6F73", 920, 10)

    y = 340
    for bullet in scene.bullets:
        draw.ellipse((94, y + 14, 114, y + 34), fill="#D97706")
        y = draw_wrapped(draw, (134, y), bullet, bullet_font, "#263241", 820, 16) + 14

    right_box = (1030, 170, 1810, 850)
    draw.rounded_rectangle(right_box, radius=26, fill="#FFFFFF", outline="#D9E0EA", width=2)

    if scene.image:
        paste_image(canvas, scene.image, (1080, 220, 1760, 800))
    elif scene.code:
        draw_code(draw, scene.code, (1075, 275, 1765, 735))
    else:
        draw.rounded_rectangle((1110, 265, 1730, 725), radius=24, fill="#EAF2F1")
        draw.text((1165, 350), "Zero Hardware", font=load_font(56, True), fill="#2F6F73")
        draw.text((1165, 430), "Robot Learning", font=load_font(48, True), fill="#0F172A")
        draw.text((1165, 520), "Data -> Plots -> Portfolio", font=load_font(36), fill="#475569")

    out = FRAMES_DIR / f"scene_{index:02d}.png"
    canvas.save(out)
    return out


def srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - math.floor(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_text_assets() -> None:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    voiceover = CONTENT_DIR / "bilibili_video_01_voiceover.md"
    shotlist = CONTENT_DIR / "bilibili_video_01_shotlist.md"
    subtitles = CONTENT_DIR / "bilibili_video_01_subtitles.srt"

    voiceover_lines = ["# B 站视频 01 口播稿\n"]
    shotlist_lines = ["# B 站视频 01 不出镜分镜\n"]
    srt_lines: list[str] = []
    cursor = 0.0

    for idx, scene in enumerate(SCENES, start=1):
        voiceover_lines.append(f"## Scene {idx:02d} - {scene.title}\n\n{scene.narration}\n")
        shotlist_lines.append(
            f"## Scene {idx:02d} ({scene.duration}s)\n\n"
            f"- 画面标题：{scene.title}\n"
            f"- 画面副标题：{scene.subtitle}\n"
            f"- 画面元素：{', '.join(scene.bullets)}\n"
            f"- 口播：{scene.narration}\n"
        )
        srt_lines.extend(
            [
                str(idx),
                f"{srt_time(cursor)} --> {srt_time(cursor + scene.duration)}",
                scene.narration,
                "",
            ]
        )
        cursor += scene.duration

    voiceover.write_text("\n".join(voiceover_lines), encoding="utf-8")
    shotlist.write_text("\n".join(shotlist_lines), encoding="utf-8")
    subtitles.write_text("\n".join(srt_lines), encoding="utf-8")


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        found = shutil.which("ffmpeg")
        if not found:
            raise RuntimeError("ffmpeg not found. Install requirements-lite.txt or put ffmpeg on PATH.")
        return found


def render_video(frame_paths: list[Path]) -> Path:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    concat_file = CONTENT_DIR / "concat.txt"
    lines: list[str] = []
    for frame, scene in zip(frame_paths, SCENES):
        lines.append(f"file '{frame.as_posix()}'")
        lines.append(f"duration {scene.duration}")
    lines.append(f"file '{frame_paths[-1].as_posix()}'")
    concat_file.write_text("\n".join(lines), encoding="utf-8")

    output = EXPORTS_DIR / "bilibili_video_01_noface_draft.mp4"
    cmd = [
        ffmpeg_exe(),
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-vf",
        f"fps={FPS},format=yuv420p",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        str(output),
    ]
    subprocess.run(cmd, check=True)
    return output


def create_tts_audio() -> Path | None:
    if not (Path(r"C:\Windows\Fonts").exists() and shutil.which("powershell")):
        return None

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    narration_text = EXPORTS_DIR / "bilibili_video_01_narration.txt"
    audio_path = EXPORTS_DIR / "bilibili_video_01_tts.wav"
    narration_text.write_text("\n\n".join(scene.narration for scene in SCENES), encoding="utf-8")

    ps = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.SelectVoice('Microsoft Huihui Desktop'); "
        "$s.Rate = 0; "
        "$s.Volume = 100; "
        f"$s.SetOutputToWaveFile('{audio_path}'); "
        f"$text = Get-Content -LiteralPath '{narration_text}' -Raw -Encoding UTF8; "
        "$s.Speak($text); "
        "$s.Dispose();"
    )
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
        return audio_path
    except Exception as exc:
        print(f"TTS generation skipped: {exc}")
        return None


def mux_audio(video_path: Path, audio_path: Path) -> Path:
    output = EXPORTS_DIR / "bilibili_video_01_noface_with_tts.mp4"
    target_duration = str(sum(scene.duration for scene in SCENES))
    cmd = [
        ffmpeg_exe(),
        "-y",
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
        "160k",
        "-t",
        target_duration,
        str(output),
    ]
    subprocess.run(cmd, check=True)
    return output


def main() -> int:
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    write_text_assets()
    frames = [render_scene(scene, idx) for idx, scene in enumerate(SCENES, start=1)]
    cover = CONTENT_DIR / "cover.png"
    Image.open(frames[0]).save(cover)
    output = render_video(frames)
    audio = create_tts_audio()
    voiced_output = mux_audio(output, audio) if audio else None
    print(f"Cover: {cover}")
    print(f"Video draft: {output}")
    if voiced_output:
        print(f"Video with TTS: {voiced_output}")
    print(f"Voiceover: {CONTENT_DIR / 'bilibili_video_01_voiceover.md'}")
    print(f"Subtitles: {CONTENT_DIR / 'bilibili_video_01_subtitles.srt'}")
    print(f"Shotlist: {CONTENT_DIR / 'bilibili_video_01_shotlist.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
