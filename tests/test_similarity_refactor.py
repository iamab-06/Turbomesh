import os
import json
import numpy as np
import cv2
import pytest
from host.core.deep_similarity import (
    compute_entity_diff_from_detections,
    compute_orb_and_alignment,
    compute_aligned_ssim_and_diff,
    compute_region_level_metrics,
    rule_based_forensic_synthesis,
    run_deep_image_similarity
)

def test_class_count_set_diffing():
    # Case: Image 1 has 3 persons, Image 2 has 2 persons and 1 car
    det1 = [
        {'class_name': 'person', 'conf': 0.9, 'box': [10, 10, 100, 100]},
        {'class_name': 'person', 'conf': 0.85, 'box': [110, 10, 200, 100]},
        {'class_name': 'person', 'conf': 0.8, 'box': [210, 10, 300, 100]}
    ]
    det2 = [
        {'class_name': 'person', 'conf': 0.95, 'box': [15, 12, 105, 102]},
        {'class_name': 'person', 'conf': 0.88, 'box': [115, 12, 205, 102]},
        {'class_name': 'car', 'conf': 0.92, 'box': [50, 150, 200, 250]}
    ]

    diff = compute_entity_diff_from_detections(det1, det2)
    print("Entity diff output:", diff)

    assert "person (2)" in diff["shared_objects"]
    assert "person (1)" in diff["only_in_image_1"]
    assert "car (1)" in diff["only_in_image_2"]
    assert len(diff["only_in_image_1"]) == 1
    assert len(diff["only_in_image_2"]) == 1
    print("✓ Class-count set diffing test passed!")

def test_homography_alignment_and_ssim():
    # Create synthetic reference image with patterns
    img1 = np.ones((300, 300, 3), dtype=np.uint8) * 180
    cv2.circle(img1, (150, 150), 40, (50, 50, 200), -1)
    cv2.rectangle(img1, (50, 50), (100, 100), (30, 180, 50), -1)
    cv2.rectangle(img1, (200, 200), (270, 270), (200, 150, 30), -1)

    # Shift Image 2 slightly (translation dx=10, dy=5)
    M = np.float32([[1, 0, 10], [0, 1, 5]])
    img2 = cv2.warpAffine(img1, M, (300, 300))

    orb_data, H_valid, img2_aligned, valid_mask, good, kp1, kp2 = compute_orb_and_alignment(img1, img2)
    aligned_ssim, heatmap = compute_aligned_ssim_and_diff(img1, img2_aligned, valid_mask)

    print(f"ORB inliers: {orb_data['good_inlier_matches']}, Aligned SSIM: {aligned_ssim:.4f}")
    assert aligned_ssim > 0.80, f"Aligned SSIM should be high for minor shift, got {aligned_ssim}"
    assert heatmap.shape == img1.shape
    print("✓ Homography-aligned SSIM test passed!")

def test_framing_shift_rule():
    # Verify diagnostic rule engine categorizes framing / camera shift when resnet >= 0.85 and inliers >= 25
    metrics = {
        "quantitative_metrics": {
            "deep_semantic_cosine": {"resnet50": 0.89},
            "structural_and_pixel": {
                "ssim_score": 0.62,
                "phash_similarity": 0.85,
                "orb_keypoint_matches": {"good_inlier_matches": 35}
            }
        }
    }
    region_scores = {
        "foreground_subject_similarity": 0.91,
        "background_environment_similarity": 0.74,
        "lighting_consistency": 0.86,
        "color_palette_match": 0.95
    }

    forensic = rule_based_forensic_synthesis(metrics, region_scores)
    categories = [d["category"] for d in forensic["what_is_different"]]
    severities = {d["category"]: d["severity"] for d in forensic["what_is_different"]}

    print("Diagnostic What is Different categories:", categories)
    assert "Framing / Camera Shift" in categories
    assert severities["Framing / Camera Shift"] == "LOW"
    assert "Pose / Angle" not in categories, "Should not trigger HIGH Pose / Angle when framing shift matches"
    print("✓ Framing / Camera Shift diagnostic rule test passed!")

if __name__ == "__main__":
    test_class_count_set_diffing()
    test_homography_alignment_and_ssim()
    test_framing_shift_rule()
    print("ALL TESTS PASSED SUCCESSFULLY!")
