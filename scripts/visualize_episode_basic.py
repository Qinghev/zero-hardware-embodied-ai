from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


DEFAULT_REPO_ID = "lerobot/pusht"


def import_lerobot_dataset() -> type:
    try:
        from lerobot.datasets.lerobot_dataset import LeRobotDataset

        return LeRobotDataset
    except Exception:
        from lerobot.common.datasets.lerobot_dataset import LeRobotDataset

        return LeRobotDataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualize one LeRobot dataset episode with action plots and a first-frame preview.",
    )
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID, help="Hugging Face dataset repo id.")
    parser.add_argument("--episode-index", type=int, default=0, help="Episode index to visualize.")
    parser.add_argument(
        "--root",
        default=None,
        help="Optional local dataset/cache root if you already downloaded the dataset.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=300,
        help="Maximum frames to scan from the selected episode.",
    )
    parser.add_argument("--assets-dir", default="assets", help="Directory for image outputs.")
    parser.add_argument("--reports-dir", default="reports", help="Directory for JSON summary output.")
    return parser.parse_args()


def to_numpy(value: Any) -> np.ndarray:
    if hasattr(value, "detach"):
        value = value.detach().cpu().numpy()
    elif hasattr(value, "cpu") and hasattr(value, "numpy"):
        value = value.cpu().numpy()
    elif hasattr(value, "numpy"):
        value = value.numpy()
    return np.asarray(value)


def to_scalar(value: Any) -> int | float | str:
    array = to_numpy(value)
    if array.shape == ():
        scalar = array.item()
        if isinstance(scalar, (np.integer, np.floating)):
            return scalar.item()
        return scalar
    if array.size == 1:
        return array.reshape(-1)[0].item()
    return str(value)


def image_to_hwc(image: Any) -> np.ndarray:
    array = to_numpy(image)
    if array.ndim == 4:
        array = array[0]
    if array.ndim == 3 and array.shape[0] in (1, 3, 4):
        array = np.moveaxis(array, 0, -1)
    if np.issubdtype(array.dtype, np.floating):
        max_value = float(np.nanmax(array)) if array.size else 1.0
        if max_value <= 1.0:
            array = array * 255.0
        array = np.clip(array, 0, 255).astype(np.uint8)
    return array


def find_image_key(sample: dict[str, Any]) -> str | None:
    preferred = [
        "observation.images.front",
        "observation.images.front_left",
        "observation.image",
        "image",
    ]
    for key in preferred:
        if key in sample:
            return key
    for key in sample:
        if "image" in key:
            return key
    return None


def load_dataset(repo_id: str, root: str | None) -> Any:
    LeRobotDataset = import_lerobot_dataset()
    if root:
        return LeRobotDataset(repo_id, root=root)
    return LeRobotDataset(repo_id)


def collect_episode(dataset: Any, episode_index: int, max_frames: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    started = False

    for dataset_index in range(len(dataset)):
        sample = dataset[dataset_index]
        sample_episode = int(to_scalar(sample.get("episode_index", 0)))

        if sample_episode == episode_index:
            started = True
            records.append(sample)
        elif started:
            break

        if len(records) >= max_frames:
            break

    return records


def plot_action_timeseries(actions: np.ndarray, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    for dim in range(actions.shape[1]):
        ax.plot(actions[:, dim], label=f"a{dim}", linewidth=1.4)
    ax.set_title("Action time series")
    ax.set_xlabel("Frame")
    ax.set_ylabel("Action value")
    ax.grid(True, alpha=0.25)
    if actions.shape[1] <= 8:
        ax.legend(ncol=min(actions.shape[1], 4), fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_action_distribution(actions: np.ndarray, output_path: Path) -> None:
    dims = actions.shape[1]
    cols = min(dims, 3)
    rows = int(np.ceil(dims / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 2.8 * rows), squeeze=False)
    for dim, ax in enumerate(axes.reshape(-1)):
        if dim >= dims:
            ax.axis("off")
            continue
        ax.hist(actions[:, dim], bins=30, color="#3766A6", alpha=0.85)
        ax.set_title(f"action[{dim}]")
        ax.grid(True, alpha=0.2)

    fig.suptitle("Action distribution", y=1.01)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def save_first_frame(sample: dict[str, Any], output_path: Path) -> str | None:
    image_key = find_image_key(sample)
    if image_key is None:
        return None

    image = image_to_hwc(sample[image_key])
    plt.imsave(output_path, image)
    return image_key


def main() -> int:
    args = parse_args()
    assets_dir = Path(args.assets_dir)
    reports_dir = Path(args.reports_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading dataset: {args.repo_id}")
    dataset = load_dataset(args.repo_id, args.root)
    print(f"Dataset length: {len(dataset)} frames")

    records = collect_episode(dataset, args.episode_index, args.max_frames)
    if not records:
        print(f"No records found for episode_index={args.episode_index}")
        return 1

    actions = np.stack([to_numpy(sample["action"]).reshape(-1) for sample in records], axis=0)

    first_frame_path = assets_dir / f"episode_{args.episode_index}_first_frame.png"
    image_key = save_first_frame(records[0], first_frame_path)

    timeseries_path = assets_dir / f"episode_{args.episode_index}_action_timeseries.png"
    distribution_path = assets_dir / f"episode_{args.episode_index}_action_distribution.png"
    plot_action_timeseries(actions, timeseries_path)
    plot_action_distribution(actions, distribution_path)

    summary = {
        "repo_id": args.repo_id,
        "episode_index": args.episode_index,
        "frames_scanned": len(records),
        "action_shape": list(actions.shape),
        "action_mean": actions.mean(axis=0).round(6).tolist(),
        "action_std": actions.std(axis=0).round(6).tolist(),
        "action_min": actions.min(axis=0).round(6).tolist(),
        "action_max": actions.max(axis=0).round(6).tolist(),
        "image_key": image_key,
        "outputs": {
            "first_frame": str(first_frame_path) if image_key else None,
            "action_timeseries": str(timeseries_path),
            "action_distribution": str(distribution_path),
        },
    }

    summary_path = reports_dir / f"episode_{args.episode_index}_basic_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Generated outputs:")
    for key, value in summary["outputs"].items():
        if value:
            print(f"- {key}: {Path(value).resolve()}")
    print(f"- summary: {summary_path.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
