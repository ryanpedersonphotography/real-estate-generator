# Real Estate Tour Generator

A Python-based static site generator that creates beautiful, single-page real estate tour websites from listing data and photos.

## Features

- ✅ **Interactive Wizard Mode** - Step-by-step prompts to create listings without editing JSON
- ✅ **Automated Netlify Deployment** - Deploy directly from wizard with site tracking
- ✅ **Simple CLI** - One command to build a complete listing site
- ✅ **Mobile-First Design** - Responsive layout that looks great on all devices  
- ✅ **Interactive Lightbox** - Click photos to view in fullscreen with navigation
- ✅ **Multiple Themes** - Classic Light, Luxury Dark, Modern Light
- ✅ **Agent Profile** - Optional agent photo and contact information
- ✅ **3D Tours** - Matterport integration with responsive iframes
- ✅ **Video Tours** - YouTube/Vimeo embed support
- ✅ **SEO Optimized** - Meta tags, keywords, and structured data ready
- ✅ **Fast Loading** - Static generation with optimized images (Phase 4)
- ✅ **Graceful Fallbacks** - All sections are optional and handle missing data elegantly

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ryanpedersonphotography/real-estate-generator
cd real-estate-generator

# Install dependencies
pip3 install --user --break-system-packages jinja2
# Or use a virtual environment:
# python3 -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt
```

### Option 1: Interactive Wizard Mode (NEW! ✨)

The easiest way to create a listing - just answer prompts!

1. **Prepare your property folder**:
   ```
   my-property-name/
     photos/          # Add all property photos here
     hero.jpg         # Optional: Specific hero image
     agent.jpg        # Optional: Agent photo
   ```

2. **Run the wizard**:
   ```bash
   python3 site.py wizard
   ```

3. **Follow the prompts**:
   ```
   Enter property folder name: my-property-name
   ✓ Found folder: my-property-name/
   ✓ Found 12 photos in photos/ folder
   
   PROPERTY DETAILS (All optional - press Enter to skip)
   Property Title: Beautiful Lakefront Home
   Address: 123 Main St, City, ST 12345
   Price: 450000
   Bedrooms: 3
   Bathrooms: 2
   ...
   
   Generate site now? (y/n) [y]: y
   ✓ Site ready at: dist/my-property-name/index.html
   
   Deploy to Netlify? (y/n) [n]: y
   ✓ Site deployed to: https://my-property-name.netlify.app
   ```

### Option 2: Manual JSON Configuration

For batch processing or advanced control:

1. **Prepare your listing folder** with this structure:
   ```
   listings/my-property/
     listing.json          # Property details and configuration
     photos/               # JPEG photos of the property
       01-front.jpg
       02-living.jpg
       ...
   ```

2. **Run the build command**:
   ```bash
   python3 site.py build --input listings/my-property --output dist/my-property
   ```

3. **Preview the site**:
   ```bash
   open dist/my-property/index.html
   ```

### Deploy to Netlify

#### Option 1: Automated Deployment (Recommended)

The wizard now includes built-in Netlify deployment! When you run the wizard, after building your site you'll be asked:

```
Deploy to Netlify? (y/n) [n]: y

Select deployment option:
  1. Deploy to new site (auto-generated URL)
  2. Deploy to custom subdomain
  3. Link to existing Netlify site
  4. Skip deployment
