# Quick Start Guide 🚀

Get your real estate listing online in 5 minutes!

## Prerequisites

- Python 3.7+ installed
- Photos of your property
- 5 minutes of your time

## Installation

```bash
# Clone the repository
git clone https://github.com/ryanpedersonphotography/real-estate-generator
cd real-estate-generator

# Install dependencies
pip3 install --user jinja2 pillow
```

## Fastest Way: Wizard Mode 🧙‍♂️

### Step 1: Prepare Your Photos

Create a folder for your property and add photos:

```bash
mkdir my-property
mkdir my-property/photos
# Copy your photos into my-property/photos/
```

**Pro tip**: Organize photos in subfolders for filtering:
```bash
my-property/
  photos/
    exterior/     # Outside shots
    interior/     # Inside shots
    kitchen/      # Kitchen photos
```

### Step 2: Run the Wizard

```bash
python3 site.py wizard
```

### Step 3: Follow the Prompts

The wizard will ask you about:

1. **Property folder** → Type: `my-property`
2. **Photo organization** → Choose: Merge all or Filter by category
3. **Hero image** → Select from your photos
4. **Property details** → All optional! Press Enter to skip
5. **Generate site** → Yes!
6. **Deploy to Netlify** → Optional (requires Netlify CLI)

### Step 4: View Your Site

```bash
open dist/my-property/index.html
```

That's it! Your site is ready! 🎉

---

## Common Scenarios

### "I just have photos, nothing else"

Perfect! The wizard handles this:

```bash
# Create folder and add photos
mkdir beach-house
cp ~/Desktop/house-photos/* beach-house/photos/

# Run wizard - press Enter to skip all fields
python3 site.py wizard
# Enter: beach-house
# Press Enter repeatedly to use defaults
# Type: y to generate

# Done!
```

### "I want a hero image"

Add a `hero.jpg` to your property folder:

```bash
my-property/
  hero.jpg        # This will be the main image
  photos/         # Rest of your photos
```

### "I want my agent photo included"

Add `agent.jpg` to your property folder:

```bash
my-property/
  agent.jpg       # Agent photo
  photos/         # Property photos
```

### "I have photos in different folders"

The tool automatically detects this:

```bash
my-property/
  photos/
    exterior/     # Outdoor shots
    interior/     # Indoor shots
    aerial/       # Drone shots
```

You'll be asked:
- **Merge all** → Single gallery
- **Filter by category** → Buttons to filter: [All] [Exterior] [Interior] [Aerial]

### "I want to deploy online"

Install Netlify CLI first:

```bash
npm install -g netlify-cli
netlify login
```

Then during wizard, choose "y" when asked about deployment.

---

## Manual Mode (Advanced)

If you prefer creating `listing.json` manually:

### Step 1: Create listing.json

```json
{
  "title": "Beautiful Beach House",
  "address": "123 Ocean Drive, Malibu, CA",
  "details": {
    "price": 2500000,
    "beds": 4,
    "baths": 3,
    "sqft": 3200
  },
  "agent": {
    "name": "Jane Doe",
    "phone": "555-0123",
    "email": "jane@realty.com"
  },
  "theme": {
    "scheme": "luxury-dark"
  }
}
```

### Step 2: Build the Site

```bash
python3 site.py build --input my-property --output dist/my-property
```

---

## Features at a Glance

### 🎨 Themes

Choose during wizard:
- **Classic Light** - Clean, professional
- **Luxury Dark** - Elegant, high-end
- **Modern Light** - Contemporary, fresh

### 📸 Image Optimization

Automatic! Your images are:
- Resized to web-friendly dimensions
- Compressed for fast loading (50-70% smaller)
- Progressive JPEG for better perceived performance

### 🎭 Interactive Gallery

- Click any photo to open fullscreen
- Navigate with arrows or swipe
- ESC or click outside to close

### 📱 Mobile Responsive

Sites look perfect on:
- Phones
- Tablets  
- Desktops
- Even TVs!

---

## Troubleshooting

### "Command not found: python3"

Try `python` instead of `python3`:
```bash
python site.py wizard
```

### "No module named jinja2"

Install dependencies:
```bash
pip3 install --user jinja2 pillow
```

### "Photos not showing"

Check your folder structure:
```bash
my-property/
  photos/         # ← Must be named "photos"
    image1.jpg    # ← JPEG files
    image2.jpg
```

### "Deployment failed"

Make sure Netlify CLI is installed:
```bash
npm install -g netlify-cli
netlify login
```

### "Site looks broken"

Open from the `dist` folder:
```bash
# Correct
open dist/my-property/index.html

# Wrong - won't load CSS/JS properly
open my-property/index.html
```

---

## Tips & Tricks

### 🎯 Best Practices

1. **Photo Order**: Name files to control order
   ```
   01-exterior-front.jpg
   02-exterior-back.jpg
   03-living-room.jpg
   ```

2. **Photo Quality**: 
   - Use high-res photos (they'll be optimized)
   - Landscape orientation works best
   - Bright, well-lit shots

3. **Hero Image**:
   - Best exterior shot as `hero.jpg`
   - Or select during wizard
   - 16:9 aspect ratio ideal

### ⚡ Speed Tips

- **Batch Processing**: Process multiple properties
  ```bash
  for folder in property-*; do
    python3 site.py build --input "$folder" --output "dist/$folder"
  done
  ```

- **Reuse Templates**: Save `listing.json` as template
  ```bash
  cp my-property/listing.json template.json
  # Edit and reuse for similar properties
  ```

### 🚀 Advanced Features

- **Matterport Tours**: Add URL during wizard
- **YouTube Videos**: Include video URL
- **Custom Domains**: Configure in Netlify
- **Analytics**: Add Google Analytics ID

---

## Examples

### Minimal Setup (Photos Only)

```bash
mkdir simple-house
cp photos/* simple-house/photos/
python3 site.py wizard
# Enter: simple-house
# Press Enter for all prompts
# Type: y
```

### Full Featured

```bash
mkdir luxury-estate
mkdir -p luxury-estate/photos/{exterior,interior,aerial}
# Add photos to respective folders
cp headshot.jpg luxury-estate/agent.jpg
cp best-exterior.jpg luxury-estate/hero.jpg

python3 site.py wizard
# Enter all details
# Choose luxury-dark theme
# Deploy to Netlify
```

### Command Line Pro

```bash
# Quick one-liner for existing listing.json
python3 site.py build --input prop1 --output dist/prop1 && open dist/prop1/index.html

# Process all properties
find . -name "listing.json" -exec dirname {} \; | while read dir; do
  python3 site.py build --input "$dir" --output "dist/$(basename $dir)"
done
```

---

## Next Steps

- 📖 Read full [README.md](README.md) for detailed features
- 🗺️ Check [ROADMAP.md](ROADMAP.md) for upcoming features
- 🐛 Report issues on [GitHub](https://github.com/ryanpedersonphotography/real-estate-generator/issues)
- ⭐ Star the repo if you find it useful!

---

## Help

```bash
# Show all options
python3 site.py --help

# Show version
python3 site.py --version

# Get wizard help
python3 site.py wizard --help

# Get build help
python3 site.py build --help
```

---

**Happy listing! 🏡**