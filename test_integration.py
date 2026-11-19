"""
Integration test for TurboMesh Deep Similarity Pipeline
Tests the full workflow: job creation → file upload → processing → results
"""
import sys
import json
import os
from pathlib import Path

# Add paths
sys.path.insert(0, 'host')

def test_integration():
    """Test the complete integration flow"""
    print("="*70)
    print("TurboMesh Deep Similarity - Integration Test")
    print("="*70)
    
    # 1. Verify core modules can be imported
    print("\n✓ Step 1: Verifying module imports...")
    try:
        from core.deep_similarity import run_deep_image_similarity
        from core.processing import run_image_similarity
        from core.hardware import get_hardware_info
        from core.jobs import job_manager
        print("  ✓ All modules imported successfully")
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False
    
    # 2. Check hardware
    print("\n✓ Step 2: Detecting hardware...")
    hw = get_hardware_info()
    print(f"  Device: {hw['device']}")
    print(f"  Backend: {hw['backend']}")
    print(f"  GPU: {hw['gpu']}")
    
    # 3. Create test images
    print("\n✓ Step 3: Creating test images...")
    import cv2
    import numpy as np
    
    test_dir = Path("integration_test")
    test_dir.mkdir(exist_ok=True)
    
    input_dir = test_dir / "input"
    output_dir = test_dir / "output"
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Create two similar portrait-style images
    img1 = np.zeros((480, 320, 3), dtype=np.uint8)
    img1[:] = (40, 60, 80)  # Dark blue-gray background
    cv2.circle(img1, (160, 200), 60, (220, 180, 150), -1)  # Face
    cv2.circle(img1, (145, 185), 8, (20, 20, 20), -1)  # Left eye
    cv2.circle(img1, (175, 185), 8, (20, 20, 20), -1)  # Right eye
    cv2.ellipse(img1, (160, 210), (20, 10), 0, 0, 180, (200, 100, 100), 2)  # Mouth
    cv2.imwrite(str(input_dir / "portrait1.jpg"), img1)
    
    # Similar but with different pose
    img2 = np.zeros((480, 320, 3), dtype=np.uint8)
    img2[:] = (35, 55, 75)  # Slightly different lighting
    cv2.circle(img2, (170, 210), 58, (215, 175, 145), -1)  # Face shifted
    cv2.circle(img2, (155, 195), 8, (20, 20, 20), -1)  # Left eye
    cv2.circle(img2, (185, 195), 8, (20, 20, 20), -1)  # Right eye
    cv2.ellipse(img2, (170, 220), (20, 10), 0, 0, 180, (200, 100, 100), 2)  # Mouth
    cv2.imwrite(str(input_dir / "portrait2.jpg"), img2)
    
    print(f"  ✓ Created: {input_dir / 'portrait1.jpg'}")
    print(f"  ✓ Created: {input_dir / 'portrait2.jpg'}")
    
    # 4. Create mock job
    print("\n✓ Step 4: Creating mock job...")
    job = {
        'job_id': 'integration_test_001',
        'client_id': 'test_client',
        'operation': 'image_similarity',
        'files': {
            'portrait1.jpg': {'path': str(input_dir / 'portrait1.jpg')},
            'portrait2.jpg': {'path': str(input_dir / 'portrait2.jpg')}
        }
    }
    print(f"  Job ID: {job['job_id']}")
    print(f"  Operation: {job['operation']}")
    print(f"  Files: {list(job['files'].keys())}")
    
    # 5. Run the processing pipeline
    print("\n✓ Step 5: Running deep similarity pipeline...")
    try:
        result_files = run_image_similarity(job, str(input_dir), str(output_dir))
        print(f"  ✓ Pipeline completed successfully")
        print(f"  Generated files: {result_files}")
    except Exception as e:
        print(f"  ✗ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. Verify output files
    print("\n✓ Step 6: Verifying output files...")
    expected_files = [
        'deep_similarity.json',
        'gradcam_pair.png',
        'ssim_diff.png',
        'orb_matches.png'
    ]
    
    for filename in expected_files:
        filepath = output_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"  ✓ {filename} ({size:,} bytes)")
        else:
            print(f"  ✗ Missing: {filename}")
            return False
    
    # 7. Validate JSON structure
    print("\n✓ Step 7: Validating JSON schema...")
    json_path = output_dir / 'deep_similarity.json'
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    required_keys = [
        'job_id',
        'operation',
        'inputs',
        'verdict',
        'quantitative_metrics',
        'forensic_breakdown',
        'region_level_scores',
        'visual_artifacts',
        'p2p_telemetry'
    ]
    
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        print(f"  ✗ Missing keys: {missing_keys}")
        return False
    
    print("  ✓ All required keys present")
    
    # 8. Display key results
    print("\n✓ Step 8: Key results summary...")
    print(f"  Classification: {data['verdict']['classification']}")
    print(f"  Overall Similarity: {data['verdict']['overall_similarity_score']:.1%}")
    print(f"  Confidence: {data['verdict']['confidence']:.1%}")
    print(f"  ResNet50 Similarity: {data['quantitative_metrics']['deep_semantic_cosine']['resnet50']:.4f}")
    print(f"  SSIM Score: {data['quantitative_metrics']['structural_and_pixel']['ssim_score']:.4f}")
    print(f"  ORB Matches: {data['quantitative_metrics']['structural_and_pixel']['orb_keypoint_matches']['good_inlier_matches']}")
    print(f"  GPU Hardware: {data['p2p_telemetry']['gpu_hardware']}")
    print(f"  Total GPU Time: {data['p2p_telemetry']['latency_breakdown_ms']['total_gpu_time']:.1f}ms")
    
    # 9. Test JSON serialization
    print("\n✓ Step 9: Testing JSON serialization...")
    try:
        json_str = json.dumps(data, indent=2)
        print(f"  ✓ JSON is valid and serializable ({len(json_str):,} characters)")
    except Exception as e:
        print(f"  ✗ JSON serialization failed: {e}")
        return False
    
    # 10. Verify forensic breakdown structure
    print("\n✓ Step 10: Verifying forensic breakdown...")
    fb = data['forensic_breakdown']
    print(f"  Similar items: {len(fb['what_is_similar'])}")
    print(f"  Different items: {len(fb['what_is_different'])}")
    print(f"  Shared objects: {fb['detected_entities_comparison']['shared_objects']}")
    
    if fb['what_is_similar']:
        print(f"  Example similarity: {fb['what_is_similar'][0]['category']} ({fb['what_is_similar'][0]['confidence']:.0%})")
    
    if fb['what_is_different']:
        print(f"  Example difference: {fb['what_is_different'][0]['category']} ({fb['what_is_different'][0]['severity']})")
    
    # 11. Test file serving paths
    print("\n✓ Step 11: Verifying file serving paths...")
    for artifact_name, artifact_path in data['visual_artifacts'].items():
        print(f"  {artifact_name}: {artifact_path}")
        # Path should match pattern /outputs/{job_id}/{filename}
        expected_pattern = f"/outputs/{job['job_id']}/"
        if expected_pattern in artifact_path:
            print(f"    ✓ Path format correct")
        else:
            print(f"    ⚠ Path format unexpected (not critical)")
    
    # 12. Performance check
    print("\n✓ Step 12: Performance analysis...")
    total_time = data['p2p_telemetry']['latency_breakdown_ms']['total_gpu_time']
    cv_time = data['p2p_telemetry']['latency_breakdown_ms']['math_and_cv_metrics']
    vlm_time = data['p2p_telemetry']['latency_breakdown_ms']['vlm_forensic_reasoning']
    
    print(f"  Total GPU Time: {total_time:.1f}ms")
    print(f"  CV Metrics: {cv_time:.1f}ms ({cv_time/total_time*100:.1f}%)")
    print(f"  VLM Reasoning: {vlm_time:.1f}ms ({vlm_time/total_time*100:.1f}%)")
    print(f"  Speedup vs CPU: {data['p2p_telemetry']['speedup_vs_local_cpu']}")
    
    if total_time < 10000:  # Under 10 seconds is good
        print("  ✓ Performance is acceptable")
    else:
        print("  ⚠ Performance is slow (consider optimizing)")
    
    # Summary
    print("\n" + "="*70)
    print("✅ INTEGRATION TEST PASSED")
    print("="*70)
    print(f"\nResults saved to: {output_dir}")
    print("\nNext steps:")
    print("1. Start TurboMesh host: cd host && python main.py")
    print("2. Start TurboMesh user: cd user && python main.py")
    print("3. Upload two images via the web UI")
    print("4. View the rich forensic analysis results")
    
    return True

if __name__ == '__main__':
    try:
        success = test_integration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
