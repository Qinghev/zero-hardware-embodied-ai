# B 站视频脚本 01

## 标题

没有机器人硬件，如何跑通第一个具身智能项目？LeRobot 数据集可视化实战

## 视频目标

让观众在前 30 秒看到结果，并相信这个项目不需要机械臂、不需要 GPU，也可以成为一个简历项目的起点。

## 时长

建议 8-12 分钟。第一版也可以先录 3-5 分钟 MVP 版本。

## 结构

### 0:00-0:30 展示结果

画面：

- GitHub README 第一屏
- demo first frame
- action time series
- action distribution
- Colab 运行结果

口播：

```text
很多人想入门具身智能，第一反应是买机械臂。但其实第一个项目不应该先买硬件，而应该先理解机器人数据。

这个视频演示一个零硬件项目：用 LeRobot 的公开 PushT 数据集，完成 episode 可视化和 action 分布分析。最后这些图和报告可以放进 GitHub，也可以写进简历。
```

### 0:30-1:30 适合谁

口播：

```text
这个项目适合会一点 Python，想入门 robot learning、具身智能、VLA，或者想准备机器人/AI 实习项目的同学。

它不适合完全不会编程、只想看科普、或者想马上控制真实机器人的用户。
```

画面：

- README 的“适合谁 / 不适合谁”

### 1:30-2:30 项目是什么

口播：

```text
我们不训练大模型，也不控制真实机器人。第一步只做一件事：读懂机器人数据。

这里的关键词是 episode、observation、action。episode 是一次完整任务轨迹，observation 是机器人看到或感知到的状态，action 是策略或操作记录下来的动作。
```

画面：

- README demo 图
- `assets/demo_action_timeseries.png`

### 2:30-4:30 Colab 跑通

画面：

- 打开 GitHub README
- 点击 Open in Colab
- 连接 runtime
- 运行 quick start notebook

口播：

```text
项目 01 不需要 GPU，所以 Colab 里选 None 就可以。这个 notebook 默认跑轻量版，不先安装完整 LeRobot，减少环境问题。

它会 clone GitHub 仓库，安装轻量依赖，下载 PushT 的小型 parquet 和 mp4 文件，然后生成三张图。
```

### 4:30-6:30 解释输出

画面：

- `episode_0_first_frame.png`
- `episode_0_action_timeseries.png`
- `episode_0_action_distribution.png`
- `episode_0_lite_summary.json`

口播：

```text
第一张图是 episode 的首帧。第二张图是 action 随时间变化，可以看到两个动作维度在 16 秒轨迹里的变化。第三张图是 action 分布，能帮助我们检查动作范围、集中区间和异常值。

这类分析虽然基础，但很适合作为入门项目，因为它让你真正接触机器人学习的数据结构，而不是只看概念。
```

### 6:30-8:00 如何写进简历

口播：

```text
这个项目可以这样写：

基于 LeRobot 公开机器人数据集实现 episode 数据读取与 action 可视化分析，完成机器人 observation/action 数据结构理解、轨迹统计和基础可视化结果输出。

英文可以写成：

Built a zero-hardware robot learning data analysis project with LeRobot PushT data, including episode loading, action trajectory visualization, action distribution analysis, and a reproducible project summary.
```

画面：

- README 的作品集描述
- GitHub 仓库结构

### 8:00-9:00 引导

口播：

```text
免费版代码已经放在 GitHub，支持 Colab 和本地轻量版。如果你打不开 Colab，也可以本地运行 requirements-lite。

后面我会继续做完整项目包，包括数据质量检查、HTML 报告、简历模板、面试问答和常见错误排查。
```

画面：

- GitHub repo URL
- README quick start

## 视频简介

```text
很多人想入门具身智能，但一上来就卡在机械臂、仿真环境、论文和代码。
这个视频演示一个零硬件项目：用 LeRobot PushT 数据集完成 episode 可视化和 action 分布分析。

免费代码：
GitHub：https://github.com/Qinghev/zero-hardware-embodied-ai

适合：
- 会 Python
- 想入门机器人 AI / 具身智能 / VLA
- 想做一个可以写进简历的项目
- 暂时没有机器人硬件

不适合：
- 完全不会编程
- 想马上控制真实机器人
- 只想看科普不想跑代码
```

## 置顶评论

```text
免费版代码已放 GitHub：
https://github.com/Qinghev/zero-hardware-embodied-ai

建议先跑 Colab quick start。如果 Colab 不稳定，也可以用本地轻量版：
pip install -r requirements-lite.txt
python scripts/visualize_pusht_lite.py --episode-index 0
```
