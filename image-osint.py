import os
import re
import sys
import asyncio
import webbrowser
import subprocess
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pytesseract

# ───────────────────────────────
# Auto-Installer for Maigret
# ───────────────────────────────
def ensure_maigret():
    try:
        import maigret
        return maigret
    except ImportError:
        print("\n⚠️ Maigret not found. Installing automatically...\n")

        home = os.path.expanduser("~")
        maigret_path = os.path.join(home, "maigret")

        if not os.path.exists(maigret_path):
            subprocess.call(["git", "clone", "https://github.com/soxoj/maigret.git", maigret_path])

        requirements = os.path.join(maigret_path, "requirements.txt")
        if os.path.exists(requirements):
            subprocess.call([sys.executable, "-m", "pip", "install", "-r", requirements])

        sys.path.append(maigret_path)
        try:
            import maigret
            print("✅ Maigret installed successfully!\n")
            return maigret
        except ImportError:
            print("❌ Failed to load Maigret even after installation.")
            return None

# ───────────────────────────────
# EXIF + GPS Extraction
# ───────────────────────────────
def get_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_tag = GPSTAGS.get(t, t)
                    gps_data[sub_tag] = value[t]
                exif_data[tag_name] = gps_data
            else:
                exif_data[tag_name] = value
    return exif_data

def convert_to_degrees(value):
    d, m, s = value
    return d[0] / d[1] + (m[0] / m[1]) / 60 + (s[0] / s[1]) / 3600

def get_gps_coords(exif_data):
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

