# ImageAnnotation-Streamlit
Light and interactive image annotation app built with Streamlit – draw bounding boxes, label images, and store annotations in JSON format.

# 🍱 ImageAnnotation-Streamlit

Aplikasi anotasi dan klasifikasi gambar berbasis Streamlit, dirancang untuk mendeteksi dan memberi label pada gambar makanan tradisional Indonesia secara otomatis dan manual.

---

## ✨ Fitur Utama

- **Deteksi Otomatis** menggunakan model YOLOv8 (ultralytics)
- **Anotasi Manual** dengan bounding box interaktif
- **Koreksi Label** oleh pengguna (termasuk penambahan label baru)
- Simpan gambar & anotasi dalam format YOLO
- Dukungan upload, preview, dan hasil anotasi

---

## 📁 Struktur Folder

```
ImageAnnotation-Streamlit/
├── app.py
├── requirements.txt
├── labels.txt
├── feedback_dataset/
│   ├── images/
│   └── labels/
├── .streamlit/
│   └── config.toml
└── .gitignore
```

---

## ⚙️ Instalasi & Menjalankan Proyek

### 1. Clone Repo dan Masuk ke Folder
```bash
git clone https://github.com/laelacitrasih/ImageAnnotation-Streamlit.git
cd ImageAnnotation-Streamlit
```

### 2. Buat dan Aktifkan Virtual Environment
```bash
python3 -m venv env
source env/bin/activate  # Mac/Linux
# atau
env\Scripts\activate     # Windows
```

### 3. Install Dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi
```bash
streamlit run app.py
```

---

## 🗂️ Format Anotasi Output (YOLO)

Anotasi disimpan dalam format YOLO:

```
class_id x_center y_center width height
```

Semua nilai bounding box dinormalisasi (0–1) berdasarkan ukuran gambar.

---

## 🧠 Tentang Model

Proyek ini menggunakan model YOLOv8 dari [`ultralytics`](https://github.com/ultralytics/ultralytics).

Secara default, menggunakan model ringan:  
```python
YOLO("yolov8n.pt")
```

> Kamu bisa mengganti model custom `.pt` jika sudah melakukan pelatihan untuk makanan Indonesia.

---

## 📤 Deployment ke Streamlit Cloud

1. Upload semua file ini ke GitHub (repo publik)
2. Buka [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Pilih repo, pastikan file utama: `app.py`
4. Klik **Deploy**

---

## 🙌 Kontribusi & Lisensi

Feel free to fork, edit, and contribute!  
Proyek ini open-source untuk eksplorasi teknologi anotasi dan computer vision sederhana.
