import os
import json
import time
import math
import hashlib
import numpy as np
import cv2
import torch
import torch.nn as nn
from PIL import Image

from core.hardware import get_hardware_info

hw = get_hardware_info()
DEVICE = hw['device']

# Style presets and color schemes
PALETTES = {
    'cyberpunk': {
        'bg': [(10, 5, 25), (20, 10, 45), (5, 15, 35)],
        'primary': (0, 240, 255),       # Neon Cyan (BGR)
        'secondary': (255, 0, 180),     # Hot Magenta (BGR)
        'accent': (20, 255, 160),       # Neon Lime (BGR)
        'glow': (255, 100, 220)
    },
    'synthwave': {
        'bg': [(15, 5, 30), (35, 10, 60), (10, 5, 20)],
        'primary': (240, 50, 255),      # Purple-Pink (BGR)
        'secondary': (50, 210, 255),    # Cyan (BGR)
        'accent': (50, 140, 255),       # Neon Orange (BGR)
        'glow': (200, 80, 255)
    },
    'space': {
        'bg': [(5, 5, 15), (15, 10, 30), (5, 15, 25)],
        'primary': (255, 200, 100),     # Star Gold/Cyan
        'secondary': (220, 80, 200),    # Nebula Violet
        'accent': (100, 240, 255),      # Azure Glow
        'glow': (255, 220, 180)
    },
    'sunset': {
        'bg': [(20, 15, 45), (40, 25, 75), (15, 35, 80)],
        'primary': (40, 120, 255),      # Sunset Orange
        'secondary': (80, 40, 220),     # Crimson Red
        'accent': (50, 220, 255),       # Gold
        'glow': (100, 180, 255)
    },
    'nature': {
        'bg': [(15, 30, 20), (25, 50, 30), (20, 40, 25)],
        'primary': (50, 180, 80),       # Emerald Green
        'secondary': (80, 220, 140),    # Mint Foliage
        'accent': (30, 160, 240),       # Warm Sunlit Gold
        'glow': (100, 230, 180)
    },
    'ocean': {
        'bg': [(30, 20, 5), (60, 40, 10), (45, 30, 5)],
        'primary': (240, 160, 30),      # Deep Cyan / Teal
        'secondary': (220, 220, 80),    # Aquamarine
        'accent': (255, 240, 200),      # White Foam
        'glow': (220, 180, 80)
    },
    'fantasy': {
        'bg': [(25, 15, 35), (45, 25, 60), (30, 10, 40)],
        'primary': (255, 120, 200),     # Mystic Amethyst
        'secondary': (80, 230, 255),    # Ethereal Azure
        'accent': (100, 255, 180),      # Magic Jade
        'glow': (220, 160, 255)
    },
    'cinematic': {
        'bg': [(15, 18, 22), (28, 32, 40), (20, 22, 28)],
        'primary': (200, 210, 225),     # Cool Steel
        'secondary': (60, 140, 210),    # Tungsten Amber
        'accent': (180, 160, 130),      # Titanium
        'glow': (140, 170, 210)
    },
    'monochrome': {
        'bg': [(15, 15, 15), (30, 30, 30), (20, 20, 20)],
        'primary': (220, 220, 220),     # Silver
        'secondary': (140, 140, 140),   # Steel
        'accent': (255, 255, 255),      # Highlight
        'glow': (180, 180, 180)
    }
}


