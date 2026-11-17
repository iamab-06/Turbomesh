"""
Real-time hand sign inference using landmarks and RandomForest model.
Consistent with training pipeline from landmark_training.py
"""

import pickle
import numpy as np
import cv2
from PIL import Image
from typing import Optional, Tuple

try:
    import mediapipe as mp
    from mediapipe.solutions import hands as mp_hands
except ImportError:
    print("⚠ MediaPipe not fully imported. Install with: pip install --no-compile mediapipe")
    mp = None
    mp_hands = None

# Global state for model and hand detector
_loaded_model = None
_hand_detector = None
_model_metadata = None


def initialize_hand_detector():
    """Initialize MediaPipe hand detector."""
    global _hand_detector
    if _hand_detector is None:
        if mp_hands is None:
            raise ImportError("MediaPipe not available. Run: pip install --no-compile mediapipe")
        _hand_detector = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    return _hand_detector


def extract_hand_landmarks_from_frame(frame):
    """
    Extract hand landmarks from a video frame.
    
    Args:
        frame: numpy array (BGR format from OpenCV)
    
    Returns:
        landmarks: numpy array of shape (21, 3) or None
    """
    detector = initialize_hand_detector()
    
    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = detector.process(rgb_frame)
    
    if not results.multi_hand_landmarks:
        return None
    
    # Extract landmarks from first detected hand
    hand_landmarks = results.multi_hand_landmarks[0]
    landmarks = np.array([
        [lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark
    ])
    
    return landmarks


def normalize_landmarks(landmarks):
    """Normalize landmarks (same as training pipeline)."""
    if landmarks is None:
        return None
    
    # Center on wrist
    centered = landmarks - landmarks[0]
    
    # Scale by max distance
    distances = np.linalg.norm(centered, axis=1)
    max_distance = np.max(distances)
    
    if max_distance > 0:
        normalized = centered / max_distance
    else:
        normalized = centered
    
    return normalized


def extract_geometric_features(landmarks):
    """Extract geometric features (same as training pipeline)."""
    if landmarks is None:
        return None
    
    features = []
    fingertips = [4, 8, 12, 16, 20]
    wrist = landmarks[0]
    
    for tip_idx in fingertips:
        dist = np.linalg.norm(landmarks[tip_idx] - wrist)
        features.append(dist)
    
    for i in range(len(fingertips)):
        for j in range(i + 1, len(fingertips)):
            dist = np.linalg.norm(
                landmarks[fingertips[i]] - landmarks[fingertips[j]]
            )
            features.append(dist)
    
    return np.array(features)


def get_hand_features_from_frame(frame):
    """
    Extract features from a video frame (complete pipeline).
    
    Args:
        frame: numpy array (BGR from OpenCV)
    
    Returns:
        features: numpy array (78,) or None if no hand detected
    """
    landmarks = extract_hand_landmarks_from_frame(frame)
    if landmarks is None:
        return None
    
    normalized = normalize_landmarks(landmarks)
    flat = normalized.flatten().astype(np.float32)
    geometric = extract_geometric_features(normalized)
    
    if geometric is not None:
        flat = np.concatenate([flat, geometric])
    
    return flat.astype(np.float32)


def load_model(model_data: bytes, metadata: dict) -> Tuple[bool, str]:
    """
    Load RandomForest model from pickled bytes.
    
    Args:
        model_data: pickled model bytes
        metadata: model metadata dict
    
    Returns:
        (success: bool, message: str)
    """
    global _loaded_model, _model_metadata
    
    try:
        # Deserialize model
        _loaded_model = pickle.loads(model_data)
        _model_metadata = metadata
        
        num_classes = metadata.get('num_classes', 10)
        model_type = metadata.get('model_type', 'Unknown')
        
        print(f"✓ Model loaded: {model_type} with {num_classes} classes")
        return True, f"Model loaded successfully ({model_type})"
    except Exception as e:
        print(f"❌ Failed to load model: {str(e)}")
        return False, f"Failed to load model: {str(e)}"


def infer(frame) -> Optional[dict]:
    """
    Run inference on a video frame.
    
    Args:
        frame: numpy array (BGR from OpenCV or converted from PIL)
    
    Returns:
        {
            'predicted_class': str (e.g., '5'),
            'predicted_index': int,
            'confidence': float (0.0-1.0),
            'probabilities': dict,
            'hand_detected': bool
        }
        or None if model not loaded
    """
    global _loaded_model, _model_metadata
    
    if _loaded_model is None:
        return None
    
    # Extract features from frame
    features = get_hand_features_from_frame(frame)
    
    if features is None:
        return {
            'predicted_class': None,
            'predicted_index': -1,
            'confidence': 0.0,
            'probabilities': {},
            'hand_detected': False,
            'error': 'No hand detected in frame'
        }
    
    try:
        # Get prediction
        features_reshaped = features.reshape(1, -1)
        predicted_idx = _loaded_model.predict(features_reshaped)[0]
        
        # Get probabilities
        probabilities_array = _loaded_model.predict_proba(features_reshaped)[0]
        confidence = float(probabilities_array[predicted_idx])
        
        # Map index to class label
        idx_to_class = _model_metadata.get('idx_to_class', {})
        predicted_class = idx_to_class.get(str(predicted_idx), str(predicted_idx))
        
        # Build probability dict
        probabilities = {}
        for idx, prob in enumerate(probabilities_array):
            class_label = idx_to_class.get(str(idx), str(idx))
            probabilities[class_label] = float(prob)
        
        return {
            'predicted_class': predicted_class,
            'predicted_index': int(predicted_idx),
            'confidence': confidence,
            'probabilities': probabilities,
            'hand_detected': True
        }
    except Exception as e:
        print(f"Inference error: {str(e)}")
        return {
            'predicted_class': None,
            'predicted_index': -1,
            'confidence': 0.0,
            'probabilities': {},
            'hand_detected': False,
            'error': str(e)
        }


def cleanup():
    """Clean up MediaPipe resources."""
    global _hand_detector
    if _hand_detector is not None:
        _hand_detector.close()
        _hand_detector = None
