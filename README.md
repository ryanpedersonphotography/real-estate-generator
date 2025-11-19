# Real Estate Tour Generator

A Python-based static site generator that creates beautiful, single-page real estate tour websites from listing data and photos.

## Features

- ✅ **Simple CLI** - One command to build a complete listing site
- ✅ **Mobile-First Design** - Responsive layout that looks great on all devices  
- ✅ **Interactive Lightbox** - Click photos to view in fullscreen with navigation
- ✅ **Multiple Themes** - Classic Light, Luxury Dark, Modern Light
- ✅ **Agent Profile** - Optional agent photo and contact information
- ✅ **SEO Optimized** - Meta tags, keywords, and structured data ready
- ✅ **Fast Loading** - Static generation with optimized images (Phase 4)
- ✅ **Flexible Media** - Support for photos, video, Matterport tours, floor plans (coming soon)
- ✅ **Graceful Fallbacks** - All sections are optional and handle missing data elegantly

## Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd real-estate-generator

# Install dependencies
pip3 install --user --break-system-packages jinja2
# Or use a virtual environment:
# python3 -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt
```

### Build Your First Site

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

## Available Themes

- **classic-light** - Clean, professional light theme (default)
- **luxury-dark** - Elegant dark theme with gold accents
- **modern-light** - Contemporary light theme with green accents

## Project Structure

```
real-estate-generator/
  site.py              # Main generator script
  config.json          # Global configuration
  requirements.txt     # Python dependencies
  templates/
    listing.html       # Page template
  static/
    styles.css         # Styling
  listings/            # Your property listings
    example-listing/   # Example property
  dist/                # Generated sites (gitignored)
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed development phases:

- ✅ **Phase 0-3**: Basic site generation with photos and details
- 🚧 **Phase 4**: Image optimization with Pillow
- 📋 **Phase 5**: Multiple hero styles (slider, Ken Burns, video)
- 📋 **Phase 6**: Additional media sections (Matterport, video, aerials)
- 📋 **Phase 7**: CLI enhancements (--hero-style, --theme flags)
- 📋 **Phase 8**: Netlify deployment optimization

## Example

An example listing is included in `listings/example-listing/`. Build it with:

```bash
python3 site.py build --input listings/example-listing --output dist/example-listing
```

## Contributing

Contributions are welcome! Please check the ROADMAP.md for planned features and feel free to submit issues or pull requests.

## License

MIT License - feel free to use this for your real estate projects!