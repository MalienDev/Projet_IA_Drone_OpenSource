# Drone BLOS Stream Simulator (Windows PowerShell)
# Simulates a Beyond Line Of Sight (BLOS) drone stream via SRT protocol

param(
    [string]$VideoPath = ".\test-video.mp4",
    [string]$StreamUrl = "rtmp://localhost:1935/drone-01-blos",
    [int]$Fps = 30,
    [string]$Resolution = "1280x720"
)

# Check if FFmpeg is available
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Error "FFmpeg is not installed or not in PATH. Please install FFmpeg first."
    exit 1
}

# Check if video file exists
if (-not (Test-Path $VideoPath)) {
    Write-Error "Video file not found: $VideoPath"
    Write-Host "Please provide a valid video file path."
    exit 1
}

Write-Host "Starting BLOS stream simulation..." -ForegroundColor Green
Write-Host "Video: $VideoPath" -ForegroundColor Cyan
Write-Host "Stream URL: $StreamUrl" -ForegroundColor Cyan
Write-Host "FPS: $Fps, Resolution: $Resolution" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the stream" -ForegroundColor Yellow

# FFmpeg command to stream video via RTMP
# -re: read input at native frame rate
# -stream_loop -1: loop infinitely
# -c:v libx264: H.264 encoding
# -preset ultrafast: fastest encoding for low latency
# -tune zerolatency: optimize for live streaming
# -g 30: keyframe interval
# -f flv: FLV output format for RTMP
ffmpeg -re -stream_loop -1 -i $VideoPath `
    -c:v libx264 -preset ultrafast -tune zerolatency -g 30 `
    -pix_fmt yuv420p -r $Fps -s $Resolution `
    -f flv $StreamUrl