```

The tool automatically:
- Creates new Netlify sites or updates existing ones
- Tracks site IDs in `.netlify/state.json` for reliable re-deployment
- Handles custom subdomains (e.g., `my-property.netlify.app`)
- Remembers your sites for future updates

**Requirements**: Install [Netlify CLI](https://docs.netlify.com/cli/get-started/) first:
```bash
npm install -g netlify-cli
netlify login
```

#### Option 2: Manual Deployment

1. Drag and drop the `dist/my-property` folder to [Netlify](https://app.netlify.com)
2. Your site will be live in seconds!

## Listing Configuration

Create a `listing.json` file with your property details:

```json
{
  "title": "Beautiful Family Home",
  "address": "123 Main St, Springfield, IL 62701",
  "details": {
    "price": 450000,
    "beds": 4,
    "baths": 2.5,
    "sqft": 2400
  },
  "agent": {
    "name": "John Smith",
    "phone": "555-123-4567",
    "email": "john@realty.com",
    "company": "Premier Realty"
  },
  "seo": {
    "title": "Beautiful Family Home - 123 Main St Springfield",
    "description": "Stunning 4 bed, 2.5 bath family home in Springfield",
    "keywords": ["Springfield real estate", "family home", "4 bedroom house"]
  },
  "theme": {
    "scheme": "classic-light"  // or "luxury-dark", "modern-light"
  }
}
```

### Required Fields
- `title` - Property listing title
- `address` - Full property address
- `details.price` - Listing price (number)
- `details.beds` - Number of bedrooms
- `details.baths` - Number of bathrooms
- `details.sqft` - Square footage

### Optional Fields
- `details.year_built` - Year the property was built
- `details.property_type` - Type of property (e.g., "Single Family")
- `details.mls` - MLS listing number
- `agent.name` - Agent's full name
- `agent.photo` - Filename of agent photo (e.g., "agent.jpg")
- `agent.phone` - Agent phone number
- `agent.email` - Agent email address
- `agent.company` - Real estate company name
- `agent.license` - Agent license number
- `seo.*` - SEO metadata
- `theme.scheme` - Color theme selection

### Agent Photo
Place the agent photo file in the listing folder root (same level as `listing.json`):
```
listings/my-property/
  listing.json
  agent.jpg         # Agent photo (optional)
  photos/
    ...
```

## Wizard Mode Details

The interactive wizard mode makes it easy to create listings without touching JSON:

### Folder Structure
```
property-folder-name/
  photos/              # Required: Property photos
    01-photo.jpg
    02-photo.jpg
    ...
  hero.jpg            # Optional: Hero image (otherwise uses first photo)
  agent.jpg           # Optional: Agent photo
```

### What the Wizard Asks
- **Property Details** - Title, address, price, beds, baths, sqft (all optional)
- **Additional Info** - Year built, property type, MLS number (optional)
- **Agent Information** - Name, phone, email, company, license (optional)
- **Media URLs** - Matterport 3D tour, YouTube/Vimeo video (optional)
- **Site Configuration** - Theme selection, hero style
- **Deployment Options** - Deploy to Netlify with auto or custom subdomain

### Special Features
- **All Fields Optional** - Press Enter to skip any field
- **Smart Defaults** - Reasonable defaults for empty fields
- **Auto-detect Assets** - Finds hero.jpg and agent.jpg automatically
- **SEO Generation** - Creates meta tags from your inputs
- **Instant Preview** - Option to open in browser immediately
- **Site Tracking** - Remembers Netlify sites for reliable re-deployment
- **Auto Deployment** - One-click deploy with custom subdomain support

## Available Themes

- **classic-light** - Clean, professional light theme (default)
- **luxury-dark** - Elegant dark theme with gold accents
- **modern-light** - Contemporary light theme with green accents

## Project Structure

```
real-estate-generator/
  site.py              # Main generator script with wizard and deployment
  site_no_deploy.py    # Original version without deployment features
  requirements.txt     # Python dependencies
  templates/
    listing.html       # Page template
  static/
    styles.css         # Styling with themes
    lightbox.js        # Interactive photo gallery
  [property-folders]/  # Your property folders (in root)
    photos/            # Property photos
    hero.jpg           # Optional hero image
    agent.jpg          # Optional agent photo
    listing.json       # Generated by wizard
    .netlify/          # Site deployment tracking
      state.json       # Netlify site ID
  dist/                # Generated sites (gitignored)
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed development phases:

- ✅ **Phase 0-3**: Basic site generation with photos and details
- ✅ **Phase 3.5**: Interactive lightbox gallery
- ✅ **Phase 3.6**: Interactive wizard mode
- ✅ **Phase 3.7**: Automated Netlify deployment with site tracking
- 🚧 **Phase 4**: Image optimization with Pillow
- 📋 **Phase 5**: Multiple hero styles (slider, Ken Burns, video)
- 📋 **Phase 6**: Additional media sections (floor plans, aerials)
- 📋 **Phase 7**: CLI enhancements (--hero-style, --theme flags)
- 📋 **Phase 8**: Advanced deployment features

## Example

An example listing is included in `listings/example-listing/`. Build it with:

```bash
python3 site.py build --input listings/example-listing --output dist/example-listing
```

## Contributing

Contributions are welcome! Please check the ROADMAP.md for planned features and feel free to submit issues or pull requests.

## License

MIT License - feel free to use this for your real estate projects!