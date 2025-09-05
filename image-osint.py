#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import asyncio
import webbrowser
import subprocess
from PIL import Image, ExifTags, UnidentifiedImageError
import pytesseract

# ╭──────────────────────────────╮
# │ Auto Install & Import Maigret │
# ╰──────────────────────────────╯
def ensure_maigret():
    try:
        import maigret
        return True
    except ImportError:
        print("\n⚠️  Maigret not found. Installing automatically...\n")
        home = os.path.expanduser("~")
        maigret_path = os.path.join(home, "maigret")

        # Clone repo if not exists
        if not os.path.exists(maigret_path):
            subprocess.call(["git", "clone", "https://github.com/soxoj/maigret.git", maigret_path])

        # Install dependencies
        reqs = os.path.join(maigret_path, "requirements.txt")
        if os.path.exists(reqs):
            subprocess.call([sys.executable, "-m", "pip", "install", "-r", reqs])

        sys.path.append(maigret_path)
        try:
            import maigret
            print("✅ Maigret installed successfully.")
            return True
        except ImportError:
            print("❌ Failed to load Maigret even after installation.")
            return False


# ╭──────────────────────────────╮
# │ EXIF Extraction              │
# ╰──────────────────────────────╯
def get_exif_data(image_path):
    """Extract EXIF data from image."""
    try:
        image = Image.open(image_path)
        exif_data = {}
        info = image._getexif()

        if info:
            for tag, value in info.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                if tag_name == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_tag = ExifTags.GPSTAGS.get(t, t)
                        gps_data[sub_tag] = value[t]
                    exif_data[tag_name] = gps_data
                else:
                    exif_data[tag_name] = value
        return exif_data

    except UnidentifiedImageError:
        return {"Error": "❌ Unsupported or corrupted image format"}
    except Exception as e:
        return {"Error": str(e)}


def convert_to_degrees(value):
    """Convert GPS coordinates to degrees."""
    try:
        d, m, s = value
        return float(d) + (float(m) / 60.0) + (float(s) / 3600.0)
    except Exception:
        return None


def get_gps_coords(exif_data):
    """Extract latitude and longitude from EXIF."""
    gps_info = exif_data.get("GPSInfo", {})
    if gps_info:
        lat = gps_info.get("GPSLatitude")
        lat_ref = gps_info.get("GPSLatitudeRef")
        lon = gps_info.get("GPSLongitude")
        lon_ref = gps_info.get("GPSLongitudeRef")

        if lat and lon and lat_ref and lon_ref:
            lat = convert_to_degrees(lat)
            lon = convert_to_degrees(lon)
            if lat_ref != "N":
                lat = -lat
            if lon_ref != "E":
                lon = -lon
            return lat, lon
    return None, None


# ╭──────────────────────────────╮
# │ OCR Text Extraction          │
# ╰──────────────────────────────╯
def extract_text(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {e}"


# ╭──────────────────────────────╮
# │ Reverse Image Search         │
# ╰──────────────────────────────╯
def reverse_image_search():
    print("\n🌐 Launching Reverse Image Search...")
    webbrowser.open("https://images.google.com/")
    webbrowser.open("https://yandex.com/images/")
    webbrowser.open("https://www.bing.com/visualsearch")
    webbrowser.open("https://tineye.com/")
    print("✅ Tabs opened: Google, Yandex, Bing, TinEye")
    print("👉 Upload the image manually for best results.")


# ╭──────────────────────────────╮
# │ Username Finder              │
# ╰──────────────────────────────╯
def find_usernames(text):
    return set(re.findall(r'@?([a-zA-Z0-9._-]{3,20})', text))


async def check_usernames(usernames):
    if not usernames:
        print("\n🙅 No usernames found in text/metadata.")
        return

    print("\n👤 Possible Usernames Found:\n")
    for username in usernames:
        print(username)

    if ensure_maigret():
        import maigret
        print("\n🔎 Checking usernames on social media...\n")
        for username in usernames:
            try:
                result = await maigret.search(username, timeout=5)
                for site, data in result['sites'].items():
                    if data['status'].is_found():
                        print(f"✅ Found {username} on {site}: {data['url']}")
            except Exception as e:
                print(f"⚠️ Error checking {username}: {e}")
    else:
        print("\n⚠️ Maigret not available. Skipping username checks.")


# ╭──────────────────────────────╮
# │ Main Analyzer                │
# ╰──────────────────────────────╯
def main():
    print("╭──────────────────────────────────────────────────────────────╮")
    print("│ 📸 Hardcore OSINT Image Analyzer 🔎                          │")
    print("╰──────────────────────────────────────────────────────────────╯")

    image_path = input("Enter image path: ").strip()

    if not os.path.isfile(image_path):
        print("❌ File not found.")
        return

    # Metadata
    exif_data = get_exif_data(image_path)
    if exif_data:
        print("\n📸 Extracted Metadata:\n")
        for key, value in exif_data.items():
            print(f"{key}: {value}")
    else:
        print("\n❌ No EXIF metadata found.")

    # GPS
    lat, lon = get_gps_coords(exif_data)
    if lat and lon:
        print(f"\n🌍 GPS Coordinates: {lat}, {lon}")
        print(f"🔗 Google Maps Link: https://maps.google.com/?q={lat},{lon}")

    # OCR
    print("\n🔍 Extracted Text (OCR):\n")
    text = extract_text(image_path)
    print(text if text else "No text detected.")

    # Reverse Image Search
    reverse_image_search()

    # Username hunting
    usernames = find_usernames(text)
    asyncio.run(check_usernames(usernames))

    # Final banner
    print("\n╭──────────────────────────────────────────────────────────────╮")
    print("│ Analysis Completed ✅                                        │")
    print("╰──────────────────────────────────────────────────────────────╯")

    print("\n⚡ Script developed with pride ⚡")
    print("╭──────────────────────────────────────────────────────────────╮")
    print("│ by cyber-23priyanshu                                         │")
    print("╰──────────────────────────────────────────────────────────────╯")


if __name__ == "__main__":
    main()
