"""
Test script for Deep Forensic Image Similarity pipeline
"""
import os
import sys
import json
from pathlib import Path

# Add host to path
sys.path.insert(0, 'host')

from core.deep_similarity import (
    extract_image_metadata,
    compute_ssim,
    compute_phash_similarity,
    compute_color_histogram_correlation,
    compute_orb_matches,
    run_deep_image_similarity,
    get_image_embedding
)

def create_test_images():
    """Create dummy test images if they don't exist"""
    import cv2
    import numpy as np
    
    test_dir = Path("test_images")
    test_dir.mkdir(exist_ok=True)
    
    # Image 1: Blue square with white circle
    img1 = np.zeros((400, 400, 3), dtype=np.uint8)
    img1[:, :] = (200, 100, 50)  # BGR
    cv2.circle(img1, (200, 200), 80, (255, 255, 255), -1)
    cv2.imwrite(str(test_dir / "test_img1.jpg"), img1)
    
    # Image 2: Similar but slightly different (rotated, different lighting)
    img2 = np.zeros((400, 400, 3), dtype=np.uint8)
    img2[:, :] = (180, 90, 40)  # Slightly darker
    cv2.circle(img2, (220, 210), 75, (240, 240, 240), -1)  # Offset circle
    cv2.imwrite(str(test_dir / "test_img2.jpg"), img2)
    
    # Image 3: Completely different
    img3 = np.zeros((400, 400, 3), dtype=np.uint8)
    img3[:, :] = (50, 150, 200)  # Different color
    cv2.rectangle(img3, (100, 100), (300, 300), (0, 255, 0), -1)
    cv2.imwrite(str(test_dir / "test_img3.jpg"), img3)
    
    return [
        str(test_dir / "test_img1.jpg"),
        str(test_dir / "test_img2.jpg"),
        str(test_dir / "test_img3.jpg")
    ]

def test_metadata_extraction():
    """Test metadata extraction"""
    print("\n=== Testing Metadata Extraction ===")
    test_imgs = create_test_images()
    
    meta = extract_image_metadata(test_imgs[0])
    print(f"✓ Filename: {meta['filename']}")
    print(f"✓ Resolution: {meta['resolution']}")
    print(f"✓ Aspect Ratio: {meta['aspect_ratio']}")
    print(f"✓ Dominant Colors: {meta['dominant_colors_hex']}")
    
    assert 'filename' in meta
    assert 'resolution' in meta
    assert 'aspect_ratio' in meta
    assert len(meta['dominant_colors_hex']) == 3
    print("✓ Metadata extraction passed")

def test_quantitative_metrics():
    """Test quantitative similarity metrics"""
    print("\n=== Testing Quantitative Metrics ===")
    test_imgs = create_test_images()
    
    # Test similar images
    print("\n--- Similar Images (1 vs 2) ---")
    ssim_val = compute_ssim(test_imgs[0], test_imgs[1])
    print(f"SSIM: {ssim_val:.4f}")
    
    phash_sim = compute_phash_similarity(test_imgs[0], test_imgs[1])
    print(f"pHash Similarity: {phash_sim:.4f}")
    
    color_corr = compute_color_histogram_correlation(test_imgs[0], test_imgs[1])
    print(f"Color Histogram Correlation: {color_corr:.4f}")
    
    orb_data = compute_orb_matches(test_imgs[0], test_imgs[1])
    print(f"ORB Inlier Matches: {orb_data['good_inlier_matches']}")
    
    # Test dissimilar images
    print("\n--- Dissimilar Images (1 vs 3) ---")
    ssim_val_diff = compute_ssim(test_imgs[0], test_imgs[2])
    print(f"SSIM: {ssim_val_diff:.4f}")
    
    phash_sim_diff = compute_phash_similarity(test_imgs[0], test_imgs[2])
    print(f"pHash Similarity: {phash_sim_diff:.4f}")
    
    # Similar images should have higher scores
    assert ssim_val > ssim_val_diff, "SSIM should be higher for similar images"
    assert phash_sim > phash_sim_diff, "pHash should be higher for similar images"
    
    print("✓ Quantitative metrics passed")

