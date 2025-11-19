# Real Estate Tour Generator – Focused Roadmap

Goal: A Python CLI that takes `listing.json + photos/` and generates a fast, single-page static tour site. Then progressively adds hero variations, extra media sections, and image optimization.

---

## Phase 0 – Repo + Minimal Skeleton

- [x] Create repo structure
- [x] Add basic structure:
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
- [x] Add `.gitignore` with:
  - `dist/`
  - `__pycache__/`
  - `.DS_Store`
  - `*.pyc`
  - `.env`

---

## Phase 1 – Data Model + Example Listing

**Goal**: Lock the schema and have a concrete example to work against.

- [x] Define `listings/example-listing/listing.json`:
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
- [x] Drop 5–10 sample JPGs into `listings/example-listing/photos/`
- [x] Decide required fields for v1:
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

- [x] Install deps:
  ```bash
  pip install jinja2
  ```

- [x] Implement minimal CLI in `site.py` using argparse:
  - Command: `python site.py build --input listings/example-listing --output dist/example-listing`
  - Args:
    - `--input` (required): path to listing folder
    - `--output` (required): path to output folder

- [x] In `site.py`:
  - Parse args with argparse
  - Load listing.json from --input
  - Collect photo filenames from --input/photos/*.jpg
  - Create --output directory (clean it if it exists)
  - Copy static/styles.css into --output/static/styles.css
  - Copy photos into --output/photos/ (raw copy for now)
  - Render templates/listing.html with Jinja2 into --output/index.html
  
- [x] Hardcode defaults in code:
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

- [x] In `site.py`, compute:
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

## Phase 4 – Image Optimization with Multi-Folder Support (COMPLETED)

**Goal**: Optimize images with Pillow, support multiple photo folders with merge/filter options.

### Core Image Optimization
- [x] Install Pillow:
  ```bash
  pip install pillow
  ```

- [x] Create image processing function:
  ```python
  from PIL import Image
  
  def optimize_image(src_path, dest_path, max_width=1920, quality=85):
      """Optimize image for web with size and quality adjustments."""
      img = Image.open(src_path)
      # Convert RGBA to RGB if needed
      if img.mode in ('RGBA', 'LA', 'P'):
          bg = Image.new('RGB', img.size, (255, 255, 255))
          bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
          img = bg
      # Resize if needed
      if img.width > max_width:
          ratio = max_width / img.width
          new_size = (max_width, int(img.height * ratio))
          img = img.resize(new_size, Image.LANCZOS)
      # Save optimized
      img.save(dest_path, 'JPEG', quality=quality, optimize=True, progressive=True)
  ```

- [x] Generate thumbnails for gallery:
  ```python
  def create_thumbnail(src_path, dest_path, size=(400, 300)):
      """Create thumbnail for gallery grid."""
      img = Image.open(src_path)
      img.thumbnail(size, Image.LANCZOS)
      img.save(dest_path, 'JPEG', quality=80, optimize=True)
  ```

### Multiple Folder Support
- [x] Detect subfolder structure in photos/:
  ```python
  def scan_photo_folders(photos_dir):
      """Scan for photos in root and subdirectories."""
      folders = {}
      # Check root level photos
      root_photos = [f for f in photos_dir.glob("*.jpg")]
      if root_photos:
          folders["all"] = root_photos
      # Check subdirectories
      for subdir in photos_dir.iterdir():
          if subdir.is_dir():
              sub_photos = list(subdir.glob("*.jpg"))
              if sub_photos:
                  folders[subdir.name] = sub_photos
      return folders
  ```

- [x] In wizard mode, detect multiple folders and ask user:
  ```
  ✓ Found multiple photo folders:
    - exterior/ (8 photos)
    - interior/ (12 photos) 
    - kitchen/ (5 photos)
    
  How would you like to organize the gallery?
    1. Merge all photos into one gallery
    2. Create filtered gallery with category buttons
  Choice [1]:
  ```

- [x] Store gallery organization preference:
  ```json
  "gallery": {
    "organization": "merged",  // or "filtered"
    "categories": ["exterior", "interior", "kitchen"]
  }
  ```

### Hero Image Selection
- [x] Check for hero.jpg in root directory (current behavior)
- [x] If no hero.jpg found, prompt user:
  ```
  No hero.jpg found. Select hero image:
    1. Use first photo from gallery
    2. Select specific photo
    3. Skip hero image
  Choice [1]:
  ```
  
- [x] If option 2, show numbered list of available photos:
  ```
  Select photo for hero:
    1. exterior/front-view.jpg
    2. exterior/sunset.jpg
    3. interior/living-room.jpg
    ...
  Enter number:
  ```

### Filtered Gallery Implementation
- [x] Add filter buttons to template when organization="filtered":
  ```html
  {% if gallery_organization == "filtered" %}
  <div class="gallery-filters">
    <button class="filter-btn active" data-filter="all">All</button>
    {% for category in gallery_categories %}
    <button class="filter-btn" data-filter="{{ category }}">
      {{ category|title }}
    </button>
    {% endfor %}
  </div>
  {% endif %}
  ```

- [x] Add JavaScript for filtering:
  ```javascript
  function initGalleryFilters() {
      const filterBtns = document.querySelectorAll('.filter-btn');
      const galleryItems = document.querySelectorAll('.gallery-item');
      
      filterBtns.forEach(btn => {
          btn.addEventListener('click', () => {
              const filter = btn.dataset.filter;
              // Update active button
              filterBtns.forEach(b => b.classList.remove('active'));
              btn.classList.add('active');
              // Filter items
              galleryItems.forEach(item => {
                  if (filter === 'all' || item.dataset.category === filter) {
                      item.style.display = 'block';
                  } else {
                      item.style.display = 'none';
                  }
              });
          });
      });
  }
  ```

### Agent Photo Handling
- [x] Already checking for agent.jpg in root (implemented)
- [x] Gracefully skip if not found (already implemented)

### Verification
- [x] Test with single folder structure (backwards compatible)
- [x] Test with multiple subfolders
- [x] Verify image optimization reduces file sizes by 50-70%
- [x] Ensure filter buttons work smoothly
- [x] Test hero image selection flow

---

## Phase 5 – Hero Variants (API, not full UI yet)

**Goal**: Make hero style pluggable, but only implement single-image now.

- [x] In listing.json, add optional:
  ```json
  "hero": {
    "style": "single"   // future: "slider", "kenburns", "video"
  }
  ```

- [x] In `site.py`, compute:
  ```python
  hero_style = (listing.get("hero") or {}).get("style", "single")
  ```

- [x] In `listing.html`, wrap hero in conditional, but only support "single" for now:
  ```html
  {% if hero_style == "single" %}
    <!-- single image hero markup -->
  {% endif %}
  ```
  
- [x] Later you'll add `elif hero_style == "slider"` / `"kenburns"` / `"video"` blocks or partials
- [x] (Optional) Add a CLI flag later:
  ```bash
  python site.py build --input ... --output ... --hero-style slider
  ```
  
For now: no flag, just config-driven.

---

## Phase 6 – Extra Sections (Matterport, Video, Aerials, Floorplan)

**Goal**: Make the template smart about optional extras without exploding complexity.

Do this only after v1 feels solid.

- [x] Extend listing.json schema (you already have media object – now actually use it):
  ```json
  "media": {
    "matterport_url": "https://my.matterport.com/show/?m=XXXX",
    "video_url": "https://youtu.be/...",
    "has_aerials": true,
    "has_floorplan": true
  }
  ```

- [x] In `site.py`, detect optional folders:
  - `aerials/` → list of files or empty list
  - `floorplan/` → list of files or empty list
  - Pass to template:
    - `matterport_url`
    - `video_url`
    - `aerial_photos`
    - `floorplan_images`

- [x] In `listing.html`, add conditional sections:
  - `{% if matterport_url %}` 3D Tour section `{% endif %}`
  - `{% if video_url %}` Video section `{% endif %}`
  - `{% if aerial_photos %}` Aerials section `{% endif %}`
  - `{% if floorplan_images %}` Floorplan section `{% endif %}`
  
Keep layout simple; styling can be iterative.

---

## Phase 7 – Small CLI Enhancements

**Goal**: Add a couple of useful flags once the core engine is stable.

- [x] Add `--hero-style` flag:
  - Valid choices: single, slider, kenburns, video
  - If provided, override `listing["hero"]["style"]`
  
- [x] Add `--theme` flag:
  - Valid choices: classic-light, luxury-dark, etc.
  - If provided, override `listing["theme"]["scheme"]`
  
- [x] Add `--slug` or auto-detect slug from folder name and use it in template

---

## Phase 8 – Netlify-ready

**Goal**: Make deployment a 10-second task.

- [x] In repo root, add simple README instructions:
  - Run:
    ```bash
    python site.py build --input listings/example-listing --output dist/example-listing
    ```
  - Then drag `dist/example-listing` folder into Netlify UI

- [x] (Optional) Add `netlify.toml`:
  ```toml
  [build]
    publish = "dist/example-listing"
    command = "python site.py build --input listings/example-listing --output dist/example-listing"
  ```

- [x] Deploy once, sanity check, done

---

## Phase 9 – Testing & Performance Optimization

**Goal**: Ensure sites are fast, accessible, and SEO-optimized with automated testing.

### Lighthouse Integration
- [ ] Add Lighthouse CI for automated performance testing:
  ```bash
  npm install -g @lhci/cli
  lhci autorun --upload.target=temporary-public-storage
  ```

- [ ] Create performance budget:
  ```json
  {
    "performance": 90,
    "accessibility": 100,
    "best-practices": 95,
    "seo": 100
  }
  ```

- [ ] Add to build process:
  ```python
  def run_lighthouse_test(site_url):
      """Run Lighthouse audit and return scores."""
      subprocess.run(["lighthouse", site_url, "--output=json"])
  ```

### Playwright E2E Testing
- [ ] Install Playwright for cross-browser testing:
  ```bash
  pip install playwright
  playwright install
  ```

- [ ] Create test suite for generated sites:
  ```python
  # tests/test_site_generation.py
  def test_gallery_filtering():
      # Test filter buttons work
  def test_lightbox_navigation():
      # Test lightbox opens and navigates
  def test_responsive_layout():
      # Test mobile/tablet/desktop views
  def test_image_loading():
      # Verify lazy loading and optimization
  ```

- [ ] Add visual regression testing:
  - Screenshot comparison for themes
  - Layout verification across breakpoints
  - Cross-browser compatibility checks

### Performance Monitoring
- [ ] Add Core Web Vitals tracking:
  - Largest Contentful Paint (LCP) < 2.5s
  - First Input Delay (FID) < 100ms
  - Cumulative Layout Shift (CLS) < 0.1

- [ ] Implement performance reporting:
  ```
  ✓ Performance Score: 95/100
  ✓ Accessibility: 100/100
  ✓ SEO: 100/100
  ✓ Mobile Speed: Fast
  ```

### Automated Testing Workflow
- [ ] Pre-deployment checks:
  - Run Lighthouse on local build
  - Execute Playwright test suite
  - Validate HTML/CSS/JS
  - Check image optimization

- [ ] CI/CD integration:
  - GitHub Actions workflow
  - Automatic testing on PR
  - Performance regression alerts

---

## Phase 10 – Advanced Media & Interactivity

**Goal**: Rich media experiences and interactive features.

### Video Generation from Photos
- [ ] Auto-generate video tours using photos:
  - Ken Burns effect on images
  - Smooth transitions
  - Background music
  - Text overlays for rooms

### Interactive Floor Plans
- [ ] Clickable floor plan navigation:
  - SVG floor plans with hotspots
  - Click room to see photos
  - Highlight current room
  - Mobile-friendly interaction

### Virtual Staging Integration
- [ ] AI-powered virtual staging:
  - Upload empty room photos
  - Generate furnished versions
  - Toggle staged/unstaged view
  - Multiple style options

---

## Phase 11 – Intelligent Image Processing & Quality Control

**Goal**: Advanced image editing, quality detection, and automated enhancements for professional results.

### Image Quality Detection
- [ ] Automatic quality scoring system:
  ```python
  def analyze_image_quality(image_path):
      """Detect and score image quality issues."""
      return {
          "sharpness": 0.92,
          "exposure": "slightly_underexposed",
          "blur_detection": False,
          "noise_level": "low",
          "composition_score": 0.85,
          "resolution_adequate": True,
          "color_accuracy": 0.88
      }
  ```

- [ ] Quality-based image filtering:
  - Flag blurry or low-quality photos
  - Suggest best photos for hero image
  - Auto-reject unusable images
  - Quality threshold settings

### Automated Image Enhancement
- [ ] Smart exposure correction:
  - Auto-adjust brightness/contrast
  - HDR tone mapping
  - Shadow/highlight recovery
  - Adaptive histogram equalization

- [ ] Color correction & grading:
  - Auto white balance
  - Vibrance enhancement
  - Consistent color temperature
  - Match lighting across photos

- [ ] Advanced cropping & composition:
  - AI-powered smart crop
  - Rule of thirds alignment
  - Remove unwanted edges
  - Perspective correction

### Professional Image Editing
- [ ] Object removal capabilities:
  - Remove personal items
  - Clean up clutter
  - Remove vehicles from driveways
  - Erase power lines

- [ ] Sky replacement:
  - Detect overcast skies
  - Replace with blue sky options
  - Sunset/sunrise effects
  - Weather matching

- [ ] Image enhancement presets:
  ```python
  ENHANCEMENT_PRESETS = {
      "luxury": {
          "brightness": +10,
          "contrast": +15,
          "warmth": +5,
          "vibrance": +20
      },
      "modern": {
          "brightness": +5,
          "contrast": +20,
          "coolness": +3,
          "clarity": +15
      },
      "cozy": {
          "brightness": +8,
          "warmth": +10,
          "vibrance": +10,
          "vignette": "subtle"
      }
  }
  ```

### Batch Processing Workflows
- [ ] Preset application to all photos:
  - Apply consistent style
  - Batch color correction
  - Watermark addition
  - Metadata preservation

- [ ] Smart categorization:
  - Auto-detect room types with AI
  - Flag duplicate shots
  - Group similar angles
  - Suggest best of each room

### Quality Reports
- [ ] Generate image quality report:
  ```
  Image Quality Analysis Report
  ============================
  Total Images: 45
  High Quality: 38 (84%)
  Medium Quality: 5 (11%)
  Low Quality: 2 (5%)
  
  Recommended Actions:
  - Replace: IMG_2451.jpg (too blurry)
  - Enhance: IMG_2467.jpg (underexposed)
  - Hero Candidate: IMG_2401.jpg (score: 95/100)
  ```

- [ ] Professional compliance check:
  - MLS photo requirements
  - Minimum resolution validation
  - Aspect ratio compliance
  - File size optimization

### Integration with External Services
- [ ] AI enhancement APIs:
  - Remove.bg for background removal
  - Let's Enhance.io for upscaling
  - Clipdrop for object removal
  - Adobe Sensei for smart edits

- [ ] Professional tool integration:
  - Lightroom preset import
  - Photoshop action compatibility
  - Capture One styles
  - RAW file processing

---

## Phase 12 – Desktop Application with Visual GUI

**Goal**: Create a professional Electron desktop app with drag-and-drop interface for non-technical users.

### Core Application Features
- [ ] Electron app framework setup:
  ```javascript
  // main.js
  const { app, BrowserWindow, ipcMain } = require('electron');
  const path = require('path');
  
  function createWindow() {
    const win = new BrowserWindow({
      width: 1400,
      height: 900,
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false
      },
      icon: 'assets/icon.png',
      title: 'Real Estate Tour Generator Pro'
    });
    
    win.loadFile('index.html');
  }
  ```

- [ ] Modern UI with framework:
  - React or Vue.js for interface
  - Tailwind CSS for styling
  - Framer Motion for animations
  - Dark/light mode support

### Visual Workflow Interface
- [ ] Drag-and-drop photo management:
  - Drop folder or photos directly
  - Visual file browser
  - Thumbnail previews
  - Drag to reorder photos
  - Multi-select operations

- [ ] Visual project wizard:
  ```
  ┌─────────────────────────────────┐
  │  📁 Select Photos               │
  │  ↓                              │
  │  📝 Property Details            │
  │  ↓                              │
  │  🎨 Choose Theme                │
  │  ↓                              │
  │  ✨ Image Enhancement           │
  │  ↓                              │
  │  🚀 Generate & Deploy           │
  └─────────────────────────────────┘
  ```

- [ ] Live preview panel:
  - Real-time site preview
  - Theme switcher
  - Mobile/tablet/desktop views
  - Before/after image comparison

### Image Editing Suite
- [ ] Built-in image editor:
  - Crop tool with grid overlay
  - Brightness/contrast sliders
  - Color adjustment wheels
  - Rotation and straightening
  - Red-eye removal
  - Blemish removal brush

- [ ] Batch editing interface:
  - Apply to all checkbox
  - Side-by-side comparison
  - Undo/redo history
  - Preset dropdown menu
  - Save custom presets

- [ ] AI enhancement panel:
  - One-click enhance button
  - Sky replacement dropdown
  - Object removal tool
  - Virtual staging toggle
  - Quality score display

### Visual Quality Control
- [ ] Image quality dashboard:
  ```
  ┌──────────────────────────────┐
  │ Quality Analysis             │
  ├──────────────────────────────┤
  │ ✅ IMG_001.jpg  Score: 95   │
  │ ⚠️  IMG_002.jpg  Score: 72   │
  │    → Slightly blurry         │
  │ ❌ IMG_003.jpg  Score: 45   │
  │    → Too dark, recommend     │
  │      retake or enhance       │
  └──────────────────────────────┘
  ```

- [ ] Visual sorting interface:
  - Drag into category folders
  - Color-coded quality indicators
  - Duplicate detection highlighting
  - Best photo recommendations

### Property Details Form Builder
- [ ] Visual form interface:
  - Auto-complete for addresses
  - Price slider with formatting
  - Room counter widgets
  - Photo gallery assignment
  - Map integration for location

- [ ] Template management:
  - Save property templates
  - Import previous listings
  - Clone and modify
  - Export/import JSON

### Deployment & Publishing
- [ ] One-click deployment panel:
  - Netlify integration
  - Custom domain setup
  - SSL certificate status
  - Analytics integration
  - QR code generator

- [ ] Multi-platform publishing:
  ```
  ┌─────────────────────────┐
  │ Publish to:             │
  ├─────────────────────────┤
  │ ☑️ Netlify              │
  │ ☑️ GitHub Pages         │
  │ ☐ AWS S3               │
  │ ☐ FTP Server           │
  │ ☑️ Local Folder         │
  └─────────────────────────┘
  ```

### Project Management
- [ ] Visual project library:
  - Grid view of all projects
  - Thumbnail previews
  - Search and filter
  - Tags and categories
  - Recent projects

- [ ] Batch operations:
  - Process multiple listings
  - Bulk updates
  - Archive old projects
  - Export all sites

### Advanced Features
- [ ] Real-time collaboration:
  - Share projects with team
  - Comments on photos
  - Approval workflow
  - Version history

- [ ] Integration panel:
  - MLS sync
  - CRM connections
  - Cloud storage (Dropbox, Google Drive)
  - Social media scheduling

- [ ] Performance monitoring:
  - Lighthouse scores in-app
  - Loading speed preview
  - SEO checklist
  - Accessibility audit

### Native OS Integration
- [ ] System features:
  - Native file dialogs
  - OS notifications
  - Menu bar integration
  - Keyboard shortcuts
  - Auto-updates

- [ ] Performance optimization:
  - Hardware acceleration
  - Multi-threading for image processing
  - Background processing
  - Progress indicators

### Distribution
- [ ] Multi-platform builds:
  ```bash
  npm run build:mac    # macOS .app
  npm run build:win    # Windows .exe
  npm run build:linux  # Linux AppImage
  ```

- [ ] Installation packages:
  - Code signing for trust
  - Auto-updater integration
  - MSI installer for Windows
  - DMG for macOS
  - Snap/Flatpak for Linux

---

## Phase 13 – Polish & Enhancements (Future)

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