# Drone Stream Simulator

This directory contains scripts to simulate drone video streams for development and testing without requiring actual drone hardware.

## Purpose

The simulator uses FFmpeg to loop a test video and push it to MediaMTX via different protocols:
- **LOS (Line Of Sight)**: RTSP protocol (simulates direct radio link)
- **BLOS (Beyond Line Of Sight)**: SRT protocol (simulates satellite/cellular link)

## Requirements

- FFmpeg installed and available in PATH
- A test video file (preferably aerial/drone footage)
- MediaMTX running (via `docker compose up mediamtx`)

## Usage

### 1. Prepare test video

Place a test video file in this directory or reference an existing one:
```bash
# Example: download a sample aerial video
# Or use any MP4 file you have
```

### 2. Start MediaMTX

```bash
docker compose up -d mediamtx
```

### 3. Run simulator scripts

#### Windows (PowerShell)
```powershell
# LOS simulation (RTSP)
.\ai-pipeline\simulator\simulate-los.ps1

# BLOS simulation (SRT)
.\ai-pipeline\simulator\simulate-blos.ps1
```

### Afficher la vraie video VisDrone dans le dashboard

Depuis la racine du depot :

```powershell
docker compose up -d
.\ai-pipeline\simulator\simulate-los.ps1 -VideoPath .\data\visdrone_test_video.mp4 -StreamUrl rtmp://localhost:1935/drone-01-los -Fps 30 -Resolution 1344x756
```

Tant que cette commande reste ouverte, le dashboard peut lire le flux local :

- Dashboard : http://localhost:3000
- HLS MediaMTX : http://localhost:8888/drone-01-los/index.m3u8

Connexion par defaut si la base est seedee : `admin` / `admin123`.

#### Linux/Mac
```bash
# LOS simulation (RTSP)
./ai-pipeline/simulator/simulate-los.sh

# BLOS simulation (SRT)
./ai-pipeline/simulator/simulate-blos.sh
```

## Configuration

Edit the simulator scripts to change:
- Video file path
- Stream URL endpoints
- Video encoding parameters
- FPS and resolution

## Test Videos

Recommended sources for test videos:
- VisDrone dataset (https://github.com/VisDrone/VisDrone-Dataset)
- UAVDT dataset (https://github.com/SUTDCV/UAVDT)
- Any aerial/drone footage MP4 files
