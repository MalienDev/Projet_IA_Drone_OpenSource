#!/usr/bin/env python3
"""
Script de validation visuelle des détections sur vidéo aérienne.

Ce script permet de visualiser les détections en temps réel sur une vidéo
pour valider la qualité des détections sur de vraies scènes aériennes.

Usage:
    python visual_validation.py --video <path> [--duration <seconds>]
"""

import argparse
import sys
from pathlib import Path

# Ajouter le répertoire ai-pipeline au path
ai_pipeline_path = Path(__file__).parent.parent
sys.path.insert(0, str(ai_pipeline_path))

from inference.detector import ObjectDetector, DetectionConfig


def main():
    parser = argparse.ArgumentParser(description="Validation visuelle des détections")
    parser.add_argument(
        "--video",
        type=str,
        required=True,
        help="Chemin vers la vidéo à traiter"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="Durée du test en secondes (0 = illimité)"
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.5,
        help="Seuil de confiance (défaut: 0.5)"
    )
    parser.add_argument(
        "--no-tracking",
        action="store_true",
        help="Désactiver le tracking"
    )
    parser.add_argument(
        "--no-rules",
        action="store_true",
        help="Désactiver le moteur de règles"
    )
    
    args = parser.parse_args()
    
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Erreur: Vidéo non trouvée: {video_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("VALIDATION VISUELLE DES DÉTECTIONS")
    print("=" * 60)
    print(f"Vidéo: {video_path}")
    print(f"Durée: {args.duration}s (0 = illimité)")
    print(f"Confiance: {args.confidence}")
    print(f"Tracking: {'OFF' if args.no_tracking else 'ON'}")
    print(f"Moteur de règles: {'OFF' if args.no_rules else 'ON'}")
    print("=" * 60)
    
    # Configuration du détecteur
    config = DetectionConfig(
        rtsp_url=str(video_path),  # Utiliser le chemin direct pour une vidéo locale
        model_path="yolov8n.pt",
        confidence_threshold=args.confidence,
        use_tracking=not args.no_tracking,
        enable_rules_engine=not args.no_rules,
        enable_alert_publishing=False,  # Pas de Redis pour la validation visuelle
        enable_media_storage=False  # Pas de stockage pour la validation visuelle
    )
    
    # Créer le détecteur
    detector = ObjectDetector(config)
    
    # Modifier process_stream pour accepter une durée limite
    import cv2
    import time
    import threading
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Erreur: Impossible d'ouvrir la vidéo: {video_path}")
        sys.exit(1)
    
    print("✅ Vidéo ouverte avec succès")
    print("⌨️  Appuyez sur 'q' pour quitter")
    print("=" * 60)
    
    start_time = time.time()
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Fin de la vidéo")
                break
            
            # Détecter les objets
            detections = detector.detect_frame(frame)
            
            # Dessiner les détections
            frame_with_detections = detector.draw_detections(frame, detections)
            
            # Afficher
            cv2.imshow("Validation Visuelle - Drone Surveillance", frame_with_detections)
            
            frame_count += 1
            
            # Vérifier la durée limite
            if args.duration > 0:
                elapsed = time.time() - start_time
                if elapsed >= args.duration:
                    print(f"Durée limite atteinte ({args.duration}s)")
                    break
            
            # Quitter avec 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Arrêt demandé par l'utilisateur")
                break
    
    except KeyboardInterrupt:
        print("Interruption par l'utilisateur")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        
        print("=" * 60)
        print("STATISTIQUES")
        print("=" * 60)
        print(f"Durée: {elapsed:.2f}s")
        print(f"Frames traitées: {frame_count}")
        print(f"FPS moyen: {fps:.2f}")
        print("=" * 60)


if __name__ == "__main__":
    main()
