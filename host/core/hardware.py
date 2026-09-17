import torch

def get_hardware_info():
    if torch.cuda.is_available():
        device = 'cuda'
        backend = 'CUDA'
        gpu_name = torch.cuda.get_device_name(0)
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        device = 'mps'
        backend = 'MPS'
        gpu_name = 'Apple Silicon'
    else:
        device = 'cpu'
        backend = 'CPU'
        gpu_name = 'Not detected'

    return {
        'device': device,
        'backend': backend,
        'gpu': gpu_name
    }

