import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import json
import torch
import torchvision
from torchvision.transforms import functional as F
import uuid
from streamlit_drawable_canvas import st_canvas

# === Set Halaman Harus Paling Awal ===
st.set_page_config(page_title="Anotasi Gambar Objek", layout="centered")

# === Konstanta Folder ===
ANNOTATION_DIR = "saved_annotations"
os.makedirs(ANNOTATION_DIR, exist_ok=True)

# === Load Model Deteksi Otomatis (Faster R-CNN COCO) ===
@st.cache_resource
def load_detection_model():
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    model.eval()
    return model

detection_model = load_detection_model()

COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag',
    'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
    'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana',
    'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table',
    'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
    'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

# === Fungsi Deteksi Otomatis (Hanya 1 Objek) ===
def detect_top_object(image):
    image_tensor = F.to_tensor(image).unsqueeze(0)
    with torch.no_grad():
        predictions = detection_model(image_tensor)[0]

    for box, label_idx, score in zip(predictions['boxes'], predictions['labels'], predictions['scores']):
        if score >= 0.5:
            label = COCO_INSTANCE_CATEGORY_NAMES[label_idx] if label_idx < len(COCO_INSTANCE_CATEGORY_NAMES) else str(label_idx)
            return {
                'label': label,
                'box': [int(box[0]), int(box[1]), int(box[2]), int(box[3])],
                'score': float(score)
            }
    return None

# === Streamlit Interface ===
st.title("🖼️ Anotasi Gambar Objek")

uploaded_file = st.file_uploader("📂 Unggah gambar Anda", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="📷 Gambar yang diunggah", use_column_width=True)

    label_input = ''

    if 'detected' not in st.session_state:
        st.session_state.detected = None

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Jalankan Deteksi Otomatis"):
            with st.spinner("🔄 Mendeteksi objek..."):
                st.session_state.detected = detect_top_object(image)

    detected = st.session_state.detected
    if detected:
        image_det = image.copy()
        draw = ImageDraw.Draw(image_det)
        box = detected['box']
        label = label_input or detected['label']

        draw.rectangle(box, outline="blue", width=3)

        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()

        text_position = (box[0] + 4, max(box[1] - 20, 0))
        draw.text(text_position, label, fill="blue", font=font)

        st.image(image_det, caption="📦 Hasil Deteksi Otomatis", use_column_width=True)

        xmin, ymin, xmax, ymax = box
        save_data = {
            "image": uploaded_file.name,
            "label": label,
            "box": [xmin, ymin, xmax, ymax]
        }
        filename = os.path.join(ANNOTATION_DIR, f"annotation_{uuid.uuid4().hex[:8]}.json")
        with open(filename, "w") as f:
            json.dump(save_data, f, indent=2)
        st.success(f"✅ Anotasi otomatis disimpan: {filename}")

    st.subheader("🖌️ Anotasi Manual (gambar kotak)")
    label_input = st.text_input("🏷️ Masukkan label anotasi (otomatis/manual)")
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=2,
        background_image=image,
        update_streamlit=True,
        height=image.height,
        width=image.width,
        drawing_mode="rect",
        key="canvas_main"
    )

    if canvas_result.json_data and len(canvas_result.json_data["objects"]) > 0 and label_input:
        obj = canvas_result.json_data["objects"][-1]
        left = int(obj["left"])
        top = int(obj["top"])
        width = int(obj["width"])
        height = int(obj["height"])
        xmin_manual, ymin_manual = left, top
        xmax_manual, ymax_manual = left + width, top + height

        draw = ImageDraw.Draw(image)
        draw.rectangle([xmin_manual, ymin_manual, xmax_manual, ymax_manual], outline="red", width=2)

        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()
        text_position = (xmin_manual + 4, max(ymin_manual - 20, 0))
        draw.text(text_position, label_input, fill="red", font=font)

        st.image(image, caption="🖍️ Hasil Anotasi Manual", use_column_width=True)

        save_data = {
            "image": uploaded_file.name,
            "label": label_input,
            "box": [xmin_manual, ymin_manual, xmax_manual, ymax_manual]
        }
        filename = os.path.join(ANNOTATION_DIR, f"annotation_{uuid.uuid4().hex[:8]}.json")
        with open(filename, "w") as f:
            json.dump(save_data, f, indent=2)
        st.success(f"✅ Anotasi manual disimpan: {filename}")