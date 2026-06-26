#!/bin/bash
# Drone BLOS Stream Simulator (Linux/Mac)
# Simulates a Beyond Line Of Sight (BLOS) drone stream via SRT protocol

VIDEO_PATH="${1:-./test-video.mp4}"
STREAM_URL="${2:-srt://localhost:6001?mode=caller}"
FPS="${3:-30}"
RESOLUTION="${4:-1280x720}"

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: FFmpeg is not installed or not in PATH. Please install FFmpeg first."
    exit 1
fi

# Check if video file exists
if [ ! -f "$VIDEO_PATH" ]; then
    echo "Error: Video file not found: $VIDEO_PATH"
    echo "Please provide a valid video file path."
    exit 1
fi

echo "Starting BLOS stream simulation..."
echo "Video: $VIDEO_PATH"
echo "Stream URL: $STREAM_URL"
echo "FPS: $FPS, Resolution: $RESOLUTION"
echo "Press Ctrl+C to stop the stream"

# FFmpeg command to stream video via SRT
ffmpeg -re -stream_loop -1 -i "$VIDEO_PATH" \
    -c:v libx264 -preset ultrafast -tune zerolatency \
    -pix_fmt yuv420p -r "$FPS" -s "$RESOLUTION" \
    -f mpegts "$STREAM_URL"