def test_deep_embeddings():
    """Test deep semantic embeddings"""
    print("\n=== Testing Deep Semantic Embeddings ===")
    test_imgs = create_test_images()
    
    import torch.nn as nn
    
    emb1 = get_image_embedding(test_imgs[0])
    emb2 = get_image_embedding(test_imgs[1])
    emb3 = get_image_embedding(test_imgs[2])
    
    cos = nn.CosineSimilarity(dim=0)
    sim_12 = cos(emb1, emb2).item()
    sim_13 = cos(emb1, emb3).item()
    
    print(f"ResNet50 similarity (1 vs 2): {sim_12:.4f}")
    print(f"ResNet50 similarity (1 vs 3): {sim_13:.4f}")
    
    assert emb1.shape[0] == 2048, "ResNet50 should output 2048-dim features"
    print("✓ Deep embeddings passed")

def test_full_pipeline():
    """Test the complete deep similarity pipeline"""
    print("\n=== Testing Full Deep Similarity Pipeline ===")
    test_imgs = create_test_images()
    
    # Create mock job structure
    job = {
        'job_id': 'test_job_001',
        'files': {
            'test_img1.jpg': {'path': test_imgs[0]},
            'test_img2.jpg': {'path': test_imgs[1]}
        }
    }
    
    input_dir = "test_images"
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    print("\nRunning full pipeline...")
    result_files = run_deep_image_similarity(job, input_dir, str(output_dir))
    
    print(f"\n✓ Generated files: {result_files}")
    
    # Verify JSON output
    json_path = output_dir / "deep_similarity.json"
    assert json_path.exists(), "deep_similarity.json should be generated"
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    print("\n--- JSON Structure Validation ---")
    assert data['operation'] == 'deep_image_similarity'
    assert 'verdict' in data
    assert 'quantitative_metrics' in data
    assert 'forensic_breakdown' in data
    assert 'visual_artifacts' in data
    assert 'p2p_telemetry' in data
    
    print(f"✓ Classification: {data['verdict']['classification']}")
    print(f"✓ Overall Similarity: {data['verdict']['overall_similarity_score']:.3f}")
    print(f"✓ Confidence: {data['verdict']['confidence']:.3f}")
    print(f"✓ ResNet50 Similarity: {data['quantitative_metrics']['deep_semantic_cosine']['resnet50']:.4f}")
    print(f"✓ SSIM Score: {data['quantitative_metrics']['structural_and_pixel']['ssim_score']:.4f}")
    print(f"✓ ORB Matches: {data['quantitative_metrics']['structural_and_pixel']['orb_keypoint_matches']['good_inlier_matches']}")
    
    # Verify visual artifacts
    for artifact_file in ['gradcam_pair.png', 'ssim_diff.png', 'orb_matches.png']:
        artifact_path = output_dir / artifact_file
        assert artifact_path.exists(), f"{artifact_file} should be generated"
        print(f"✓ Generated: {artifact_file}")
    
    # Verify telemetry
    telemetry = data['p2p_telemetry']
    assert 'worker_node_id' in telemetry
    assert 'gpu_hardware' in telemetry
    assert 'models_executed' in telemetry
    assert 'latency_breakdown_ms' in telemetry
    assert 'verification_hash' in telemetry
    print(f"✓ Worker Node: {telemetry['worker_node_id']}")
    print(f"✓ GPU Hardware: {telemetry['gpu_hardware']}")
    print(f"✓ Total GPU Time: {telemetry['latency_breakdown_ms']['total_gpu_time']:.1f}ms")
    
    # Pretty print a sample of the forensic breakdown
    print("\n--- Forensic Breakdown Sample ---")
    if data['forensic_breakdown']['what_is_similar']:
        print(f"Similar: {data['forensic_breakdown']['what_is_similar'][0]['category']}")
    if data['forensic_breakdown']['what_is_different']:
        print(f"Different: {data['forensic_breakdown']['what_is_different'][0]['category']}")
    
    print("\n✓ Full pipeline test passed!")
    print(f"\n📊 Results saved to: {output_dir}")
    
    return data

def main():
    """Run all tests"""
    print("="*60)
    print("TurboMesh Deep Forensic Image Similarity - Test Suite")
    print("="*60)
    
    try:
        test_metadata_extraction()
        test_quantitative_metrics()
        test_deep_embeddings()
        result = test_full_pipeline()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
        print("\nYou can now:")
        print("1. Inspect test_output/deep_similarity.json")
        print("2. View generated heatmaps in test_output/")
        print("3. Start the TurboMesh host and test with real images")
        
        return 0
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ TEST FAILED: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