def parse_prompt(prompt: str, user_style: str = None):
    """Analyze prompt to determine themes, subjects, styles, and palette."""
    text = prompt.lower()
    
    # Check style override or detect in prompt
    style = 'cinematic'
    if user_style and user_style in PALETTES:
        style = user_style
    else:
        for key in PALETTES:
            if key in text:
                style = key
                break
        if 'neon' in text or 'cyber' in text or 'futuristic' in text or 'tokyo' in text:
            style = 'cyberpunk'
        elif 'space' in text or 'galaxy' in text or 'star' in text or 'nebula' in text or 'planet' in text:
            style = 'space'
        elif 'sunset' in text or 'sunrise' in text or 'dusk' in text or 'dawn' in text:
            style = 'sunset'
        elif 'ocean' in text or 'sea' in text or 'water' in text or 'beach' in text or 'underwater' in text:
            style = 'ocean'
        elif 'forest' in text or 'nature' in text or 'tree' in text or 'mountain' in text or 'landscape' in text:
            style = 'nature'
        elif 'magic' in text or 'fantasy' in text or 'dragon' in text or 'castle' in text or 'glowing' in text:
            style = 'fantasy'
        elif 'retro' in text or 'wave' in text or '80s' in text:
            style = 'synthwave'
        elif 'black and white' in text or 'monochrome' in text or 'noir' in text or 'pencil' in text:
            style = 'monochrome'

    # Detect subject elements
    subjects = []
    if any(w in text for w in ['mountain', 'mountains', 'hill', 'peak', 'alps']):
        subjects.append('mountains')
    if any(w in text for w in ['city', 'skyline', 'building', 'skyscraper', 'metropolis', 'tower']):
        subjects.append('city')
    if any(w in text for w in ['planet', 'moon', 'sun', 'orb', 'sphere', 'celestial']):
        subjects.append('celestial')
    if any(w in text for w in ['ocean', 'sea', 'water', 'lake', 'river', 'waves']):
        subjects.append('water')
    if any(w in text for w in ['car', 'vehicle', 'robot', 'ship', 'spaceship', 'aircraft']):
        subjects.append('vehicle')
    if any(w in text for w in ['forest', 'trees', 'jungle', 'plants']):
        subjects.append('foliage')
    if any(w in text for w in ['stars', 'galaxy', 'nebula', 'cosmic']):
        subjects.append('stars')
    if any(w in text for w in ['grid', 'matrix', 'wireframe', 'cyber']):
        subjects.append('grid')

    # If no specific subject detected, default according to style
    if not subjects:
        if style in ['cyberpunk', 'synthwave']:
            subjects = ['city', 'grid', 'celestial']
        elif style == 'space':
            subjects = ['stars', 'celestial', 'nebula']
        elif style in ['nature', 'sunset']:
            subjects = ['mountains', 'celestial', 'water']
        elif style == 'ocean':
            subjects = ['water', 'celestial']
        else:
            subjects = ['mountains', 'celestial', 'stars']

    return {
        'style': style,
        'palette': PALETTES.get(style, PALETTES['cinematic']),
        'subjects': subjects,
        'is_neon': style in ['cyberpunk', 'synthwave'] or 'neon' in text,
        'has_sun_or_moon': 'celestial' in subjects or 'sun' in text or 'moon' in text or 'sunset' in text,
        'has_horizon': any(s in subjects for s in ['mountains', 'city', 'water'])
    }


class NeuralLatentField(nn.Module):
    """Implicit Neural Representation (INR) network mapping spatial coords + latent code to neural imagery."""
    def __init__(self, latent_dim=32, hidden_dim=64, num_frequencies=6):
        super().__init__()
        self.num_frequencies = num_frequencies
        in_dim = 2 * (2 * num_frequencies) + latent_dim
        
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(hidden_dim, 3),
            nn.Sigmoid()
        )

    def forward(self, coords, latent):
        # coords: (N, 2) in [-1, 1]
        # Fourier positional encoding
        b, _ = coords.shape
        freq_bands = 2.0 ** torch.linspace(0, self.num_frequencies - 1, self.num_frequencies, device=coords.device)
        encodings = []
        for freq in freq_bands:
            encodings.append(torch.sin(coords * math.pi * freq))
            encodings.append(torch.cos(coords * math.pi * freq))
        fourier_feats = torch.cat(encodings, dim=-1) # (N, 2 * 2 * num_frequencies)
        
        # Expand latent vector across coordinates
        latent_expanded = latent.unsqueeze(0).expand(b, -1)
        x = torch.cat([fourier_feats, latent_expanded], dim=-1)
        return self.net(x)


