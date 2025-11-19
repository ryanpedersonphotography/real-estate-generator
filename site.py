#!/usr/bin/env python3
"""
Real Estate Tour Generator - Static Site Builder
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

def load_listing_data(input_path):
    """Load and validate listing.json from input directory."""
    listing_file = Path(input_path) / "listing.json"
    
    if not listing_file.exists():
        print(f"Error: listing.json not found in {input_path}")
        sys.exit(1)
    
    with open(listing_file, 'r') as f:
        data = json.load(f)
    
    # Validate required fields
    required = ["title", "address", "details"]
    for field in required:
        if field not in data:
            print(f"Error: Required field '{field}' missing in listing.json")
            sys.exit(1)
    
    # Validate required detail fields
    required_details = ["price", "beds", "baths", "sqft"]
    for field in required_details:
        if field not in data["details"]:
            print(f"Error: Required field 'details.{field}' missing in listing.json")
            sys.exit(1)
    
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

def build_site(input_path, output_path):
    """Build the static site from input listing to output directory."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    print(f"Building site from {input_path} to {output_path}")
    
    # Load listing data
    listing = load_listing_data(input_path)
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
        "title": listing["title"],
        "address": listing["address"],
        "details": listing["details"],
        
        # Photos
        "photos": photos,
        
        # Agent info (optional)
        "agent": listing.get("agent", {}),
        "agent_photo_path": f"agent/{agent_photo_filename}" if agent_photo_filename else None,
        
        # SEO
        "seo_title": listing.get("seo", {}).get("title") or listing["title"],
        "seo_description": listing.get("seo", {}).get("description") or f"Real estate listing at {listing['address']}",
        "seo_keywords": listing.get("seo", {}).get("keywords", []),
        
        # Theme
        "theme_scheme": listing.get("theme", {}).get("scheme", "classic-light"),
        
        # Hero style (hardcoded for v1)
        "hero_style": "single",
        
        # Format price with commas
        "price_formatted": f"${listing['details']['price']:,}"
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
    
    args = parser.parse_args()
    
    if args.command == 'build':
        build_site(args.input, args.output)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()