import os
import urllib.request

FONT_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS = {
    "Inter-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
    "Inter-Italic.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter-Italic%5Bopsz%2Cwght%5D.ttf",
    "Montserrat-Bold.ttf": "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Bold.ttf",
    "Montserrat-Regular.ttf": "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Regular.ttf",
    "PlayfairDisplay-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
    "PlayfairDisplay-Italic.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf"
}

def setup_fonts():
    fonts_path = os.path.join(FONT_DIR, "fonts")
    os.makedirs(fonts_path, exist_ok=True)
    
    print("Setting up fonts...")
    for filename, url in FONTS.items():
        dest = os.path.join(fonts_path, filename)
        if not os.path.exists(dest):
            print(f"Downloading {filename} from {url}...")
            try:
                # Add User-Agent to bypass potential bot block
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
                )
                with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
                    out_file.write(response.read())
                print(f"Successfully downloaded {filename}")
            except Exception as e:
                print(f"Failed to download {filename}: {e}")
                print("Will fallback to default system fonts if available.")
        else:
            print(f"{filename} already exists.")

if __name__ == "__main__":
    setup_fonts()
