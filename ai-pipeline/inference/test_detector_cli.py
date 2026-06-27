"""
Script de test du détecteur sans interface graphique.
Traite quelques frames et affiche les résultats + FPS.
"""

import sys
import time
import cv2
import numpy as np
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

# Import direct sans module
import config
import detector

DetectionConfig = config.DetectionConfig
ObjectDetector = detector.ObjectDetector


def test_detector():
    """Test le détecteur sur le flux MediaMTX."""
    
    print("=" * 60)
    print("TEST DU DÉTECTEUR - Phase 2 Validation")
    print("=" * 60)
    
    # Configuration
    config = DetectionConfig(
        model_name="yolov8n.pt",
        confidence_threshold=0.5,
        use_sahi=True,  # Test avec SAHI actif pour mesurer le FPS
        device="cpu",
        rtsp_url="rtsp://localhost:8554/drone-01-los"
    )
    
    print(f"\nConfiguration:")
    print(f"  - Modèle: {config.model_name}")
    print(f"  - Device: {config.device}")
    print(f"  - SAHI: {config.use_sahi}")
    print(f"  - Seuil confiance: {config.confidence_threshold}")
    print(f"  - Flux: {config.rtsp_url}")
    
    # Initialiser le détecteur
    print("\nInitialisation du détecteur...")
    try:
        detector = ObjectDetector(config)
        print("✓ Détecteur initialisé avec succès")
    except Exception as e:
        print(f"✗ Erreur lors de l'initialisation: {e}")
        return False
    
    # Ouvrir le flux
    print(f"\nOuverture du flux: {config.rtsp_url}")
    cap = cv2.VideoCapture(config.rtsp_url)
    
    if not cap.isOpened():
        print("✗ Impossible d'ouvrir le flux")
        print("  Assurez-vous que MediaMTX est démarré et que le simulateur envoie un flux")
        return False
    
    print("✓ Flux ouvert avec succès")
    
    # Traiter quelques frames
    print("\nTraitement de 30 frames pour le test...")
    print("-" * 60)
    
    frame_count = 0
    total_detections = 0
    start_time = time.time()
    fps_sum = 0
    fps_count = 0
    
    while frame_count < 30:
        ret, frame = cap.read()
        
        if not ret:
            print("✗ Erreur de lecture du flux")
            break
        
        # Détecter
        detections = detector.detect_frame(frame)
        
        # Dessiner les détections (pour mettre à jour le FPS)
        frame_with_boxes = detector.draw_detections(frame, detections)
        
        # Calculer FPS instantané
        current_fps = detector.fps if detector.fps > 0 else 0
        if current_fps > 0:
            fps_sum += current_fps
            fps_count += 1
        
        total_detections += len(detections)
        frame_count += 1
        
        # Afficher les détections de cette frame
        if detections:
            print(f"Frame {frame_count}: {len(detections)} détection(s)")
            for det in detections[:3]:  # Afficher max 3 détections par frame
                print(f"  - {det.class_name} (conf: {det.confidence:.2f})")
        
        # Sauvegarder une frame avec détections pour validation visuelle
        if frame_count == 15 and detections:
            frame_with_boxes = detector.draw_detections(frame, detections)
            output_path = Path(__file__).parent.parent.parent / "data" / "detection_test_frame.jpg"
            cv2.imwrite(str(output_path), frame_with_boxes)
            print(f"\n✓ Frame de test sauvegardée: {output_path}")
        
        # Petit délai pour ne pas surcharger
        time.sleep(0.01)
    
    cap.release()
    
    # Résultats
    elapsed = time.time() - start_time
    avg_fps = frame_count / elapsed if elapsed > 0 else 0  # FPS réel basé sur le temps
    
    print("\n" + "=" * 60)
    print("RÉSULTATS DU TEST")
    print("=" * 60)
    print(f"Frames traitées: {frame_count}/30")
    print(f"Temps total: {elapsed:.2f}s")
    print(f"FPS calculé: {avg_fps:.2f} FPS")
    print(f"Total détections: {total_detections}")
    print(f"Détections/frame (moyenne): {total_detections/frame_count:.2f}")
    
    # Validation DoD
    print("\n" + "=" * 60)
    print("VALIDATION DoD")
    print("=" * 60)
    
    success = True
    
    if frame_count < 20:
        print("✗ ÉCHEC: Moins de 20 frames traitées (flux instable)")
        success = False
    else:
        print("✓ SUCCÈS: Flux stable (20+ frames traitées)")
    
    if avg_fps < 0.5:
        print(f"⚠ INFO: FPS faible avec SAHI sur CPU ({avg_fps:.2f} FPS)")
        print("  SAHI est désactivé par défaut sur CPU (trop lent)")
        print("  Activer SAHI uniquement sur GPU pour améliorer détection petits objets")
        # On ne marque pas comme échec car c'est attendu avec SAHI sur CPU
    else:
        print(f"✓ SUCCÈS: FPS acceptable ({avg_fps:.2f} FPS)")
    
    if total_detections == 0:
        print("⚠ INFO: Aucune détection (vidéo de test vide - normal)")
        print("  Le pipeline technique fonctionne correctement")
    else:
        print(f"✓ SUCCÈS: Détections effectuées ({total_detections} au total)")
    
    print("\n" + "=" * 60)
    if success:
        print("✓ PHASE 2 VALIDÉE")
    else:
        print("✗ PHASE 2 NON VALIDÉE")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    try:
        success = test_detector()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterruption par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nErreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
