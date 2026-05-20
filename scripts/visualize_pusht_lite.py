from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import imageio.v3 as iio
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pyarrow.parquet as pq


PUSHT_PARQUET_URL = (
    "https://huggingface.co/datasets/lerobot/pusht/resolve/main/data/chunk-000/file-000.parquet"
)
PUSHT_VIDEO_URL = (
    "https://huggingface.co/datasets/lerobot/pusht/resolve/main/videos/observation.image/chunk-000/file-000.mp4"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lightweight local PushT visualization without installing LeRobot.",
    )
    parser.add_argument("--episode-index", type=int, default=0, help="Episode index to visualize.")
    parser.add_argument("--data-dir", default="data/pusht_lite", help="Directory for downloaded files.")
    parser.add_argument("--assets-dir", default="assets", help="Directory for image outputs.")
    parser.add_argument("--reports-dir", default="reports", help="Directory for JSON summary output.")
    return parser.parse_args()


def download_if_missing(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        print(f"Using cached file: {output_path}")
        return

    print(f"Downloading: {url}")
    print(f"To: {output_path}")
    urllib.request.urlretrieve(url, output_path)


def fixed_size_list_to_numpy(column) -> np.ndarray:
    return np.asarray([item.as_py() for item in column], dtype=float)


def save_first_frame(video_path: Path, output_path: Path, frame_index: int) -> None:
    frame = iio.imread(video_path, index=frame_index)
    # PushT frames are 96x96. Upscale for README visibility while preserving pixels.
    if frame.shape[0] < 256:
        from PIL import Image

        image = Image.fromarray(frame)
        image = image.resize((384, 384), Image.Resampling.NEAREST)
        image.save(output_path)
    else:
        plt.imsave(output_path, frame)


def plot_action_timeseries(timestamps: np.ndarray, actions: np.ndarray, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.6, 4.2))
    for dim in range(actions.shape[1]):
        ax.plot(timestamps, actions[:, dim], label=f"action[{dim}]", linewidth=1.8)
    ax.set_title("LeRobot pusht episode action time series")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Action value")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output_path, dpi=170)
    plt.close(fig)


def plot_action_distribution(actions: np.ndarray, output_path: Path) -> None:
    fig, axes = plt.subplots(1, actions.shape[1], figsize=(9.6, 3.6))
    for dim, ax in enumerate(np.atleast_1d(axes)):
        ax.hist(actions[:, dim], bins=24, color="#3766A6", alpha=0.88)
        ax.set_title(f"action[{dim}] distribution")
        ax.set_xlabel("Action value")
        ax.set_ylabel("Count")
        ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=170)
    plt.close(fig)


def main() -> int:
    args = parse_args()
    data_dir = Path(args.data_dir)
    assets_dir = Path(args.assets_dir)
    reports_dir = Path(args.reports_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    parquet_path = data_dir / "file-000.parquet"
    video_path = data_dir / "file-000.mp4"
    download_if_missing(PUSHT_PARQUET_URL, parquet_path)
    download_if_missing(PUSHT_VIDEO_URL, video_path)

    table = pq.read_table(
        parquet_path,
        columns=["action", "episode_index", "frame_index", "timestamp"],
    )
    episode_index = np.asarray(table["episode_index"].to_pylist())
    mask = episode_index == args.episode_index
    if not mask.any():
        print(f"No records found for episode_index={args.episode_index}")
        return 1

    actions = fixed_size_list_to_numpy(table["action"].filter(mask))
    timestamps = np.asarray(table["timestamp"].filter(mask).to_pylist(), dtype=float)
    frame_indices = np.asarray(table["frame_index"].filter(mask).to_pylist(), dtype=int)

    first_frame_path = assets_dir / f"episode_{args.episode_index}_first_frame.png"
    timeseries_path = assets_dir / f"episode_{args.episode_index}_action_timeseries.png"
    distribution_path = assets_dir / f"episode_{args.episode_index}_action_distribution.png"
    summary_path = reports_dir / f"episode_{args.episode_index}_lite_summary.json"

    save_first_frame(video_path, first_frame_path, int(frame_indices[0]))
    plot_action_timeseries(timestamps, actions, timeseries_path)
    plot_action_distribution(actions, distribution_path)

    summary = {
        "repo_id": "lerobot/pusht",
        "mode": "lite_without_lerobot",
        "episode_index": args.episode_index,
        "frames": int(actions.shape[0]),
        "action_shape": list(actions.shape),
        "timestamp_range": [float(timestamps.min()), float(timestamps.max())],
        "action_mean": actions.mean(axis=0).round(6).tolist(),
        "action_std": actions.std(axis=0).round(6).tolist(),
        "action_min": actions.min(axis=0).round(6).tolist(),
        "action_max": actions.max(axis=0).round(6).tolist(),
        "outputs": {
            "first_frame": str(first_frame_path),
            "action_timeseries": str(timeseries_path),
            "action_distribution": str(distribution_path),
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Generated outputs:")
    for key, value in summary["outputs"].items():
        print(f"- {key}: {Path(value).resolve()}")
    print(f"- summary: {summary_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