def generate_image_tensor(prompt: str, width: int = 512, height: int = 512, seed: int = None, style_override: str = None):
    """Synthesize high-quality prompt-conditioned image using PyTorch neural latent field & semantic layers."""
    start_time = time.time()
    
    # Determine seed from prompt if not specified
    if seed is None or seed < 0:
        hash_val = int(hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:8], 16)
        seed = hash_val % (2**31 - 1)
        
    torch.manual_seed(seed)
    np.random.seed(seed % (2**32))
    
    analysis = parse_prompt(prompt, style_override)
    palette = analysis['palette']
    style = analysis['style']
    subjects = analysis['subjects']
    
    # 1. Build PyTorch Coordinate Grid
    target_device = torch.device(DEVICE if torch.cuda.is_available() else 'cpu')
    y_coords = torch.linspace(-1.0, 1.0, height, device=target_device)
    x_coords = torch.linspace(-1.0, 1.0, width, device=target_device)
    grid_y, grid_x = torch.meshgrid(y_coords, x_coords, indexing='ij')
    coords = torch.stack([grid_x.flatten(), grid_y.flatten()], dim=-1) # (H*W, 2)
    
    # 2. Derive prompt semantic latent vector
    latent_dim = 32
    # Seeded pseudo-random normal projection conditioned on prompt tokens
    token_sum = sum(ord(c) for c in prompt) + seed
    generator = torch.Generator(device=target_device)
    generator.manual_seed(token_sum % (2**31 - 1))
    latent = torch.randn(latent_dim, device=target_device, generator=generator)
    
    # 3. Neural Latent Field synthesis
    neural_model = NeuralLatentField(latent_dim=latent_dim, hidden_dim=64, num_frequencies=5).to(target_device)
    # Initialize weights deterministically from seed
    for p in neural_model.parameters():
        if p.dim() > 1:
            nn.init.xavier_uniform_(p, gain=0.8)
            
    with torch.no_grad():
        neural_rgb = neural_model(coords, latent).view(height, width, 3).cpu().numpy()
        
    # Scale neural output to base BGR image
    neural_bgr = (neural_rgb * 255.0).astype(np.uint8)
    
    # 4. Synthesize Semantic Composition Layers (OpenCV / NumPy artistic pipeline)
    img = np.zeros((height, width, 3), dtype=np.float32)
    
    # Base Atmospheric Sky / Background Gradient
    bg_colors = palette['bg']
    c_top = np.array(bg_colors[0], dtype=np.float32)
    c_mid = np.array(bg_colors[1], dtype=np.float32)
    c_bot = np.array(bg_colors[2], dtype=np.float32)
    
    horizon_y = int(height * 0.58)
    for y in range(height):
        if y < horizon_y:
            t = y / max(1, horizon_y)
            color = (1.0 - t) * c_top + t * c_mid
        else:
            t = (y - horizon_y) / max(1, height - horizon_y)
            color = (1.0 - t) * c_mid + t * c_bot
        img[y, :] = color

    # Star / Nebula field
    if 'stars' in subjects or style in ['space', 'cyberpunk', 'synthwave', 'fantasy']:
        num_stars = int(width * height * 0.0006)
        star_xs = np.random.randint(0, width, num_stars)
        star_ys = np.random.randint(0, int(height * 0.65), num_stars)
        star_radii = np.random.choice([1, 1, 2], size=num_stars, p=[0.75, 0.20, 0.05])
        star_glows = np.random.uniform(150, 255, num_stars)
        
        for sx, sy, sr, sg in zip(star_xs, star_ys, star_radii, star_glows):
            col = tuple(float(sg * c / 255.0) for c in palette['accent'])
            cv2.circle(img, (int(sx), int(sy)), int(sr), col, -1)
            
        # Cosmic nebula cloud haze
        nebula_mask = cv2.resize(np.random.normal(0.5, 0.2, (16, 16)).astype(np.float32), (width, height))
        nebula_mask = cv2.GaussianBlur(nebula_mask, (101, 101), 0)
        nebula_col = np.array(palette['secondary'], dtype=np.float32)
        img += np.clip(nebula_mask[:, :, None] * nebula_col * 0.45, 0, 180)

    # Celestial Body (Sun, Moon, Glowing Orb, or Planet)
    if analysis['has_sun_or_moon']:
        cx = int(width * 0.50 if style == 'synthwave' else width * (0.35 + 0.3 * (seed % 100) / 100.0))
        cy = int(horizon_y - height * 0.18)
        radius = int(min(width, height) * 0.14)
        
        # Volumetric Sun / Moon / Orb Gradient
        celestial_overlay = np.zeros((height, width, 3), dtype=np.float32)
        c_glow = np.array(palette['glow'], dtype=np.float32)
        c_core = np.array(palette['primary'], dtype=np.float32)
        
        glow_color = tuple(float(v) for v in (c_glow * 0.25))
        cv2.circle(celestial_overlay, (cx, cy), radius * 3, glow_color, -1)
        celestial_overlay = cv2.GaussianBlur(celestial_overlay, (151, 151), 0)
        
        # Inner Disc
        disc_mask = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(disc_mask, (cx, cy), radius, 255, -1)
        
        # Synthwave horizontal sun blinds if synthwave style
        if style == 'synthwave':
            for line_y in range(cy, cy + radius + 10, 6):
                th = int(2 + (line_y - cy) / 10)
                disc_mask[max(0, line_y - th):min(height, line_y + th), :] = 0
                
        disc_bgr = np.zeros((height, width, 3), dtype=np.float32)
        for y in range(max(0, cy - radius), min(height, cy + radius)):
            t = (y - (cy - radius)) / max(1, 2 * radius)
            disc_bgr[y, :] = (1.0 - t) * c_glow + t * c_core
            
        img = np.where(disc_mask[:, :, None] > 0, disc_bgr, img + celestial_overlay)

    # Mountains / Terrain Silhouette Layer
    if 'mountains' in subjects or style in ['nature', 'sunset', 'fantasy']:
        num_layers = 3
        for layer_idx in range(num_layers):
            layer_t = (layer_idx + 1) / num_layers
            layer_col = [float(v) for v in ((1.0 - layer_t) * np.array(palette['bg'][1]) + layer_t * np.array(palette['bg'][2]) * 0.7)]
            
            base_y = int(horizon_y - (num_layers - layer_idx) * height * 0.08)
            freq = 0.008 * (layer_idx + 1)
            pts = []
            for x in range(0, width + 10, 8):
                noise = math.sin(x * freq + seed) * 35.0 + math.cos(x * freq * 2.3 + layer_idx) * 20.0
                pts.append([x, int(base_y + noise)])
            pts.append([width, height])
            pts.append([0, height])
            pts_arr = np.array(pts, dtype=np.int32)
            cv2.fillPoly(img, [pts_arr], tuple(layer_col))

    # Cityscape / Cyberpunk Skyline Silhouette
    if 'city' in subjects or style == 'cyberpunk':
        building_color = (12.0, 10.0, 20.0)
        num_buildings = int(width / 24)
        np.random.seed(seed + 42)
        
        curr_x = 0
        while curr_x < width:
            b_width = np.random.randint(18, 48)
            b_height = np.random.randint(int(height * 0.20), int(height * 0.52))
            top_y = horizon_y - b_height
            
            # Draw building block
            cv2.rectangle(img, (curr_x, top_y), (curr_x + b_width, horizon_y), building_color, -1)
            
            # Neon window lights
            if analysis['is_neon']:
                neon_col = palette['primary'] if np.random.rand() > 0.4 else palette['secondary']
                for wy in range(top_y + 8, horizon_y - 6, 12):
                    for wx in range(curr_x + 4, curr_x + b_width - 4, 8):
                        if np.random.rand() > 0.45:
                            cv2.rectangle(img, (wx, wy), (wx + 3, wy + 5), tuple(float(c) for c in neon_col), -1)
                            
            # Antenna / Spire on taller towers
            if b_height > height * 0.38 and np.random.rand() > 0.5:
                spire_x = curr_x + b_width // 2
                spire_h = np.random.randint(15, 45)
                cv2.line(img, (spire_x, top_y), (spire_x, top_y - spire_h), (80, 80, 95), 2)
                beacon_col = tuple(float(c) for c in palette['secondary'])
                cv2.circle(img, (spire_x, top_y - spire_h), 2, beacon_col, -1)
                
            curr_x += b_width - np.random.randint(1, 6)

    # Water / Perspective Grid Floor
    if 'water' in subjects or 'ocean' in subjects or style == 'ocean':
        water_base = np.array(palette['primary'], dtype=np.float32) * 0.4
        for y in range(horizon_y, height):
            t = (y - horizon_y) / max(1, height - horizon_y)
            # Perspective water reflection
            ripple = math.sin(y * 0.25 + seed) * 12.0
            water_col = (1.0 - t * 0.5) * water_base + np.array(palette['bg'][2]) * (t * 0.5)
            img[y, :] = water_col + ripple * 0.5
            
            # Specular light streak
            if analysis['has_sun_or_moon']:
                streak_w = int(width * 0.12 * (1.0 + t * 2.5))
                cx = width // 2
                x1 = max(0, cx - streak_w)
                x2 = min(width, cx + streak_w)
                specular_col = np.array(palette['accent'], dtype=np.float32) * (1.0 - t * 0.6) * 0.5
                img[y, x1:x2] += specular_col
                
    elif 'grid' in subjects or style in ['synthwave', 'cyberpunk']:
        # Perspective Grid
        grid_color = tuple(float(c) for c in palette['secondary'])
        # Horizontal lines with exponential perspective spacing
        curr_y = float(horizon_y)
        step = 4.0
        while curr_y < height:
            y_int = int(curr_y)
            cv2.line(img, (0, y_int), (width, y_int), grid_color, 1)
            step *= 1.18
            curr_y += step
            
        # Converging perspective lines to vanishing point
        vanish_x, vanish_y = width // 2, horizon_y
        for x in range(-width // 2, width + width // 2, 40):
            cv2.line(img, (vanish_x, vanish_y), (x, height), grid_color, 1)

    # 5. Blend Neural Latent Texture Field for deep organic coherence
    neural_blend_weight = 0.28
    img = np.clip(img * (1.0 - neural_blend_weight) + neural_bgr.astype(np.float32) * neural_blend_weight, 0, 255)

    # 6. Post-processing & Stylization
    # High-intensity Bloom / Glow for Neon elements
    if analysis['is_neon'] or style in ['cyberpunk', 'synthwave', 'space', 'fantasy']:
        bright_mask = np.clip(img - 180.0, 0, 255)
        glow = cv2.GaussianBlur(bright_mask, (41, 41), 0)
        img = np.clip(img + glow * 0.65, 0, 255)

    # Vignette effect
    y_vignette = np.cos(np.linspace(-np.pi/2.5, np.pi/2.5, height))
    x_vignette = np.cos(np.linspace(-np.pi/2.5, np.pi/2.5, width))
    vignette = np.outer(y_vignette, x_vignette)
    vignette = np.clip(vignette, 0.45, 1.0)[:, :, None]
    img = np.clip(img * vignette, 0, 255)

    # Convert to 8-bit image
    final_bgr = img.astype(np.uint8)
    
    # Artistic color grade contrast
    final_bgr = cv2.convertScaleAbs(final_bgr, alpha=1.12, beta=4)

    duration = round(time.time() - start_time, 3)
    
    metadata = {
        'operation': 'image_generation',
        'prompt': prompt,
        'style': style,
        'detected_subjects': subjects,
        'seed': seed,
        'width': width,
        'height': height,
        'device': DEVICE,
        'generator': 'TurboMesh Neural Art Synthesizer (PyTorch + CUDA)',
        'generation_time_seconds': duration,
        'timestamp': int(time.time())
    }
    
    return final_bgr, metadata


_sd_pipelines = {}

def get_stable_diffusion_pipeline(model_id: str = "stabilityai/sd-turbo", device: str = None):
    """Load and cache a Diffusers Stable Diffusion pipeline on GPU or CPU."""
    global _sd_pipelines
    if device is None:
        device = DEVICE if torch.cuda.is_available() else 'cpu'

    if model_id in _sd_pipelines:
        return _sd_pipelines[model_id]

    from diffusers import AutoPipelineForText2Image
    
    use_cuda = (device == 'cuda' and torch.cuda.is_available())
    torch_dtype = torch.float16 if use_cuda else torch.float32

    try:
        pipe = AutoPipelineForText2Image.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            variant="fp16" if use_cuda else None
        )
    except Exception:
        pipe = AutoPipelineForText2Image.from_pretrained(
            model_id,
            torch_dtype=torch_dtype
        )

    pipe = pipe.to(device)
    if use_cuda:
        try:
            pipe.enable_attention_slicing()
        except Exception:
            pass

    _sd_pipelines[model_id] = pipe
    return pipe


