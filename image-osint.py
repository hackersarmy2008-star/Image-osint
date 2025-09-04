import os
import re
import time
import asyncio
import webbrowser
import requests
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS, GPSTAGS
import pytesseract
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Safe import Maigret
try:
    from maigret.maigret import Maigret
    maigret_available = True
except ImportError:
    maigret_available = False

console = Console()

# ------------------------
# Animation Utility
# ------------------------
def animate_print(text, delay=0.02, style="bold cyan"):
    for char in text:
        console.print(char, style=style, end="")
        time.sleep(delay)
    console.print("")

# ------------------------
# Metadata
# ------------------------
def get_exif_data(image_path):
    try:
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
