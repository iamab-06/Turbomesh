import sys, os, zipfile, shutil

zip_path = 'archive.zip'
extract_dir = 'test_extract'

if os.path.exists(extract_dir):
    shutil.rmtree(extract_dir)
os.makedirs(extract_dir)

with zipfile.ZipFile(zip_path, 'r') as zf:
    zf.extractall(extract_dir)

print("Root items:")
root_items = os.listdir(extract_dir)
for item in root_items:
    print(f"  - {item}")

print("\nChecking for images at root level:")
for item in root_items:
    item_path = os.path.join(extract_dir, item)
    if os.path.isdir(item_path):
        files = os.listdir(item_path)
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"  {item}: {len(image_files)} images, {len(files)} total files")

print("\nChecking one level deeper:")
for item in root_items:
    item_path = os.path.join(extract_dir, item)
    if os.path.isdir(item_path) and not item.startswith('.'):
        sub_items = os.listdir(item_path)
        for sub_item in sub_items:
            sub_path = os.path.join(item_path, sub_item)
            if os.path.isdir(sub_path) and not sub_item.startswith('.'):
                files = os.listdir(sub_path)
                image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if len(files) > 0:
                    print(f"  {item}/{sub_item}: {len(image_files)} images, {len(files)} total")

shutil.rmtree(extract_dir)
