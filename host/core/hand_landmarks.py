"""
Hand landmark extraction and normalization using MediaPipe.
Provides consistent feature representation for both training and inference.
"""

import numpy as np
import cv2
from PIL import Image

try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
except (ImportError, AttributeError):
    print("⚠ MediaPipe not fully imported. Install with: pip install --no-compile mediapipe")
    mp = None
    mp_hands = None

def extract_hand_landmarks(image_input):
    """
    Extract 21 hand landmarks from an image.
    
    Args:
        image_input: PIL Image or numpy array
    
    Returns:
        landmarks: numpy array of shape (21, 3) with normalized x, y, z coordinates
        or None if no hand detected
    """
    if mp_hands is None:
        raise ImportError("MediaPipe not available. Run: pip install --no-compile mediapipe")
    
    # Convert to numpy array if PIL Image
    if isinstance(image_input, Image.Image):
        image = np.array(image_input.convert('RGB'))
    else:
        image = image_input
    
    # Ensure image is RGB
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    
    def _try_detect(img_rgb):
        """img_rgb must be in RGB format."""
        with mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.3
        ) as hands:
            results = hands.process(img_rgb)
        return results
    
    # Try 1: original image (already RGB)
    results = _try_detect(image)
    
    # Try 2: CLAHE contrast enhancement (fixes overexposed images)
    if not results.multi_hand_landmarks:
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        results = _try_detect(enhanced)
    
    # Try 3: darken overexposed areas
    if not results.multi_hand_landmarks:
        darkened = cv2.convertScaleAbs(image, alpha=0.6, beta=-30)
        results = _try_detect(darkened)
    
    # Try 4: gamma correction to recover detail in blown-out highlights
    if not results.multi_hand_landmarks:
        gamma = 0.4
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
        gamma_corrected = cv2.LUT(image, table)
        results = _try_detect(gamma_corrected)
    
    if not results.multi_hand_landmarks:
        return None
    
    # Extract landmarks from first detected hand
    hand_landmarks = results.multi_hand_landmarks[0]
    landmarks = np.array([
        [lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark
    ])
    
    return landmarks


def normalize_landmarks(landmarks):
    """
    Normalize landmarks to be invariant to hand position and scale.
    
    Normalization strategy:
    1. Center landmarks relative to wrist (landmark 0)
    2. Scale to unit variance based on hand size
    
    Args:
        landmarks: numpy array of shape (21, 3)
    
    Returns:
        normalized: numpy array of shape (21, 3) with normalized coordinates
    """
    if landmarks is None:
        return None
    
    # Center on wrist (landmark 0)
    centered = landmarks - landmarks[0]
    
    # Scale by max distance to normalize hand size
    # Use the distance from wrist to the farthest landmark
    distances = np.linalg.norm(centered, axis=1)
    max_distance = np.max(distances)
    
    if max_distance > 0:
        normalized = centered / max_distance
    else:
        normalized = centered
    
    return normalized


def flatten_landmarks(landmarks):
    """
    Flatten 21 landmarks (x, y, z) to a 1D feature vector (63 features).
    
    Args:
        landmarks: numpy array of shape (21, 3)
    
    Returns:
        features: numpy array of shape (63,)
    """
    if landmarks is None:
        return None
    return landmarks.flatten()


def extract_geometric_features(landmarks):
    """
    Extract additional geometric features from hand landmarks.
    
    Features:
    - Distances between consecutive finger landmarks
    - Angles between landmarks
    - Palm area estimates
    
    Args:
        landmarks: numpy array of shape (21, 3)
    
    Returns:
        features: numpy array with additional geometric features
    """
    if landmarks is None:
        return None
    
    features = []
    
    # Distance between wrist and each fingertip (5, 9, 13, 17, 21)
    fingertips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
    wrist = landmarks[0]
    
    for tip_idx in fingertips:
        dist = np.linalg.norm(landmarks[tip_idx] - wrist)
        features.append(dist)
    
    # Distance between consecutive fingertips
    for i in range(len(fingertips)):
        for j in range(i + 1, len(fingertips)):
            dist = np.linalg.norm(
                landmarks[fingertips[i]] - landmarks[fingertips[j]]
            )
            features.append(dist)
    
    return np.array(features)


def get_hand_features(image_input, include_geometric=True):
    """
    Complete pipeline: extract landmarks → normalize → flatten → optionally add geometric features.
    
    Args:
        image_input: PIL Image or numpy array
        include_geometric: if True, append geometric features
    
    Returns:
        features: 1D numpy array suitable for classifier input
    """
    landmarks = extract_hand_landmarks(image_input)
    
    if landmarks is None:
        return None
    
    normalized = normalize_landmarks(landmarks)
    flat = flatten_landmarks(normalized)
    
    if include_geometric:
        geometric = extract_geometric_features(normalized)
        if geometric is not None:
            flat = np.concatenate([flat, geometric])
    
    return flat.astype(np.float32)