def generate_with_stable_diffusion(prompt: str, model_id: str = "stabilityai/sd-turbo", width: int = 512, height: int = 512, seed: int = None, steps: int = None, guidance_scale: float = None, style: str = None):
    """Generate high-fidelity photorealistic imagery using Stable Diffusion pipelines."""
    device = DEVICE if torch.cuda.is_available() else 'cpu'
    pipe = get_stable_diffusion_pipeline(model_id=model_id, device=device)

    generator = None
    if seed is not None and seed >= 0:
        generator = torch.Generator(device=device).manual_seed(int(seed))

    is_turbo = 'turbo' in model_id.lower()
    if steps is None or steps <= 0:
        steps = 2 if is_turbo else 20
    if guidance_scale is None:
        guidance_scale = 0.0 if is_turbo else 7.5

    start_time = time.time()
    result = pipe(
        prompt=prompt,
        width=width,
        height=height,
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        generator=generator
    )
    duration = round(time.time() - start_time, 3)

    pil_img = result.images[0]
    image_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    metadata = {
        'operation': 'image_generation',
        'prompt': prompt,
        'style': style or 'photorealistic',
        'engine': 'stable-diffusion',
        'model_id': model_id,
        'generator': f'Stable Diffusion ({model_id})',
        'steps': steps,
        'guidance_scale': guidance_scale,
        'seed': seed,
        'width': width,
        'height': height,
        'device': device,
        'generation_time_seconds': duration,
        'timestamp': int(time.time())
    }
    return image_bgr, metadata


