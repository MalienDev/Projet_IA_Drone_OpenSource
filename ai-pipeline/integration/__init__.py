"""
Module d'intégration bout-en-bout pour le système de surveillance par drone.

Ce module contient les scripts et outils pour tester l'intégration complète
du pipeline : ingestion → IA → règles → alertes → dashboard.
"""

from .integration_test import IntegrationTestRunner, LatencyTracker

__all__ = ['IntegrationTestRunner', 'LatencyTracker']
