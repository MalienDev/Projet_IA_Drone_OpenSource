# Real Video End-to-End Test Report

- Date: 2026-07-01T15:25:02.452964+00:00
- Video: `C:\Users\USER\Desktop\Projet_IA_Drone_OpenSource\data\visdrone_test_video.mp4`
- HLS URL: `http://localhost:8888/drone-01-los/index.m3u8`
- Dashboard URL: `http://localhost:3000`
- Duration: 30s
- Frames processed: 176
- Pipeline FPS: 5.86
- Detections total: 371
- Alerts captured from Redis: 25
- Events returned by backend for this run: 25

## Detection Types

- bicycle: 1
- motorcycle: 30
- person: 340

## Notes

- The video, inference, Redis, API, dashboard and media files are all local.
- Weapon alerts remain operator-confirmed only and are not treated as certainty.
- SAHI is disabled by default in this CPU-oriented test profile.
