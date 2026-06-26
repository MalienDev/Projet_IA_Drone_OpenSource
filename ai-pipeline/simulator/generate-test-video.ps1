# Generate Test Video for Drone Simulation (Windows PowerShell)
# Creates a synthetic test video using FFmpeg for development/testing

param(
    [string]$OutputPath = ".\test-video.mp4",
    [int]$Duration = 30,
    [string]$Resolution = "1280x720",
    [int]$Fps = 30
)

# Check if FFmpeg is available
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Error "FFmpeg is not installed or not in PATH. Please install FFmpeg first."
    exit 1
}

Write-Host "Generating test video..." -ForegroundColor Green
Write-Host "Output: $OutputPath" -ForegroundColor Cyan
Write-Host "Duration: ${Duration}s, Resolution: $Resolution, FPS: $Fps" -ForegroundColor Cyan

# Generate a test video with:
# - testsrc2: FFmpeg's built-in test pattern generator
# - Moving objects and colors to simulate drone footage
# - H.264 encoding for compatibility
$testSrcArgs = "testsrc2=duration=$($Duration):size=$($Resolution):rate=$($Fps)"
ffmpeg -f lavfi -i $testSrcArgs `
    -c:v libx264 -preset fast -crf 23 `
    -pix_fmt yuv420p `
    -movflags +faststart `
    $OutputPath

if ($?) {
    Write-Host "Test video generated successfully: $OutputPath" -ForegroundColor Green
} else {
    Write-Error "Failed to generate test video."
    exit 1
}
