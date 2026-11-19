import zipfile, io
import numpy as np
import cv2
from PIL import Image
import mediapipe

mp_hands = mediapipe.solutions.hands
z = zipfile.ZipFile('archive.zip')
images = [n for n in z.namelist() if n.endswith('.jpeg')]

detected = 0
failed = 0
for img_path in images[:30]:
    img_data = z.read(img_path)
    image = Image.open(io.BytesIO(img_data)).convert('RGB')
    img_np = np.array(image)
    
    with mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.3) as hands:
        results = hands.process(img_np)
    
    if results.multi_hand_landmarks:
        detected += 1
    else:
        failed += 1
        print(f'FAIL: {img_path.split("/")[-1]} brightness={img_np.mean():.1f}')

print(f'\nDetected: {detected}/30, Failed: {failed}/30')
