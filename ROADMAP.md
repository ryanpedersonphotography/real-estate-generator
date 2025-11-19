# Real Estate Tour Generator – Focused Roadmap

Goal: A Python CLI that takes `listing.json + photos/` and generates a fast, single-page static tour site. Then progressively adds hero variations, extra media sections, and image optimization.

---

## Phase 0 – Repo + Minimal Skeleton

- [ ] Create repo structure
- [ ] Add basic structure:
  ```
  real-estate-tours/
    site.py
    config.json              # global settings (optional now)
    /templates
      listing.html
    /static
      styles.css
    /listings
      /example-listing
        listing.json
        /photos
    /dist                    # gitignored; build output
  ```
- [ ] Add `.gitignore` with:
  - `dist/`
  - `__pycache__/`
  - `.DS_Store`
  - `*.pyc`
  - `.env`

---

## Phase 1 – Data Model + Example Listing

**Goal**: Lock the schema and have a concrete example to work against.

- [ ] Define `listings/example-listing/listing.json`:
  ```json
  {
    "slug": "example-listing",
    "title": "Modern Lakefront Home",
    "address": "123 Lakeview Dr, Brainerd, MN 56401",
    "details": {
      "price": 875000,
      "beds": 4,
      "baths": 3,
      "sqft": 3200
    },
    "agent": {
      "name": "Jane Doe",
      "phone": "218-555-0123",
      "email": "jane@example.com",
      "company": "North Shore Realty"
    },
    "seo": {
      "title": "Modern Lakefront Home – 123 Lakeview Dr, Brainerd MN",
      "description": "Stunning modern lakefront home with 4 beds, 3 baths and panoramic views.",
      "keywords": [
        "Brainerd lakefront home",
        "Minnesota real estate"
      ]
    },
    "media": {
      "matterport_url": null,
      "video_url": null
    },
    "theme": {
      "scheme": "classic-light"
    }
  }
  ```
- [ ] Drop 5–10 sample JPGs into `listings/example-listing/photos/`
- [ ] Decide required fields for v1:
  - title
  - address
  - details.price
  - details.beds
  - details.baths
  - details.sqft
  
Everything else optional.

---

## Phase 2 – Simple CLI + Generator (no optimization)

**Goal**: One command builds a working static page from photos + listing.json.

- [ ] Install deps:
  ```bash
  pip install jinja2
  ```

- [ ] Implement minimal CLI in `site.py` using argparse:
  - Command: `python site.py build --input listings/example-listing --output dist/example-listing`
  - Args:
    - `--input` (required): path to listing folder
    - `--output` (required): path to output folder

