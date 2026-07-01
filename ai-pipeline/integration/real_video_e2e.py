#!/usr/bin/env python3
"""
Run a local end-to-end test with a real drone/aerial video.

Flow:
1. FFmpeg loops a local MP4 into MediaMTX.
2. The dashboard can read the MediaMTX HLS republication.
3. The AI pipeline reads the RTSP republication.
4. Alerts are published to Redis.
5. The backend persists Redis alerts and serves them through the API.
"""

import argparse
import http.cookiejar
import json
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import cv2
import redis

AI_PIPELINE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = AI_PIPELINE_DIR.parent
sys.path.insert(0, str(AI_PIPELINE_DIR))

from inference.detector import DetectionConfig, ObjectDetector


class RedisAlertCollector:
    """Collect Redis alerts published during the test window."""

    def __init__(self, host: str, port: int, channel: str):
        self.host = host
        self.port = port
        self.channel = channel
        self.alerts: list[dict[str, Any]] = []
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._client: Optional[redis.Redis] = None
        self._pubsub = None

    def start(self) -> None:
        self._client = redis.Redis(
            host=self.host,
            port=self.port,
            decode_responses=True,
        )
        self._client.ping()
        self._pubsub = self._client.pubsub(ignore_subscribe_messages=True)
        self._pubsub.subscribe(self.channel)
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def _listen(self) -> None:
        while not self._stop_event.is_set():
            message = self._pubsub.get_message(timeout=0.5)
            if not message or message.get("type") != "message":
                continue
            try:
                self.alerts.append(json.loads(message["data"]))
            except json.JSONDecodeError:
                continue

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
        if self._pubsub:
            self._pubsub.close()
        if self._client:
            self._client.close()


def start_ffmpeg_publisher(
    video_path: Path,
    publish_url: str,
    fps: int,
    resolution: str,
) -> subprocess.Popen:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "warning",
        "-re",
        "-stream_loop",
        "-1",
        "-i",
        str(video_path),
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-tune",
        "zerolatency",
        "-g",
        str(fps),
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(fps),
        "-s",
        resolution,
        "-f",
        "flv",
        publish_url,
    ]
    return subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def wait_for_hls(hls_url: str, timeout_seconds: int) -> None:
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookie_jar),
        urllib.request.HTTPRedirectHandler(),
    )
    deadline = time.time() + timeout_seconds
    last_error = None

    while time.time() < deadline:
        try:
            with opener.open(hls_url, timeout=5) as response:
                content = response.read(4096).decode("utf-8", errors="replace")
            if "#EXTM3U" in content:
                return
            last_error = f"HLS response did not contain #EXTM3U: {content[:80]}"
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc)
        time.sleep(1)

    raise TimeoutError(f"HLS stream not ready at {hls_url}: {last_error}")


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(url: str, token: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_backend_events(api_base_url: str, token: str, start_time: str) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({"limit": 1000, "start_time": start_time})
    return get_json(f"{api_base_url.rstrip('/')}/api/events/?{query}", token)


def run_detection_loop(detector: ObjectDetector, rtsp_url: str, duration_seconds: int) -> dict[str, Any]:
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open RTSP stream: {rtsp_url}")

    frames_processed = 0
    detections_total = 0
    detection_types: Counter[str] = Counter()
    latencies_ms: list[float] = []
    started_at = time.time()
    deadline = started_at + duration_seconds

    try:
        while time.time() < deadline:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.1)
                continue

            frame_started_at = time.time()
            detections = detector.detect_frame(frame)
            latencies_ms.append((time.time() - frame_started_at) * 1000)

            frames_processed += 1
            detections_total += len(detections)
            detection_types.update(detection.class_name for detection in detections)
    finally:
        cap.release()

    elapsed = max(time.time() - started_at, 0.001)
    avg_latency_ms = sum(latencies_ms) / len(latencies_ms) if latencies_ms else 0.0

    return {
        "elapsed_seconds": elapsed,
        "frames_processed": frames_processed,
        "pipeline_fps": frames_processed / elapsed,
        "detections_total": detections_total,
        "detection_types": dict(detection_types),
        "avg_inference_latency_ms": avg_latency_ms,
        "max_inference_latency_ms": max(latencies_ms) if latencies_ms else 0.0,
        "min_inference_latency_ms": min(latencies_ms) if latencies_ms else 0.0,
    }


