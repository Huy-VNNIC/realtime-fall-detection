"""AI modules initialization"""
from ai.feature_extractor import FeatureExtractor
from ai.classifier import FallClassifier, DummyClassifier

__all__ = [
    'FeatureExtractor',
    'FallClassifier',
    'DummyClassifier'
]