def run_image_generation(job, input_dir, output_dir):
    """Host worker execution for image generation job."""
    prompt = job.get('prompt') or ''
    if not prompt.strip():
        # Fallback if no prompt provided
        prompt = 'Futuristic cybernetic city with glowing neon lights and starry sky'
        
    params = job.get('params') or {}
    engine = params.get('engine', 'stable-diffusion')
    model_id = params.get('model_id') or 'stabilityai/sd-turbo'
    width = int(params.get('width', 512))
    height = int(params.get('height', 512))
    seed = params.get('seed')
    if seed is not None:
        try:
            seed = int(seed)
        except (ValueError, TypeError):
            seed = None
            
    style = params.get('style')
    steps = params.get('steps')
    guidance_scale = params.get('guidance_scale')

    image_bgr = None
    metadata = None

    # Check if Stable Diffusion engine is chosen
    if engine in ['stable-diffusion', 'sd', 'sd-turbo']:
        try:
            image_bgr, metadata = generate_with_stable_diffusion(
                prompt=prompt,
                model_id=model_id,
                width=width,
                height=height,
                seed=seed,
                steps=int(steps) if steps else None,
                guidance_scale=float(guidance_scale) if guidance_scale else None,
                style=style
            )
        except Exception as e:
            print(f"Notice: Stable Diffusion ({model_id}) download or execution failed ({e}), falling back to built-in neural art synthesizer...")
            image_bgr, metadata = generate_image_tensor(
                prompt=prompt,
                width=width,
                height=height,
                seed=seed,
                style_override=style
            )
            metadata['fallback_reason'] = f"Stable Diffusion note: {str(e)[:120]}"
    else:
        # Built-in instant local neural synthesizer
        image_bgr, metadata = generate_image_tensor(
            prompt=prompt,
            width=width,
            height=height,
            seed=seed,
            style_override=style
        )

    # Save output artifacts
    out_img_path = os.path.join(output_dir, 'generated_image.png')
    cv2.imwrite(out_img_path, image_bgr)

    out_meta_path = os.path.join(output_dir, 'generation_metadata.json')
    with open(out_meta_path, 'w') as f:
        json.dump(metadata, f, indent=4)

    return ['generated_image.png', 'generation_metadata.json']
