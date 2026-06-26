#!/bin/bash
# Generate Test Video for Drone Simulation (Linux/Mac)
# Creates a synthetic test video using FFmpeg for development/testing

OUTPUT_PATH="${1:-./test-video.mp4}"
DURATION="${2:-30}"
RESOLUTION="${3:-1280x720}"
FPS="${4:-30}"

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: FFmpeg is not installed or not in PATH. Please install FFmpeg first."
    exit 1
fi

echo "Generating test video..."
echo "Output: $OUTPUT_PATH"
echo "Duration: ${DURATION}s, Resolution: $RESOLUTION, FPS: $FPS"

# Generate a test video with testsrc2
ffmpeg -f lavfi -i "testsrc2=duration=$DURATION:size=$RESOLUTION:rate=$FPS" \
    -c:v libx264 -preset fast -crf 23 \
    -pix_fmt yuv420p \
    -movflags +faststart \
    "$OUTPUT_PATH"

if [ $? -eq 0 ]; then
    echo "Test video generated successfully: $OUTPUT_PATH"
else
    echo "Error: Failed to generate test video."
    exit 1
fi
