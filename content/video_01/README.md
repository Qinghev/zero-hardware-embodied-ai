# B 站视频 01：不出镜制作包

这个目录用于制作第一条不出镜视频：

```text
不用买机械臂，也能做具身智能项目：LeRobot 数据集可视化实战
```

## 已生成内容

- `cover.png`：视频封面草稿
- `bilibili_video_01_voiceover.md`：口播稿
- `bilibili_video_01_subtitles.srt`：字幕文件
- `bilibili_video_01_shotlist.md`：分镜表

## 本地生成视频

```bash
python scripts/create_noface_video_01.py
```

输出文件在：

```text
exports/bilibili_video_01_noface_draft.mp4
exports/bilibili_video_01_noface_with_tts.mp4
```

其中 `with_tts` 版本使用 Windows 自带的中文语音合成，适合作为初稿预览。正式发布前建议用剪映/CapCut 或其他工具替换成更自然的 AI 配音。
