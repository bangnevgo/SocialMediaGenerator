# Notulen: AuraForge Social Media Content Studio

**Tanggal:** 29 Mei 2026
**Repository:** [github.com/bangnevgo/SocialMediaGenerator](https://github.com/bangnevgo/SocialMediaGenerator)
**Live Demo:** [social-media-generator-delta-five.vercel.app](https://social-media-generator-delta-five.vercel.app)

---

## Deskripsi Proyek

AuraForge adalah aplikasi web **Social Media Content Studio** untuk membuat konten media sosial (gambar & video) dengan preview realtime di browser. Dibangun dengan HTML5 Canvas + vanilla JS di frontend, dan Python (Pillow/FFmpeg) di backend engine.

**Total:** ~3.800 baris kode | 27 file source | 31 unit tests

---

## Fitur Utama

| Fitur | Detail |
|-------|--------|
| **4 Template Layout** | Quote Card, Tech Tip, Code Frame, Simple Text |
| **3 Aspect Ratio** | 1:1 (Feed), 4:5 (Portrait), 9:16 (Story/Reels) |
| **Glassmorphism Card** | Frosted glass dengan drag-and-drop repositioning |
| **Background Customizer** | 6 gradient preset, custom color, upload gambar |
| **AI Image Generation** | Via HuggingFace, Replicate, atau OpenAI DALL-E 3 |
| **Prompt Builder** | Form terstruktur (Nano Banana & Veo 3.1 formula) |
| **Parchment Post** | Template khusus bergaya kertas tua Neville Goddard |
| **Video Slideshow** | Kompilasi gambar + audio ke MP4 vertikal via FFmpeg |
| **CLI Helper** | Auto-generate perintah Python untuk rendering |
| **PNG Download** | Export canvas ke file PNG |
| **Flask Backend** | API endpoint untuk AI generation end-to-end |

---

## Struktur Proyek

```
social-media-generator/
├── index.html                  # Main HTML entry point
├── style.css                   # Global stylesheet (+ CSS variables)
├── server.py                   # Flask backend server
├── .gitignore                  # Git ignore rules
├── NOTULEN.md                   # File ini
│
├── js/                         # Frontend modules (ES modules)
│   ├── app.js                  # Main entry point & wiring
│   ├── state.js                # App state & DOM references
│   ├── render.js               # Canvas rendering engine
│   ├── drag.js                 # Drag & drop engine
│   ├── cli.js                  # CLI command generators
│   ├── prompt-builder.js       # AI prompt builder
│   └── modal.js                # Modal & clipboard helpers
│
├── engine/                     # Python rendering engines
│   ├── config.py               # Centralized layout constants
│   ├── create_post.py          # Social media post generator
│   ├── create_parchment_post.py # Parchment-style quote card
│   ├── create_video.py         # Video slideshow compiler
│   ├── ai_generator.py         # AI image/video generation
│   ├── setup_fonts.py          # Font downloader
│   └── fonts/                  # Custom font files (TTF)
│
├── tests/                      # Unit tests (unittest)
│   ├── __init__.py
│   ├── test_create_post.py     # 17 tests
│   ├── test_parchment.py       # 8 tests
│   └── test_ai_generator.py    # 6 tests
│
├── ai_assets/                  # Generated AI images (gitignored)
├── posts/                      # Generated post images (gitignored)
└── videos/                     # Generated videos (gitignored)
```

---

## Perbaikan yang Dilakukan (29 Mei 2026)

### 🔴 Bug Fixes Kritis (6)

| # | Bug | Perbaikan |
|---|-----|-----------|
| 1 | Template quote default tidak sinkron — title "AuraForge" tapi body Steve Jobs quote | HTML initial values disamakan: `title="Steve Jobs"`, `body=quote` |
| 2 | `line_mult_height()` membuat objek `ImageDraw` baru setiap baris (sangat lambat) | Dihapus fungsi terpisah; line height dihitung sekali per font |
| 3 | Upload gambar tidak reset active gradient preset di UI | Ditambah `bgPresets.forEach(p => p.classList.remove("active"))` |
| 4 | Drag card tanpa batas — bisa keluar canvas sepenuhnya | Ditambah `clampOffset()` dengan max 20% dimensi canvas |
| 5 | Vignette parchment berbentuk cincin bertingkat (80 ellipse step) | Diganti radial gradient smooth per-pixel dengan quadratic ease-out |
| 6 | `draw_wrapped_text` Python tidak support `\n` (beda dengan JS) | Ditambah split per paragraph sebelum word-wrapping |

### 🟡 Arsitektur & Kode (7)

| # | Masalah | Solusi |
|---|---------|--------|
| 7 | `app.js` 900+ baris monolith, susah di-maintain | Di-split jadi **7 ES modules** di folder `js/` |
| 8 | AI generation hanya menampilkan modal instruksi manual | Ditambah **Flask backend** (`server.py`) dengan endpoint `/api/generate-image` |
| 9 | File `.env` terekspos tanpa `.gitignore` | Dibuat `.gitignore` + validasi token di `_validate_token()` (cek empty & panjang min 10 char) |
| 10 | Font fallback tanpa warning — desain berubah drastis tanpa terasa | Ditambah `logging.warning` saat fallback dipakai; mapping terpusat di `_FONT_FALLBACK` |
| 11 | Canvas render tanpa error handling — gagal diamati | Ditambah `try/catch` + error badge merah di UI + placeholder "Render error" |
| 12 | Hardcoded values (margin, font ratio, video settings) tersebar di 5+ file | Dipusatkan ke **`engine/config.py`** sebagai single source of truth |
| 13 | Tidak ada unit test | Ditambah **31 unit tests** (`tests/`) — semua passing ✅ |

---

## Tech Stack

| Layer | Teknologi |
|-------|-----------|
| **Frontend** | HTML5 Canvas, Vanilla JS (ES modules), CSS3 |
| **Backend API** | Python Flask + flask-cors |
| **Image Engine** | Python Pillow (PIL) |
| **Video Engine** | FFmpeg (subprocess) |
| **AI APIs** | HuggingFace Inference, Replicate, OpenAI DALL-E 3 |
| **Testing** | Python unittest |
| **Deployment** | Vercel (frontend), GitHub (source) |

---

## Cara Menjalankan

### Frontend Only (Static)
```bash
# Buka langsung di browser
open index.html

# Atau via Python simple server
python3 -m http.server 8000
# → http://localhost:8000
```

### Full Stack (dengan AI generation)
```bash
# 1. Install dependencies
pip3 install flask flask-cors Pillow

# 2. Setup API keys
cp .env.example .env
# Edit .env dengan API token kamu

# 3. Start Flask server
python3 server.py
# → http://127.0.0.1:5000

# 4. Buka frontend (bisa via simple server atau langsung file://)
```

### Run Tests
```bash
python3 -m unittest discover -s tests -v
# 31 tests OK ✅
```

---

## API Endpoints (server.py)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/status` | Health check + provider availability |
| POST | `/api/generate-image` | Generate AI image (`prompt`, `provider`, `aspect_ratio`) |
| POST | `/api/render-post` | Render post PNG (`template`, `ratio`, `title`, `body`, dll.) |
| GET | `/api/preview/<path>` | Serve generated asset files |

---

## Catatan Deployment

- **Frontend** → Vercel (auto-deploy dari GitHub) ✅ Live
- **Backend Flask** → Butuh deploy terpisah (Railway / Heroku / Fly.io) ⏳ Belum di-setup
- **Command generate AI** di UI akan menampilkan error "backend not reachable" jika Flask tidak jalan — ini expected behavior

---

## Git Commits

```
a4f71bd  fix: make API_BASE configurable via window.__API_BASE__ env override
3bddfbd  Initial commit — AuraForge Social Media Content Studio
```

---

*Dibuat oleh OWL — 29 Mei 2026*