# ───────────────────────────────
# OCR + Username Finder
# ───────────────────────────────
def extract_text(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {e}"

def find_usernames(text):
    return set(re.findall(r'@?([a-zA-Z0-9._-]{3,20})', text))

# ───────────────────────────────
# Reverse Image Search
# ───────────────────────────────
def reverse_image_search(image_path):
    print("\n🌐 Launching Reverse Image Search...")
    webbrowser.open("https://images.google.com/")
    webbrowser.open("https://yandex.com/images/")
    webbrowser.open("https://www.bing.com/visualsearch")
    webbrowser.open("https://tineye.com/")
    print("✅ Tabs opened: Google, Yandex, Bing, TinEye")
    print("👉 Upload the image manually for best results.")

# ───────────────────────────────
# Username OSINT with Maigret
# ───────────────────────────────
async def check_usernames(usernames, maigret):
    if not usernames:
        print("\n🙅 No usernames found in text/metadata.")
        return

    print("\n👤 Possible Usernames Found:\n")
    for u in usernames:
        print(f"- {u}")

    if maigret is None:
        print("\n⚠️ Maigret not installed. Skipping username scan.")
        return

    print("\n🔎 Checking usernames across social media...\n")
    for username in usernames:
        try:
            result = await maigret.search(username, timeout=5)
            for site, data in result['sites'].items():
                if data['status'].is_found():
                    print(f"✅ Found {username} on {site}: {data['url']}")
        except Exception as e:
            print(f"⚠️ Error with {username}: {e}")

# ───────────────────────────────
# Main
# ───────────────────────────────
def main():
    print("╭──────────────────────────────────────────────────────────────╮")
    print("│               📸 Hardcore OSINT Image Analyzer 🔎                          │")
    print("╰──────────────────────────────────────────────────────────────╯")

    image_path = input("Enter image path: ").strip()
    if not os.path.isfile(image_path):
        print("❌ File not found.")
        return

    # Load Maigret (auto-install if missing)
    maigret = ensure_maigret()

    # Metadata
    exif_data = get_exif_data(image_path)
    if exif_data:
        print("\n📸 Extracted Metadata:")
        for k, v in exif_data.items():
            print(f"{k}: {v}")
    else:
        print("\nNo EXIF metadata found.")

    # GPS
    lat, lon = get_gps_coords(exif_data)
    if lat and lon:
        print(f"\n🌍 GPS Coordinates: {lat}, {lon}")
        print(f"🔗 Google Maps: https://maps.google.com/?q={lat},{lon}")

    # OCR
    print("\n🔍 Extracted Text (OCR):\n")
    text = extract_text(image_path)
    print(text if text else "No text detected.")

    # Reverse Image Search
    reverse_image_search(image_path)

    # Username Hunting
    usernames = find_usernames(text)
    asyncio.run(check_usernames(usernames, maigret))

    print("\n╭──────────────────────────────────────────────────────────────╮")
    print("│ Analysis Completed ✅                                        │")
    print("╰──────────────────────────────────────────────────────────────╯")

    print("\n⚡ Script developed with pride ⚡")
    print("╭──────────────────────────────────────────────────────────────╮")
    print("│ by cyber-23priyanshu                                         │")
    print("╰──────────────────────────────────────────────────────────────╯")

if __name__ == "__main__":
    main()    try:
        image = Image.open(image_path)
        exif_data = {}
        info = image._getexif()
        if info:
            for tag, value in info.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_tag = GPSTAGS.get(t, t)
                        gps_data[sub_tag] = value[t]
                    exif_data[tag_name] = gps_data
                else:
                    exif_data[tag_name] = value
        return exif_data
    except UnidentifiedImageError:
        return {"Error": "❌ Unsupported or corrupted image format"}
    except Exception as e:
        return {"Error": f"❌ Could not read EXIF: {e}"}

def convert_to_degrees(value):
    try:
        d, m, s = value
        return float(d) + float(m) / 60 + float(s) / 3600
    except Exception:
        return None

def get_gps_coords(exif_data):
    gps_info = exif_data.get("GPSInfo", {})
    if gps_info:
        lat = gps_info.get("GPSLatitude")
        lat_ref = gps_info.get("GPSLatitudeRef")
        lon = gps_info.get("GPSLongitude")
        lon_ref = gps_info.get("GPSLongitudeRef")

        if lat and lon and lat_ref and lon_ref:
            lat = convert_to_degrees(lat)
            lon = convert_to_degrees(lon)
            if lat and lon:
                if lat_ref != "N":
                    lat = -lat
                if lon_ref != "E":
                    lon = -lon
                return lat, lon
    return None, None

# ------------------------
# OCR
# ------------------------
def extract_text(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text.strip()
    except Exception:
        return ""

# ------------------------
# Username Extraction
# ------------------------
def find_usernames(text):
    if not text:
        return set()
    return set(re.findall(r'@?([a-zA-Z0-9._-]{3,20})', text))

async def check_usernames(usernames):
    results = {}
    if not maigret_available:
        return {"Error": ["⚠️ Maigret not installed. Run: pip install maigret"]}
    if usernames:
        client = Maigret()
        for username in usernames:
            try:
                found_sites = []
                search_results = await client.search(username)
                for site, data in search_results.items():
                    if data["status"].is_found():
                        found_sites.append(f"{site}: {data['url']}")
                results[username] = found_sites if found_sites else ["❌ Not found anywhere"]
            except Exception as e:
                results[username] = [f"Error: {e}"]
    return results

# ------------------------
# Reverse Image Search
# ------------------------
def reverse_image_search(image_path):
    animate_print("\n🌐 Launching Reverse Image Search...", style="bold magenta")

    try:
        webbrowser.open("https://images.google.com/")
        webbrowser.open("https://yandex.com/images/")
        webbrowser.open("https://www.bing.com/visualsearch")
        webbrowser.open("https://tineye.com/")
        console.print("[green]✅ Tabs opened: Google, Yandex, Bing, TinEye[/green]")
        console.print("[cyan]👉 Upload the image manually for best results.[/cyan]")
    except Exception as e:
        console.print(f"[red]❌ Could not open browser: {e}[/red]")

# ------------------------
# MAIN
# ------------------------
def main():
    console.print(Panel("📸 [bold magenta]Hardcore OSINT Image Analyzer[/bold magenta] 🔎", style="cyan", expand=True))

    image_path = input("Enter image path: ").strip()
    if not os.path.isfile(image_path):
        console.print("[red]❌ File not found.")
        return

    # --- Metadata ---
    exif_data = get_exif_data(image_path)
    if exif_data:
        animate_print("\n📸 Extracted Metadata:\n", style="bold yellow")
        table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        table.add_column("Tag", style="cyan")
        table.add_column("Value", style="white")

        for key, value in exif_data.items():
            table.add_row(str(key), str(value))
        console.print(table)

    # --- GPS ---
    lat, lon = get_gps_coords(exif_data)
    if lat and lon:
        animate_print("\n🌍 GPS Coordinates Found!", style="bold magenta")
        console.print(f"[cyan]Latitude:[/cyan] {lat}\n[cyan]Longitude:[/cyan] {lon}")
        console.print(f"🔗 [green]Google Maps:[/green] https://maps.google.com/?q={lat},{lon}")

    # --- OCR ---
    animate_print("\n🔍 Extracted Text (OCR):\n", style="bold blue")
    text = extract_text(image_path)
    console.print(Panel(text if text else "No text detected.", style="blue"))

    # --- Reverse Image Search ---
    reverse_image_search(image_path)

    # --- Usernames ---
    usernames = find_usernames(text)
    if usernames:
        animate_print("\n👤 Possible Usernames Found:\n", style="bold green")
        console.print(", ".join(usernames))
        results = asyncio.run(check_usernames(usernames))
        for user, sites in results.items():
            animate_print(f"\n🌐 Results for: {user}", style="bold magenta")
            for site in sites:
                console.print(f"   ✅ {site}", style="green")
    else:
        console.print("\n🙅 No usernames found in text/metadata.", style="red")

    # --- Footer ---
    console.print(Panel("[bold cyan]Analysis Completed ✅[/bold cyan]", expand=True))
    animate_print("\n⚡ Script developed with pride ⚡", style="bold yellow")
    console.print(Panel("[bold magenta]by cyber-23priyanshu[/bold magenta]", expand=True, style="green"))

if __name__ == "__main__":
    main()
