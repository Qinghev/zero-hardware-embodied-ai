# 免费版快速开始

## 1. 创建环境

```bash
conda env create -f environment.yml
conda activate zero-embodied
```

如果你已经有 Python 3.10+ 环境，也可以直接：

```bash
pip install -r requirements.txt
```

## 2. 自检环境

```bash
python check_env.py
```

全部通过后再继续。若 ffmpeg 报错，优先使用 conda 安装：

```bash
conda install ffmpeg -c conda-forge
```

## 3. 下载数据集

```bash
python scripts/download_dataset.py --repo-id lerobot/pusht
```

默认下载到：

```text
data/lerobot__pusht
```

如果你的网络较慢，可以先不手动下载，直接运行可视化脚本；LeRobot 会按需从 Hub 缓存数据。

## 4. 可视化一个 episode

```bash
python scripts/visualize_episode_basic.py --repo-id lerobot/pusht --episode-index 0
```

生成内容：

```text
assets/episode_0_first_frame.png
assets/episode_0_action_timeseries.png
assets/episode_0_action_distribution.png
reports/episode_0_basic_summary.json
```

## 5. 你应该观察什么

- action 有几个维度
- 每个 action 维度的数值范围
- 是否存在明显异常尖峰
- episode 长度是否符合预期
- 图像帧和动作变化是否能解释任务过程

## 6. 如何写进简历

免费版可以先写成：

```text
基于 LeRobot 公开机器人数据集实现 episode 数据读取与 action 可视化分析，完成机器人 observation/action 数据结构理解、轨迹统计和基础可视化结果输出。
```

完整版会提供更完整的中文/英文简历描述、报告模板和面试讲解稿。
