import os
import json
import torch
import cv2
import numpy as np
from ultralytics import YOLO
import imagehash
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import torchvision.models as models
import torchvision.transforms as transforms
import torch.nn as nn
from core.hardware import get_hardware_info
from core.hand_sign_training import run_hand_sign_recognition

hw = get_hardware_info()
DEVICE = hw['device']

def run_object_detection(job, input_dir, output_dir):
    files = list(job['files'].keys())
    if len(files) != 1:
        raise Exception('Object Detection requires exactly 1 image')
        
    img_path = os.path.join(input_dir, files[0])
    
    model = YOLO('yolov8n.pt')
    results = model(img_path, device=DEVICE)
    result = results[0]
    
    boxes = result.boxes
    classes = result.names
    
    obj_counts = {}
    vehicle_counts = {}
    vehicle_classes = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']
    
    img = cv2.imread(img_path)
    if img is None: raise Exception('Invalid image')
    out_img = img.copy()
    
    vehicles_list = []
    for box in boxes:
        cls_id = int(box.cls[0].item())
        conf = float(box.conf[0].item())
        cls_name = classes[cls_id]
        
        obj_counts[cls_name] = obj_counts.get(cls_name, 0) + 1
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        
        estimated_color = 'unknown'
        if cls_name in vehicle_classes:
            vehicle_counts[cls_name] = vehicle_counts.get(cls_name, 0) + 1
            h, w = y2 - y1, x2 - x1
            if h > 10 and w > 10:
                crop = img[y1+h//4:y2-h//4, x1+w//4:x2-w//4]
                if crop.size > 0:
                    avg_color = np.average(np.average(crop, axis=0), axis=0)
                    b, g, r = avg_color
                    if r > 150 and g < 100 and b < 100: estimated_color = 'red'
                    elif b > 150 and g < 100 and r < 100: estimated_color = 'blue'
                    elif g > 150 and r < 100 and b < 100: estimated_color = 'green'
                    elif r > 150 and g > 150 and b < 100: estimated_color = 'yellow'
                    elif r < 50 and g < 50 and b < 50: estimated_color = 'black'
                    elif r > 200 and g > 200 and b > 200: estimated_color = 'white'
                    elif abs(r-g) < 20 and abs(g-b) < 20 and abs(r-b) < 20:
                        estimated_color = 'gray' if r < 180 else 'silver'
                    else: estimated_color = 'other'
            
            vehicles_list.append({'class': cls_name, 'confidence': round(conf, 2), 'estimated_color': estimated_color, 'license_plate_detected': False, 'license_plate_blurred': False})
            
            # Heuristic blur for plates
            bh, bw = int((y2 - y1) * 0.2), int((x2 - x1) * 0.4)
            bx1, by1 = x1 + int((x2 - x1) * 0.3), y2 - bh - int((y2 - y1) * 0.05)
            bx2, by2 = bx1 + bw, by1 + bh
            if bx2 <= out_img.shape[1] and by2 <= out_img.shape[0] and bx1 >= 0 and by1 >= 0:
                plate_roi = out_img[by1:by2, bx1:bx2]
                if plate_roi.size > 0:
                    blurred = cv2.GaussianBlur(plate_roi, (51, 51), 0)
                    out_img[by1:by2, bx1:bx2] = blurred
                    vehicles_list[-1]['license_plate_detected'] = True
                    vehicles_list[-1]['license_plate_blurred'] = True
                    cv2.rectangle(out_img, (bx1, by1), (bx2, by2), (0, 0, 0), 2)
        
        cv2.rectangle(out_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(out_img, f'{cls_name} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    cv2.imwrite(os.path.join(output_dir, 'annotated_image.jpg'), out_img)
    
    analytics = {'operation': 'object_detection', 'processing_device': DEVICE, 'object_counts': obj_counts, 'vehicle_counts': vehicle_counts, 'total_vehicles': sum(vehicle_counts.values()), 'vehicles': vehicles_list, 'license_plates_detected': sum(1 for v in vehicles_list if v['license_plate_detected'])}
    with open(os.path.join(output_dir, 'analytics.json'), 'w') as f: json.dump(analytics, f, indent=4)
    return ['annotated_image.jpg', 'analytics.json']

resnet_model = None

def get_resnet_model():
    global resnet_model
    if resnet_model is None:
        resnet_model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        resnet_model = nn.Sequential(*list(resnet_model.children())[:-1])
        resnet_model.to(DEVICE)
        resnet_model.eval()
    return resnet_model

def get_image_embedding(img_path):
    model = get_resnet_model()
    transform = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    img = Image.open(img_path).convert('RGB')
    tensor = transform(img).unsqueeze(0).to(DEVICE)
    with torch.no_grad(): emb = model(tensor).squeeze()
    return emb

def run_image_similarity(job, input_dir, output_dir):
    """Route to deep forensic image similarity pipeline"""
    from core.deep_similarity import run_deep_image_similarity
    return run_deep_image_similarity(job, input_dir, output_dir)


def run_hand_sign_detection(job, input_dir, output_dir):
    """Placeholder for hand sign detection - returns metadata for model inference"""
    files = list(job['files'].keys())
    if len(files) != 1:
        raise Exception('Hand Sign Detection requires exactly 1 image')
    
    img_path = os.path.join(input_dir, files[0])
    
    # For now, return basic image info and metadata
    # The actual model inference happens on the User client
    img = Image.open(img_path)
    result = {
        'operation': 'hand_sign_detection',
        'image': files[0],
        'image_size': img.size,
        'processing_device': DEVICE,
        'status': 'Image received and ready for inference on client'
    }
    
    with open(os.path.join(output_dir, 'detection_result.json'), 'w') as f:
        json.dump(result, f, indent=4)
    
    return ['detection_result.json']
