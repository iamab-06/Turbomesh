#!/usr/bin/env python3
"""
TurboMesh Deep Similarity - Setup Verification Script
Checks that all dependencies and modules are properly installed
"""
import sys

def check_import(module_name, package_name=None):
    """Try to import a module and report status"""
    try:
        __import__(module_name)
        print(f"  ✓ {package_name or module_name}")
        return True
    except ImportError:
        print(f"  ✗ {package_name or module_name} - MISSING")
        return False

def main():
    print("="*60)
    print("TurboMesh Deep Similarity - Setup Verification")
    print("="*60)
    
    all_ok = True
    
    # Check Python version
    print("\n1. Python Version:")
    version = sys.version_info
    print(f"  {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ⚠ Python 3.8+ recommended")
        all_ok = False
    else:
        print("  ✓ Version OK")
    
    # Check core dependencies
    print("\n2. Core Dependencies:")
    deps = [
        ("torch", "PyTorch"),
        ("torchvision", "TorchVision"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("numpy", "NumPy"),
        ("sklearn", "scikit-learn"),
        ("skimage", "scikit-image"),
        ("imagehash", "ImageHash"),
        ("ultralytics", "Ultralytics YOLO"),
    ]
    
    for module, name in deps:
        if not check_import(module, name):
            all_ok = False
    
    # Check GPU availability
    print("\n3. GPU Support:")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  ✓ CUDA available")
            print(f"    GPU: {torch.cuda.get_device_name(0)}")
            print(f"    VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print(f"  ✓ MPS (Apple Silicon) available")
        else:
            print(f"  ⚠ No GPU detected - will use CPU (slower)")
    except Exception as e:
        print(f"  ✗ Error checking GPU: {e}")
        all_ok = False
    
    # Check TurboMesh modules
    print("\n4. TurboMesh Modules:")
    sys.path.insert(0, 'host')
    
    modules = [
        ("core.deep_similarity", "Deep Similarity Pipeline"),
        ("core.processing", "Processing Module"),
        ("core.hardware", "Hardware Detection"),
        ("core.jobs", "Job Manager"),
        ("core.worker", "Worker Module"),
    ]
    
    for module, name in modules:
        if not check_import(module, name):
            all_ok = False
    
    # Check if main functions are accessible
    print("\n5. Pipeline Functions:")
    try:
        from core.deep_similarity import (
            run_deep_image_similarity,
            extract_image_metadata,
            compute_ssim,
            get_image_embedding
        )
        print("  ✓ All core functions accessible")
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        all_ok = False
    
    # Test basic functionality
    print("\n6. Basic Functionality Test:")
    try:
        from core.hardware import get_hardware_info
        hw = get_hardware_info()
        print(f"  ✓ Hardware detection works")
        print(f"    Device: {hw['device']}")
        print(f"    Backend: {hw['backend']}")
    except Exception as e:
        print(f"  ✗ Hardware detection failed: {e}")
        all_ok = False
    
    # Check test files exist
    print("\n7. Test Files:")
    import os
    test_files = [
        "test_deep_similarity.py",
        "test_integration.py",
        "host/core/deep_similarity.py",
    ]
    
    for filepath in test_files:
        if os.path.exists(filepath):
            print(f"  ✓ {filepath}")
        else:
            print(f"  ✗ {filepath} - MISSING")
            all_ok = False
    
    # Summary
    print("\n" + "="*60)
    if all_ok:
        print("✅ SETUP VERIFICATION PASSED")
        print("="*60)
        print("\nYour environment is ready for Deep Similarity!")
        print("\nNext steps:")
        print("  1. Run: python test_deep_similarity.py")
        print("  2. Run: python test_integration.py")
        print("  3. Start TurboMesh: cd host && python main.py")
        return 0
    else:
        print("❌ SETUP VERIFICATION FAILED")
        print("="*60)
        print("\nSome dependencies are missing. Install them with:")
        print("  pip install -r user/requirements/host.txt")
        return 1

if __name__ == '__main__':
    sys.exit(main())
