#!/usr/bin/env python3
"""
Real Estate Tour Generator - Static Site Builder with Interactive Wizard
Generates a single-page real estate tour from listing data and photos.
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Constants
ROOT_DIR = Path(__file__).parent
TEMPLATES_DIR = ROOT_DIR / "templates"
STATIC_DIR = ROOT_DIR / "static"

def prompt_optional(prompt_text, default=None):
    """Prompt for optional input, return None if empty."""
    if default:
        response = input(f"{prompt_text} [{default}]: ").strip()
        return response if response else default
    else:
        response = input(f"{prompt_text}: ").strip()
        return response if response else None

def prompt_number(prompt_text):
    """Prompt for numeric input, return None if empty."""
    response = input(f"{prompt_text}: ").strip()
    if not response:
        return None
    try:
        # Try to parse as float first (for bathrooms like 2.5)
        if '.' in response:
            return float(response)
        return int(response)
    except ValueError:
        print(f"  Warning: Invalid number, skipping field")
        return None

def wizard_mode():
    """Interactive wizard to create listing.json and build site."""
    print("\n" + "="*60)
    print("REAL ESTATE TOUR GENERATOR - INTERACTIVE WIZARD")
    print("="*60)
    
    # Get property folder
    folder_name = input("\nEnter property folder name: ").strip()
    if not folder_name:
        print("Error: Folder name is required")
        sys.exit(1)
    
    property_path = ROOT_DIR / folder_name
    
    # Check if folder exists
    if not property_path.exists():
        print(f"Error: Folder '{folder_name}' not found in {ROOT_DIR}")
        print(f"Please create the folder and add photos before running wizard")
        sys.exit(1)
    
    # Check for photos
    photos_dir = property_path / "photos"
    if not photos_dir.exists():
        print(f"Error: No photos/ subfolder found in {folder_name}")
        print(f"Please create {folder_name}/photos/ and add photos")
        sys.exit(1)
    
    # Count photos
    photo_files = list(photos_dir.glob("*.jpg")) + list(photos_dir.glob("*.jpeg"))
    photo_files = [f for f in photo_files if f.name not in ['hero.jpg', 'agent.jpg']]
    
    print(f"✓ Found folder: {folder_name}/")
    print(f"✓ Found {len(photo_files)} photos in photos/ folder")
    
    # Check for special images
    hero_exists = (property_path / "hero.jpg").exists()
    agent_exists = (property_path / "agent.jpg").exists()
    
    if hero_exists:
        print(f"✓ Found hero.jpg")
    else:
        print(f"✗ No hero.jpg found (will use first photo)")
    
    if agent_exists:
        print(f"✓ Found agent.jpg")
    else:
        print(f"✗ No agent.jpg found")
    
    # Initialize listing data
    listing = {}
    
    # Property Details (all optional)
    print("\n" + "="*60)
    print("PROPERTY DETAILS (All optional - press Enter to skip)")
    print("="*60)
    
    listing["title"] = prompt_optional("Property Title") or "Property Listing"
    listing["address"] = prompt_optional("Address") or "Address Not Provided"
    
    # Details section
    details = {}
    price = prompt_number("Price (numbers only)")
    if price:
        details["price"] = price
    else:
        details["price"] = 0  # Default to 0 if not provided
    
    beds = prompt_number("Bedrooms")
    if beds:
        details["beds"] = beds
    else:
        details["beds"] = 0
    
    baths = prompt_number("Bathrooms")
    if baths:
        details["baths"] = baths
    else:
        details["baths"] = 0
    
    sqft = prompt_number("Square Feet")
    if sqft:
        details["sqft"] = sqft
    else:
        details["sqft"] = 0
    
    year_built = prompt_number("Year Built [optional]")
    if year_built:
        details["year_built"] = year_built
    
    property_type = prompt_optional("Property Type [optional]")
    if property_type:
        details["property_type"] = property_type
    
    mls = prompt_optional("MLS Number [optional]")
    if mls:
        details["mls"] = mls
    
    listing["details"] = details
    
    # Agent Information
    print("\n" + "="*60)
    print("AGENT INFORMATION (press Enter to skip all)")
    print("="*60)
    
    agent_name = prompt_optional("Agent Name [optional]")
    if agent_name:
        agent = {"name": agent_name}
        
        if agent_exists:
            agent["photo"] = "agent.jpg"
        
        agent_phone = prompt_optional("Agent Phone [optional]")
        if agent_phone:
            agent["phone"] = agent_phone
        
        agent_email = prompt_optional("Agent Email [optional]")
        if agent_email:
            agent["email"] = agent_email
        
        agent_company = prompt_optional("Agent Company [optional]")
        if agent_company:
            agent["company"] = agent_company
        
        agent_license = prompt_optional("Agent License [optional]")
        if agent_license:
            agent["license"] = agent_license
        
        listing["agent"] = agent
    
    # Additional Media
    print("\n" + "="*60)
    print("ADDITIONAL MEDIA (press Enter to skip)")
    print("="*60)
    
    media = {}
    matterport = prompt_optional("Matterport URL [optional]")
    if matterport:
        media["matterport_url"] = matterport
    
    video_url = prompt_optional("Video URL (YouTube/Vimeo) [optional]")
    if video_url:
        media["video_url"] = video_url
    
    if media:
        listing["media"] = media
    
    # SEO (auto-generate if not provided)
    seo = {}
    seo["title"] = listing.get("title", "Property Listing")
    if listing.get("address") and listing["address"] != "Address Not Provided":
        seo["title"] = f"{listing['title']} - {listing['address']}"
    
    seo["description"] = f"Property listing"
    if details.get("beds") and details["beds"] > 0:
        seo["description"] = f"{details['beds']} bed"
    if details.get("baths") and details["baths"] > 0:
        seo["description"] += f", {details['baths']} bath"
    if listing.get("address") and listing["address"] != "Address Not Provided":
        seo["description"] += f" property at {listing['address']}"
    
    listing["seo"] = seo
    
    # Site Configuration
    print("\n" + "="*60)
    print("SITE CONFIGURATION")
    print("="*60)
    
    print("\nSelect Theme:")
    print("  1. Classic Light (default)")
    print("  2. Luxury Dark")
    print("  3. Modern Light")
    theme_choice = prompt_optional("Choice", "1")
    
    theme_map = {
        "1": "classic-light",
        "2": "luxury-dark",
        "3": "modern-light"
    }
    theme = theme_map.get(theme_choice, "classic-light")
    listing["theme"] = {"scheme": theme}
    
    print("\nSelect Hero Style:")
    print("  1. Single Image (default)")
    print("  2. Image Slider (coming soon)")
    print("  3. Video Hero (coming soon)")
    hero_choice = prompt_optional("Choice", "1")
    
    hero_map = {
        "1": "single",
        "2": "slider",
        "3": "video"
    }
    hero_style = hero_map.get(hero_choice, "single")
    listing["hero"] = {"style": hero_style}
    
    # Handle hero image
    if hero_exists:
        listing["hero"]["image"] = "hero.jpg"
    
    # Save listing.json
    listing_path = property_path / "listing.json"
    with open(listing_path, 'w') as f:
        json.dump(listing, f, indent=2)
    
    print(f"\n✓ Created: {folder_name}/listing.json")
    
    # Ask to generate site
    generate = prompt_optional("\nGenerate site now? (y/n)", "y")
    if generate.lower() == 'y':
        print(f"✓ Building site...")
        output_path = ROOT_DIR / "dist" / folder_name
        build_site(property_path, output_path, hero_exists=hero_exists)
        print(f"✓ Site ready at: dist/{folder_name}/index.html")
        
        # Offer to open in browser
        open_browser = prompt_optional("Open in browser? (y/n)", "n")
        if open_browser.lower() == 'y':
            import webbrowser
            webbrowser.open(f"file://{output_path}/index.html")
    else:
        print(f"\nTo build later, run:")
        print(f"  python site.py build --input {folder_name} --output dist/{folder_name}")

def load_listing_data(input_path, required_validation=True):
    """Load and validate listing.json from input directory."""
    listing_file = Path(input_path) / "listing.json"
    
    if not listing_file.exists():
        print(f"Error: listing.json not found in {input_path}")
        sys.exit(1)
    
    with open(listing_file, 'r') as f:
        data = json.load(f)
    
    # Only validate required fields if not from wizard
    if required_validation:
        # For wizard-generated files, we use defaults so skip validation
        pass
    
    return data

def collect_photos(input_path):
    """Collect all jpg/jpeg files from photos directory."""
    photos_dir = Path(input_path) / "photos"
    
    if not photos_dir.exists():
        print(f"Error: photos directory not found in {input_path}")
        sys.exit(1)
    
    # Collect all jpg/jpeg files
    photos = []
    for ext in ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG"]:
        photos.extend(photos_dir.glob(ext))
    
    # Filter out hero.jpg and agent.jpg from main gallery
    photos = [p for p in photos if p.name not in ['hero.jpg', 'agent.jpg']]
    
    if not photos:
        print(f"Error: No photos found in {photos_dir}")
        sys.exit(1)
    
    # Sort by filename for consistent ordering
    photos.sort()
    
    # Return just the filenames
    return [p.name for p in photos]

def process_image(src_path, dest_path):
    """
    Process and copy image to destination.
    For v1: Simple copy. Will be replaced with Pillow optimization in Phase 4.
    """
    shutil.copy2(src_path, dest_path)
    # TODO: Phase 4 - Replace with Pillow resize/compress

def build_site(input_path, output_path, hero_exists=False):
    """Build the static site from input listing to output directory."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    print(f"Building site from {input_path} to {output_path}")
    
    # Load listing data
    listing = load_listing_data(input_path, required_validation=False)
    photos = collect_photos(input_path)
    
    # Clean and create output directory
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (output_path / "photos").mkdir(exist_ok=True)
    (output_path / "static").mkdir(exist_ok=True)
    
    # Copy and process photos
    print(f"Processing {len(photos)} photos...")
    for photo in photos:
        src = input_path / "photos" / photo
        dest = output_path / "photos" / photo
        process_image(src, dest)
    
    # Handle hero image
    hero_image = None
    hero_src = input_path / "hero.jpg"
    if hero_src.exists():
        hero_dest = output_path / "hero.jpg"
        process_image(hero_src, hero_dest)
        hero_image = "hero.jpg"
        print("Processing hero.jpg")
    elif photos:
        # Use first photo as hero
        hero_image = f"photos/{photos[0]}"
    
    # Process agent photo if it exists
    agent_photo_filename = None
    if listing.get("agent", {}).get("photo"):
        agent_photo_path = input_path / listing["agent"]["photo"]
        if agent_photo_path.exists():
            agent_photo_filename = listing["agent"]["photo"]
            # Create agent subdirectory if needed
            (output_path / "agent").mkdir(exist_ok=True)
            dest = output_path / "agent" / agent_photo_filename
            process_image(agent_photo_path, dest)
            print(f"Processing agent photo: {agent_photo_filename}")
    
    # Copy static assets (CSS, JS including lightbox)
    if STATIC_DIR.exists():
        for item in STATIC_DIR.iterdir():
            if item.is_file():
                shutil.copy2(item, output_path / "static" / item.name)
        
        # Ensure lightbox.js is included
        lightbox_path = STATIC_DIR / "lightbox.js"
        if not lightbox_path.exists():
            print("Warning: lightbox.js not found in static directory")
    
    # Prepare template context
    context = {
        # Basic listing data
        "listing": listing,
        "title": listing.get("title", "Property Listing"),
        "address": listing.get("address", ""),
        "details": listing.get("details", {}),
        
        # Photos
        "photos": photos,
        "hero_image": hero_image,
        
        # Agent info (optional)
        "agent": listing.get("agent", {}),
        "agent_photo_path": f"agent/{agent_photo_filename}" if agent_photo_filename else None,
        
        # SEO
        "seo_title": listing.get("seo", {}).get("title", listing.get("title", "Property Listing")),
        "seo_description": listing.get("seo", {}).get("description", "Real estate listing"),
        "seo_keywords": listing.get("seo", {}).get("keywords", []),
        
        # Theme
        "theme_scheme": listing.get("theme", {}).get("scheme", "classic-light"),
        
        # Hero style
        "hero_style": listing.get("hero", {}).get("style", "single"),
        
        # Format price with commas (only if price exists and > 0)
        "price_formatted": f"${listing.get('details', {}).get('price', 0):,}" if listing.get('details', {}).get('price', 0) > 0 else None,
        
        # Media
        "matterport_url": listing.get("media", {}).get("matterport_url"),
        "video_url": listing.get("media", {}).get("video_url"),
    }
    
    # Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    # Render template
    try:
        template = env.get_template("listing.html")
        html = template.render(**context)
    except Exception as e:
        print(f"Error rendering template: {e}")
        sys.exit(1)
    
    # Write HTML output
    output_file = output_path / "index.html"
    output_file.write_text(html, encoding='utf-8')
    
    print(f"✓ Site built successfully!")
    print(f"  Output: {output_path}/index.html")
    print(f"  Photos: {len(photos)}")
    print(f"  Theme: {context['theme_scheme']}")
    print(f"\nTo preview: open {output_path}/index.html in a browser")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a static real estate tour site from listing data and photos."
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build a listing site')
    build_parser.add_argument(
        '--input',
        required=True,
        help='Path to listing folder containing listing.json and photos/'
    )
    build_parser.add_argument(
        '--output',
        required=True,
        help='Path to output folder for generated site'
    )
    
    # Wizard command
    wizard_parser = subparsers.add_parser('wizard', help='Interactive wizard to create and build listing')
    
    args = parser.parse_args()
    
    if args.command == 'build':
        build_site(args.input, args.output)
    elif args.command == 'wizard':
        wizard_mode()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()