def write_reports(report: dict[str, Any]) -> None:
    docs_dir = REPO_ROOT / "docs"
    docs_dir.mkdir(exist_ok=True)

    json_path = docs_dir / "real-video-e2e-report.json"
    md_path = docs_dir / "real-video-e2e-report.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Real Video End-to-End Test Report",
        "",
        f"- Date: {report['test_date']}",
        f"- Video: `{report['video_path']}`",
        f"- HLS URL: `{report['hls_url']}`",
        f"- Dashboard URL: `{report['dashboard_url']}`",
        f"- Duration: {report['duration_seconds']}s",
        f"- Frames processed: {report['ai_metrics']['frames_processed']}",
        f"- Pipeline FPS: {report['ai_metrics']['pipeline_fps']:.2f}",
        f"- Detections total: {report['ai_metrics']['detections_total']}",
        f"- Alerts captured from Redis: {report['redis_alert_count']}",
        f"- Events returned by backend for this run: {report['backend_event_count']}",
        "",
        "## Detection Types",
        "",
    ]

    for detection_type, count in sorted(report["ai_metrics"]["detection_types"].items()):
        lines.append(f"- {detection_type}: {count}")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- The video, inference, Redis, API, dashboard and media files are all local.",
            "- Weapon alerts remain operator-confirmed only and are not treated as certainty.",
            "- SAHI is disabled by default in this CPU-oriented test profile.",
        ]
    )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a real local drone-video E2E test")
    parser.add_argument("--video", default="data/visdrone_test_video.mp4")
    parser.add_argument("--duration", type=int, default=45)
    parser.add_argument("--stream-name", default="drone-01-los")
    parser.add_argument("--publish-url", default="rtmp://localhost:1935/drone-01-los")
    parser.add_argument("--rtsp-url", default="rtsp://localhost:8554/drone-01-los")
    parser.add_argument("--hls-base-url", default="http://localhost:8888")
    parser.add_argument("--dashboard-url", default="http://localhost:3000")
    parser.add_argument("--api-base-url", default="http://localhost:8000")
    parser.add_argument("--redis-host", default="localhost")
    parser.add_argument("--redis-port", type=int, default=6379)
    parser.add_argument("--redis-channel", default="alerts")
    parser.add_argument("--admin-user", default="admin")
    parser.add_argument("--admin-password", default="admin123")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--resolution", default="1344x756")
    parser.add_argument("--confidence", type=float, default=0.5)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--use-sahi", action="store_true")
    parser.add_argument("--enable-weapon-model", action="store_true")
    parser.add_argument("--no-simulator", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    video_path = (REPO_ROOT / args.video).resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    hls_url = f"{args.hls_base_url.rstrip('/')}/{args.stream_name}/index.m3u8"
    simulator_process = None
    collector = RedisAlertCollector(args.redis_host, args.redis_port, args.redis_channel)
    start_time = datetime.now(timezone.utc).isoformat()

    try:
        if not args.no_simulator:
            simulator_process = start_ffmpeg_publisher(
                video_path=video_path,
                publish_url=args.publish_url,
                fps=args.fps,
                resolution=args.resolution,
            )
            time.sleep(3)

        wait_for_hls(hls_url, timeout_seconds=30)

        login_response = post_json(
            f"{args.api_base_url.rstrip('/')}/api/auth/login",
            {"username": args.admin_user, "password": args.admin_password},
        )
        token = login_response["access_token"]

        collector.start()

        config = DetectionConfig(
            rtsp_url=args.rtsp_url,
            model_name="yolov8n.pt",
            confidence_threshold=args.confidence,
            device=args.device,
            use_sahi=args.use_sahi,
            use_tracking=True,
            enable_rules_engine=True,
            enable_alert_publishing=True,
            redis_host=args.redis_host,
            redis_port=args.redis_port,
            redis_channel=args.redis_channel,
            enable_media_storage=True,
            storage_dir=str(REPO_ROOT / "data" / "media"),
            weapon_model_enabled=args.enable_weapon_model,
        )
        detector = ObjectDetector(config)
        ai_metrics = run_detection_loop(detector, args.rtsp_url, args.duration)

        time.sleep(2)
        backend_events = fetch_backend_events(args.api_base_url, token, start_time)

        report = {
            "test_date": datetime.now(timezone.utc).isoformat(),
            "video_path": str(video_path),
            "duration_seconds": args.duration,
            "stream_name": args.stream_name,
            "publish_url": args.publish_url,
            "rtsp_url": args.rtsp_url,
            "hls_url": hls_url,
            "dashboard_url": args.dashboard_url,
            "ai_metrics": ai_metrics,
            "redis_alert_count": len(collector.alerts),
            "redis_alert_types": dict(Counter(alert.get("type", "unknown") for alert in collector.alerts)),
            "backend_event_count": len(backend_events),
            "backend_event_types": dict(Counter(event.get("event_type", "unknown") for event in backend_events)),
            "local_only": True,
        }
        write_reports(report)

        print(json.dumps(report, indent=2))
        return 0
    finally:
        collector.stop()
        if simulator_process:
            simulator_process.terminate()
            try:
                simulator_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                simulator_process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
