import streamlit as st
from streamlit_drawable_canvas import st_canvas
from ultralytics import YOLO
import numpy as np
import cv2
from PIL import Image
import os
import uuid

# Load model
model = YOLO("yolov8n.pt")
FEEDBACK_DIR = "feedback_dataset/images"
LABEL_DIR = "feedback_dataset/labels"
LABEL_FILE = "labels.txt"
os.makedirs(FEEDBACK_DIR, exist_ok=True)
os.makedirs(LABEL_DIR, exist_ok=True)

# === Label Handling ===
def load_labels():
    default_labels = []
    if os.path.exists(LABEL_FILE):
        with open(LABEL_FILE, "r") as f:
            labels = [line.strip() for line in f.readlines() if line.strip()]
    else:
        labels = default_labels
    if "Lainnya" not in labels:
        labels = sorted([label for label in labels if label != "Lainnya"])
        labels.append("Lainnya")
    return labels

def add_label_to_file(new_label):
    labels = load_labels()
    if new_label and new_label not in labels:
        with open(LABEL_FILE, "a") as f:
            f.write(f"{new_label}\n")

st.title("🍱 Aplikasi Anotasi dan Deteksi Makanan Indonesia")
mode = st.radio("Pilih mode", ["Deteksi Otomatis (YOLO)", "Anotasi Manual"])

uploaded_file = st.file_uploader("📤 Upload gambar makanan", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(image)
    st.image(image, caption="📷 Gambar yang di-upload", use_column_width=True)

    if mode == "Deteksi Otomatis (YOLO)":
        results = model(image_np)
        boxes = results[0].boxes
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        for box in boxes:
            xmin, ymin, xmax, ymax = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            label = results[0].names[class_id]
            text_y = max(ymin - 10, 20)
            cv2.rectangle(image_cv, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(image_cv, label, (xmin, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        result_img = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
        st.image(result_img, caption="🧠 Hasil Deteksi Otomatis", use_column_width=True)

        st.markdown("### 📝 Koreksi Anotasi")
        if st.checkbox("Apakah hasil anotasi perlu diperbaiki?"):
            if len(boxes) > 0:
                box = boxes[0]
                det_xmin, det_ymin, det_xmax, det_ymax = map(int, box.xyxy[0])
            else:
                det_xmin, det_ymin, det_xmax, det_ymax = 50, 50, 200, 200

            label_options = load_labels()
            selected_label = st.selectbox("Label koreksi", label_options)

            if selected_label == "Lainnya":
                custom_label = st.text_input("Masukkan label baru")
                final_label = custom_label.strip()
                if final_label:
                    add_label_to_file(final_label)
            else:
                final_label = selected_label

            col1, col2 = st.columns(2)
            with col1:
                xmin = st.number_input("xmin", min_value=0, value=det_xmin)
                xmax = st.number_input("xmax", min_value=0, value=det_xmax)
            with col2:
                ymin = st.number_input("ymin", min_value=0, value=det_ymin)
                ymax = st.number_input("ymax", min_value=0, value=det_ymax)

            if st.button("💾 Simpan Koreksi"):
                uid = str(uuid.uuid4())[:8]
                image_path = os.path.join(FEEDBACK_DIR, f"{uid}.jpg")
                label_path = os.path.join(LABEL_DIR, f"{uid}.txt")
                image.save(image_path)

                img_w, img_h = image.size
                x_center = ((xmin + xmax) / 2) / img_w
                y_center = ((ymin + ymax) / 2) / img_h
                box_w = (xmax - xmin) / img_w
                box_h = (ymax - ymin) / img_h

                class_id = 0
                with open(label_path, "w") as f:
                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}\n")

                st.success("✅ Koreksi berhasil disimpan!")

    elif mode == "Anotasi Manual":
        st.markdown("### 🖍️ Gambar Anotasi Manual")
        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",
            stroke_width=2,
            background_image=image,
            update_streamlit=True,
            height=image.height,
            width=image.width,
            drawing_mode="rect",
            key="canvas",
        )

        label = st.selectbox("Label makanan", load_labels())
        if label == "Lainnya":
            label = st.text_input("Masukkan label lain", "")

        if st.button("💾 Simpan Anotasi Manual") and canvas_result.json_data:
            uid = str(uuid.uuid4())[:8]
            image_path = os.path.join(FEEDBACK_DIR, f"{uid}.jpg")
            label_path = os.path.join(LABEL_DIR, f"{uid}.txt")
            image.save(image_path)

            img_w, img_h = image.size
            with open(label_path, "w") as f:
                for obj in canvas_result.json_data["objects"]:
                    xmin = obj["left"]
                    ymin = obj["top"]
                    xmax = xmin + obj["width"]
                    ymax = ymin + obj["height"]

                    x_center = ((xmin + xmax) / 2) / img_w
                    y_center = ((ymin + ymax) / 2) / img_h
                    box_w = (xmax - xmin) / img_w
                    box_h = (ymax - ymin) / img_h

                    f.write(f"0 {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}\n")

            st.success("✅ Anotasi berhasil disimpan.")
