
# 🔎 Hardcore OSINT Image Analyzer

> 🕵️ A powerful **image OSINT tool** that extracts metadata, GPS, hidden text, possible usernames,  
> and performs **reverse image search** automatically.  
> Designed for ethical hacking, digital forensics & cyber investigation.  

---

## 🚀 Features
- 📸 Extracts **EXIF Metadata** (Camera, Model, Date, Software, etc.)
- 🌍 Detects **GPS Location** & auto-generates a **Google Maps link**
- 🔍 Performs **OCR (Text Extraction)** from images
- 👤 Finds **Usernames/Handles** hidden in images or metadata
- 🌐 Launches **Reverse Image Search** on:
  - Google Images  
  - Yandex  
  - Bing  
  - TinEye  
- 🛡 Error-handling & **animated hacker-style output**
- ✅ Supports multiple formats: `.jpg`, `.jpeg`, `.png`, `.webp`, etc.

---

## 📦 Installation

### 1. Clone the Repo
```bash
git clone https://github.com/your-username/photo-osint.git
cd photo-osint
pip install -r requirements.txt
pkg install tesseract -y
pip install pillow pytesseract rich requests maigret
python3 photo_osint.py
