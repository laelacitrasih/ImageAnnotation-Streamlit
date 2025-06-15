import streamlit as st
from PIL import Image
import os
import uuid
import json
from streamlit_drawable_canvas import st_canvas

# === Pengaturan Folder & File ===
FOLDER_PENYIMPANAN = "saved"
FILE_ANOTASI = os.path.join(FOLDER_PENYIMPANAN, "anotasi.json")
os.makedirs(FOLDER_PENYIMPANAN, exist_ok=True)

def simpan_anotasi(data):
    if os.path.exists(FILE_ANOTASI):
        with open(FILE_ANOTASI, "r") as f:
            anotasi = json.load(f)
    else:
        anotasi = []
    anotasi.append(data)
    with open(FILE_ANOTASI, "w") as f:
        json.dump(anotasi, f, indent=2)

# === Antarmuka Aplikasi ===
st.title("🖍️ Aplikasi Anotasi Gambar Makanan")

gambar = st.file_uploader("📤 Upload gambar makanan", type=["jpg", "jpeg", "png"])

if gambar:
    img = Image.open(gambar).convert("RGB")
    lebar, tinggi = img.size

    st.image(img, caption="📷 Gambar yang di-upload", use_column_width=True)

    label = st.text_input("🏷️ Masukkan label", "")

    st.markdown("### ➕ Gambar kotak (bounding box) pada gambar:")

    hasil_canvas = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=2,
        background_image=img,
        update_streamlit=True,
        height=tinggi,
        width=lebar,
        drawing_mode="rect",
        key="canvas",
    )

    if st.button("💾 Simpan Anotasi"):
        if label and hasil_canvas.json_data and hasil_canvas.json_data["objects"]:
            for objek in hasil_canvas.json_data["objects"]:
                xmin = objek["left"]
                ymin = objek["top"]
                xmax = xmin + objek["width"]
                ymax = ymin + objek["height"]

                entri = {
                    "id": str(uuid.uuid4()),
                    "nama_file": gambar.name,
                    "label": label,
                    "bbox": [xmin, ymin, xmax, ymax]
                }
                simpan_anotasi(entri)
            st.success("✅ Anotasi berhasil disimpan!")
        else:
            st.warning("Mohon upload gambar, gambar kotak, dan isi label.")

    # Tampilkan anotasi terakhir
    if os.path.exists(FILE_ANOTASI):
        with open(FILE_ANOTASI) as f:
            data = json.load(f)
        st.markdown("### 📦 Anotasi Terakhir")
        for item in data[-3:]:
            st.json(item)