- [ ] In `site.py`:
  - Parse args with argparse
  - Load listing.json from --input
  - Collect photo filenames from --input/photos/*.jpg
  - Create --output directory (clean it if it exists)
  - Copy static/styles.css into --output/static/styles.css
  - Copy photos into --output/photos/ (raw copy for now)
  - Render templates/listing.html with Jinja2 into --output/index.html
  
- [ ] Hardcode defaults in code:
  - Hero style: "single-image"
  - Theme: "classic-light"
  
No CLI flags for hero/theme in v1.

---

## Phase 3 – Minimal Template + Styling

**Goal**: One clean, single-page layout: single-image hero, details, gallery, agent.

- [x] Create `templates/listing.html` with:
  - `<head>`:
    - `<title>{{ seo_title }}</title>`
    - `<meta name="description" content="{{ seo_description }}">`
    - `<meta name="viewport" content="width=device-width, initial-scale=1">`
    - `<link rel="stylesheet" href="static/styles.css">`
  - `<body class="theme-{{ theme_scheme }}">`:
    - Hero (single image):
      - First photo as hero: `<img src="photos/{{ photos[0] }}" alt="Hero photo of {{ address }}">`
      - Overlay: title + address + price
    - Details section:
      - Address, price, beds/baths/sqft in a simple grid
    - Gallery section:
      - Grid of remaining photos (all photos including hero is fine to start)
    - Agent section:
      - Name, company, phone, email

- [ ] In `site.py`, compute:
  - `seo_title = listing["seo"]["title"] or listing["title"]`
  - `seo_description = listing["seo"]["description"] or "Real estate listing at " + listing["address"]`
  - `theme_scheme = listing["theme"]["scheme"] or "classic-light"`

- [x] Create basic `static/styles.css`:
  - Mobile-first layout
  - Simple typography
  - `.theme-classic-light` with light background, dark text
  - Hero full-width image, details as a card, gallery as 2-column grid on mobile, 3–4 columns on desktop

- [x] Run `python site.py build ...` and open `dist/example-listing/index.html` in a browser
- [x] Confirm: hero shows, details correct, gallery loads, agent info at bottom

---

## Phase 3.5 – Lightbox Gallery (COMPLETED)

**Goal**: Add interactive lightbox for photo gallery viewing.

- [x] Create `static/lightbox.js`:
  - Vanilla JavaScript, no dependencies
  - Click gallery images to open in fullscreen lightbox
  - Keyboard navigation (arrows, escape)
  - Touch-friendly mobile controls
  - Image counter and captions
  
- [x] Update `templates/listing.html`:
  - Include lightbox.js script
  
- [x] Update `static/styles.css`:
  - Lightbox overlay styles
  - Smooth transitions
  - Responsive controls
  
**Features**:
- Click any gallery image to open lightbox
- Navigate with arrow keys or on-screen buttons
- Press Escape or click backdrop to close
- Shows image counter (e.g., "3 / 10")
- Mobile optimized with touch support

---

## Phase 4 – Image Optimization (Pillow) – Upgrade

**Goal**: Replace raw copies with optimized images, keeping same behavior.

- [ ] Install Pillow:
  ```bash
  pip install pillow
  ```

- [ ] In `site.py`, replace raw copy with:
  ```python
  from PIL import Image
  
  def process_image(src_path, dest_path, max_long_edge=2000, quality=85):
      img = Image.open(src_path)
      w, h = img.size
      scale = max_long_edge / max(w, h)
      if scale < 1.0:
          new_size = (int(w * scale), int(h * scale))
          img = img.resize(new_size, Image.LANCZOS)
      img.save(dest_path, format="JPEG", quality=quality, optimize=True, progressive=True)
  ```

- [ ] Use `process_image` for each photo when writing into `--output/photos/`
- [ ] Rebuild and verify:
  - Images still look good
  - File sizes are way smaller

---

## Phase 5 – Hero Variants (API, not full UI yet)

**Goal**: Make hero style pluggable, but only implement single-image now.

- [ ] In listing.json, add optional:
  ```json
  "hero": {
    "style": "single"   // future: "slider", "kenburns", "video"
  }
  ```

- [ ] In `site.py`, compute:
  ```python
  hero_style = (listing.get("hero") or {}).get("style", "single")
  ```

- [ ] In `listing.html`, wrap hero in conditional, but only support "single" for now:
  ```html
  {% if hero_style == "single" %}
    <!-- single image hero markup -->
  {% endif %}
  ```
  
- [ ] Later you'll add `elif hero_style == "slider"` / `"kenburns"` / `"video"` blocks or partials
- [ ] (Optional) Add a CLI flag later:
  ```bash
  python site.py build --input ... --output ... --hero-style slider
  ```
  
For now: no flag, just config-driven.

---

## Phase 6 – Extra Sections (Matterport, Video, Aerials, Floorplan)

**Goal**: Make the template smart about optional extras without exploding complexity.

Do this only after v1 feels solid.

- [ ] Extend listing.json schema (you already have media object – now actually use it):
  ```json
  "media": {
    "matterport_url": "https://my.matterport.com/show/?m=XXXX",
    "video_url": "https://youtu.be/...",
    "has_aerials": true,
    "has_floorplan": true
  }
  ```

- [ ] In `site.py`, detect optional folders:
  - `aerials/` → list of files or empty list
  - `floorplan/` → list of files or empty list
  - Pass to template:
    - `matterport_url`
    - `video_url`
    - `aerial_photos`
    - `floorplan_images`

- [ ] In `listing.html`, add conditional sections:
  - `{% if matterport_url %}` 3D Tour section `{% endif %}`
  - `{% if video_url %}` Video section `{% endif %}`
  - `{% if aerial_photos %}` Aerials section `{% endif %}`
  - `{% if floorplan_images %}` Floorplan section `{% endif %}`
  
Keep layout simple; styling can be iterative.

---

## Phase 7 – Small CLI Enhancements

**Goal**: Add a couple of useful flags once the core engine is stable.

- [ ] Add `--hero-style` flag:
  - Valid choices: single, slider, kenburns, video
  - If provided, override `listing["hero"]["style"]`
  
- [ ] Add `--theme` flag:
  - Valid choices: classic-light, luxury-dark, etc.
  - If provided, override `listing["theme"]["scheme"]`
  
- [ ] Add `--slug` or auto-detect slug from folder name and use it in template

---

## Phase 8 – Netlify-ready

**Goal**: Make deployment a 10-second task.

- [ ] In repo root, add simple README instructions:
  - Run:
    ```bash
    python site.py build --input listings/example-listing --output dist/example-listing
    ```
  - Then drag `dist/example-listing` folder into Netlify UI

- [ ] (Optional) Add `netlify.toml`:
  ```toml
  [build]
    publish = "dist/example-listing"
    command = "python site.py build --input listings/example-listing --output dist/example-listing"
  ```

- [ ] Deploy once, sanity check, done

---

## Phase 9 – Polish & Enhancements (Future)

Once core is solid, consider:

- [x] Lightbox for gallery images (COMPLETED in Phase 3.5)
- [ ] Smooth scroll navigation
- [ ] Contact form with Netlify Forms
- [ ] SEO improvements (Open Graph, structured data)
- [ ] Multiple theme variations
- [ ] Batch processing multiple listings
- [ ] Index page for all listings
- [ ] Analytics integration
- [ ] Accessibility improvements
- [ ] Performance optimizations

---

## Success Criteria for Each Phase

Each phase is complete when:
- All checkboxes are checked
- The feature works end-to-end
- Code is clean and documented
- Manual test passes
- Ready for next phase to build on top

Start with Phase 0-3 to get a working v1, then iterate!