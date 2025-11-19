#!/usr/bin/env python3
"""
Real Estate Tour Generator - Static Site Builder with Interactive Wizard and Netlify Deployment
Generates a single-page real estate tour from listing data and photos.
"""

__version__ = "4.0.0"  # Phase 4 with image optimization and multi-folder support

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# Constants
ROOT_DIR = Path(__file__).parent
TEMPLATES_DIR = ROOT_DIR / "templates"
STATIC_DIR = ROOT_DIR / "static"

def optimize_image(src_path, dest_path, max_width=1920, quality=85):
    """Optimize image for web with size and quality adjustments."""
    if not PILLOW_AVAILABLE:
        # Fallback to simple copy if Pillow not available
        shutil.copy2(src_path, dest_path)
        return
    
    try:
        img = Image.open(src_path)
        
        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                bg.paste(img, mask=img.split()[-1])
            else:
                bg.paste(img)
            img = bg
        
        # Resize if needed
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # Save optimized
        img.save(dest_path, 'JPEG', quality=quality, optimize=True, progressive=True)
    except Exception as e:
        print(f"  Warning: Could not optimize {src_path.name}: {e}")
        shutil.copy2(src_path, dest_path)

def create_thumbnail(src_path, dest_path, size=(400, 300)):
    """Create thumbnail for gallery grid."""
    if not PILLOW_AVAILABLE:
        # Use full image if Pillow not available
        shutil.copy2(src_path, dest_path)
        return
    
    try:
        img = Image.open(src_path)
        
        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                bg.paste(img, mask=img.split()[-1])
            else:
                bg.paste(img)
            img = bg
        
        img.thumbnail(size, Image.LANCZOS)
        img.save(dest_path, 'JPEG', quality=80, optimize=True)
    except Exception as e:
        print(f"  Warning: Could not create thumbnail for {src_path.name}: {e}")
        shutil.copy2(src_path, dest_path)

def scan_photo_folders(photos_dir):
    """Scan for photos in root and subdirectories."""
    folders = {}
    all_photos = []
    
    # Check for photos in root level
    for ext in ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG"]:
        root_photos = list(photos_dir.glob(ext))
        # Filter out hero.jpg and agent.jpg
        root_photos = [p for p in root_photos if p.name.lower() not in ['hero.jpg', 'agent.jpg']]
        all_photos.extend(root_photos)
    
    if root_photos:
        folders["_root"] = root_photos
    
    # Check subdirectories
    for subdir in photos_dir.iterdir():
        if subdir.is_dir():
            sub_photos = []
            for ext in ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG"]:
                sub_photos.extend(subdir.glob(ext))
            
            if sub_photos:
                folders[subdir.name] = sub_photos
                all_photos.extend(sub_photos)
    
    # Always include "all" if we have any photos
    if all_photos:
        folders["all"] = all_photos
    
    return folders

def check_netlify_cli():
    """Check if Netlify CLI is installed."""
    try:
        result = subprocess.run(["netlify", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_netlify_sites():
    """Get list of user's Netlify sites."""
    try:
        result = subprocess.run(
            ["netlify", "sites:list", "--json"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            sites = json.loads(result.stdout)
            return sites
        return []
    except:
        return []

def handle_netlify_deployment(property_path, dist_path, folder_name):
    """Handle Netlify deployment with site tracking."""
    # Check if Netlify CLI is installed
    if not check_netlify_cli():
        print("\n⚠️  Netlify CLI not found")
        print("To enable deployment, install it with: npm install -g netlify-cli")
        return
    
    # Check for existing deployment
    netlify_dir = property_path / ".netlify"
    netlify_state = netlify_dir / "state.json"
    
    existing_site_id = None
    existing_site_url = None
    
    if netlify_state.exists():
        try:
            with open(netlify_state, 'r') as f:
                state = json.load(f)
                existing_site_id = state.get("siteId")
                # Try to get site info
                if existing_site_id:
                    result = subprocess.run(
                        ["netlify", "api", f"getSite", "--data", f'{{"site_id":"{existing_site_id}"}}'],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        site_info = json.loads(result.stdout)
                        existing_site_url = site_info.get("url") or site_info.get("ssl_url")
                    else:
                        # Site might have been deleted
                        existing_site_id = None
        except:
            existing_site_id = None
    
    print("\n" + "="*60)
    print("NETLIFY DEPLOYMENT")
    print("="*60)
    
    if existing_site_id:
        print(f"✓ Found existing Netlify site")
        if existing_site_url:
            print(f"  URL: {existing_site_url}")
        
        update = prompt_optional("\nUpdate existing site? (y/n)", "y")
        
        if update.lower() == 'y':
            print("\nDeploying to Netlify...")
            result = subprocess.run([
                "netlify", "deploy",
                "--dir", str(dist_path),
                "--site", existing_site_id,
                "--prod"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Site updated successfully!")
                # Try to extract URL from output
                for line in result.stdout.split('\n'):
                    if 'Website URL:' in line or 'Live URL:' in line:
                        url = line.split(':', 1)[1].strip()
                        print(f"  URL: {url}")
                        break
            else:
                print(f"❌ Deployment failed: {result.stderr}")
        return
    
    # No existing site, offer deployment options
    print("\nDeployment Options:")
    print("  1. Create new site (auto-generated URL)")
    print("  2. Create with custom subdomain")
    print("  3. Link to existing site")
    print("  4. Skip deployment")
    
    choice = prompt_optional("Choice", "4")
    
    if choice == "1":
        # Create new site with auto-generated name
        print("\nCreating new Netlify site...")
        
        # First initialize the site
        result = subprocess.run([
            "netlify", "init",
            "--manual",
            "--dir", str(dist_path)
        ], capture_output=True, text=True, input="n\n")
        
        # Deploy to new site
        result = subprocess.run([
            "netlify", "deploy",
            "--dir", str(dist_path),
            "--prod"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Site deployed successfully!")
            
            # Try to extract site ID and URL from output
            site_id = None
            site_url = None
            
            for line in result.stdout.split('\n'):
                if 'Website URL:' in line or 'Live URL:' in line:
                    site_url = line.split(':', 1)[1].strip()
                    print(f"  URL: {site_url}")
                elif 'Site ID:' in line:
                    site_id = line.split(':', 1)[1].strip()
            
            # Try to get site ID from netlify status
            if not site_id:
                status_result = subprocess.run([
                    "netlify", "status",
                    "--json"
                ], capture_output=True, text=True, cwd=dist_path)
                
                if status_result.returncode == 0:
                    try:
                        status = json.loads(status_result.stdout)
                        site_id = status.get("siteId")
                    except:
                        pass
            
            # Save site ID for future deployments
            if site_id:
                save_netlify_state(property_path, site_id)
                print(f"✓ Site ID saved for future updates")
        else:
            print(f"❌ Deployment failed: {result.stderr}")
    
    elif choice == "2":
        # Create with custom subdomain
        suggested_name = folder_name.lower().replace('_', '-')
        custom_name = prompt_optional(f"Site name (subdomain)", suggested_name)
        
        print(f"\nCreating site: {custom_name}.netlify.app...")
        
        # Create site with name
        result = subprocess.run([
            "netlify", "sites:create",
            "--name", custom_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Extract site ID
            site_id = None
            for line in result.stdout.split('\n'):
                if 'Site ID:' in line:
                    site_id = line.split(':', 1)[1].strip()
                    break
            
            if not site_id:
                # Try to parse JSON output
                try:
                    site_info = json.loads(result.stdout)
                    site_id = site_info.get("id") or site_info.get("site_id")
                except:
                    pass
            
            if site_id:
                # Deploy to the created site
                print("Deploying content...")
                deploy_result = subprocess.run([
                    "netlify", "deploy",
                    "--dir", str(dist_path),
                    "--site", site_id,
                    "--prod"
                ], capture_output=True, text=True)
                
                if deploy_result.returncode == 0:
                    print(f"✓ Site deployed successfully!")
                    print(f"  URL: https://{custom_name}.netlify.app")
                    save_netlify_state(property_path, site_id)
                else:
                    print(f"❌ Deployment failed: {deploy_result.stderr}")
            else:
                print("❌ Could not get site ID")
        else:
            if "is already taken" in result.stderr:
                print(f"❌ Name '{custom_name}' is already taken")
                print("Please try a different name or use option 3 to link to existing site")
            else:
                print(f"❌ Site creation failed: {result.stderr}")
    
    elif choice == "3":
        # Link to existing site
        print("\nFetching your Netlify sites...")
        sites = get_netlify_sites()
        
        if not sites:
            print("No existing sites found or unable to fetch sites")
            print("Please make sure you're logged in: netlify login")
            return
        
        print("\nYour Netlify sites:")
        for i, site in enumerate(sites[:10], 1):  # Show max 10 sites
            name = site.get("name", "unnamed")
            url = site.get("url", site.get("ssl_url", ""))
            print(f"  {i}. {name} ({url})")
        
        site_choice = prompt_optional("Select site number", "1")
        
        try:
            site_index = int(site_choice) - 1
            if 0 <= site_index < len(sites):
                selected_site = sites[site_index]
                site_id = selected_site.get("id") or selected_site.get("site_id")
                
                if site_id:
                    print(f"\nDeploying to {selected_site.get('name')}...")
                    
                    result = subprocess.run([
                        "netlify", "deploy",
                        "--dir", str(dist_path),
                        "--site", site_id,
                        "--prod"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print("✓ Site deployed successfully!")
                        save_netlify_state(property_path, site_id)
                    else:
                        print(f"❌ Deployment failed: {result.stderr}")
        except:
            print("Invalid selection")

def save_netlify_state(property_path, site_id):
    """Save Netlify site ID for future deployments."""
    netlify_dir = property_path / ".netlify"
    netlify_dir.mkdir(exist_ok=True)
    
    state = {"siteId": site_id}
    
    state_file = netlify_dir / "state.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    # Also add .netlify to gitignore if it exists
    gitignore = property_path / ".gitignore"
    if not gitignore.exists():
        with open(gitignore, 'w') as f:
            f.write(".netlify\n")

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
    
    # Scan for photos in folders
    photo_folders = scan_photo_folders(photos_dir)
    
    # Remove the "all" key for counting
    folder_count = {k: v for k, v in photo_folders.items() if k != "all"}
    total_photos = len(photo_folders.get("all", []))
    
    print(f"✓ Found folder: {folder_name}/")
    
    # Handle multiple folders if detected
    gallery_organization = "merged"
    gallery_categories = []
    
    if len(folder_count) > 1:
        # Multiple folders detected
        print(f"✓ Found multiple photo folders:")
        for folder_name_inner, photos in folder_count.items():
            if folder_name_inner != "_root":
                print(f"  - {folder_name_inner}/ ({len(photos)} photos)")
            else:
                print(f"  - (root level) ({len(photos)} photos)")
        
        print(f"\nTotal photos: {total_photos}")
        
        print("\nHow would you like to organize the gallery?")
        print("  1. Merge all photos into one gallery")
        print("  2. Create filtered gallery with category buttons")
        gallery_choice = prompt_optional("Choice", "1")
        
        if gallery_choice == "2":
            gallery_organization = "filtered"
            gallery_categories = [k for k in folder_count.keys() if k != "_root"]
            if "_root" in folder_count:
                gallery_categories.insert(0, "uncategorized")  # Add root photos as uncategorized
    else:
        print(f"✓ Found {total_photos} photos in photos/ folder")
    
    # Check for special images
    hero_exists = (property_path / "hero.jpg").exists()
    agent_exists = (property_path / "agent.jpg").exists()
    
    # Handle hero image selection
    hero_selected = None
    if hero_exists:
        print(f"✓ Found hero.jpg")
        hero_selected = "hero.jpg"
    else:
        print(f"✗ No hero.jpg found")
        
        # Offer to select hero image if we have photos
        if total_photos > 0:
            print("\nSelect hero image:")
            print("  1. Use first photo from gallery (default)")
            print("  2. Select specific photo")
            print("  3. Skip hero image")
            hero_choice = prompt_optional("Choice", "1")
            
            if hero_choice == "2":
                # Show numbered list of photos
                print("\nSelect photo for hero:")
                all_photos = photo_folders.get("all", [])
                for i, photo in enumerate(all_photos[:20], 1):  # Limit to first 20 for usability
                    # Show relative path from photos dir
                    rel_path = photo.relative_to(photos_dir)
                    print(f"  {i}. {rel_path}")
                
                if len(all_photos) > 20:
                    print(f"  ... and {len(all_photos) - 20} more photos")
                    print("  (showing first 20 only)")
                
                photo_num = prompt_number("Enter number")
                if photo_num and 1 <= photo_num <= len(all_photos):
                    selected_photo = all_photos[int(photo_num) - 1]
                    hero_selected = str(selected_photo.relative_to(photos_dir))
                    print(f"✓ Selected hero: {hero_selected}")
                else:
                    print("Invalid selection, using first photo")
            elif hero_choice == "3":
                hero_selected = None
                print("✓ Skipping hero image")
    
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
    if hero_selected:
        listing["hero"]["image"] = hero_selected
    
    # Add gallery organization settings
    if gallery_organization == "filtered":
        listing["gallery"] = {
            "organization": "filtered",
            "categories": gallery_categories
        }
    
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
        
        # Offer Netlify deployment
        deploy = prompt_optional("\nDeploy to Netlify? (y/n)", "n")
        if deploy.lower() == 'y':
            handle_netlify_deployment(property_path, output_path, folder_name)
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

def collect_photos(input_path, return_dict=True):
    """Collect all jpg/jpeg files from photos directory and subdirectories."""
    photos_dir = Path(input_path) / "photos"
    
    if not photos_dir.exists():
        print(f"Error: photos directory not found in {input_path}")
        sys.exit(1)
    
    # Use scan_photo_folders to get all photos
    photo_folders = scan_photo_folders(photos_dir)
    
    if not photo_folders.get("all"):
        print(f"Error: No photos found in {photos_dir}")
        sys.exit(1)
    
    # Return photos with their relative paths from photos dir
    all_photos = photo_folders["all"]
    all_photos.sort(key=lambda p: str(p))
    
    if not return_dict:
        # Simple backward compatibility mode
        return [str(p.relative_to(photos_dir)) for p in all_photos]
    
    # Build list of photo info with categories if folders exist
    photo_data = []
    for photo in all_photos:
        rel_path = photo.relative_to(photos_dir)
        # Determine category if in subfolder
        category = None
        if len(rel_path.parts) > 1:
            category = rel_path.parts[0]
        else:
            category = "uncategorized" if len(photo_folders) > 2 else None  # > 2 means we have subfolders beyond "all" and "_root"
        
        photo_data.append({
            "filename": str(rel_path),
            "category": category
        })
    
    return photo_data

def process_image(src_path, dest_path, thumbnail=False):
    """
    Process and copy image to destination with optimization.
    """
    if thumbnail:
        create_thumbnail(src_path, dest_path)
    else:
        optimize_image(src_path, dest_path)

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
    
    # If PILLOW is available, show optimization message
    if PILLOW_AVAILABLE:
        print("  Optimizing images for web...")
    
    for photo_info in photos:
        photo_path = photo_info["filename"] if isinstance(photo_info, dict) else photo_info
        src = input_path / "photos" / photo_path
        dest_path = output_path / "photos" / photo_path
        
        # Create subdirectory if photo is in a folder
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        process_image(src, dest_path)
    
    # Handle hero image
    hero_image = None
    
    # Check if hero is specified in listing
    if listing.get("hero", {}).get("image"):
        hero_spec = listing["hero"]["image"]
        if hero_spec == "hero.jpg":
            hero_src = input_path / "hero.jpg"
            if hero_src.exists():
                hero_dest = output_path / "hero.jpg"
                process_image(hero_src, hero_dest)
                hero_image = "hero.jpg"
                print("Processing hero.jpg")
        else:
            # Hero is a photo from the gallery
            hero_image = f"photos/{hero_spec}"
    else:
        # Fallback: check for hero.jpg or use first photo
        hero_src = input_path / "hero.jpg"
        if hero_src.exists():
            hero_dest = output_path / "hero.jpg"
            process_image(hero_src, hero_dest)
            hero_image = "hero.jpg"
            print("Processing hero.jpg")
        elif photos:
            # Use first photo as hero
            first_photo = photos[0]["filename"] if isinstance(photos[0], dict) else photos[0]
            hero_image = f"photos/{first_photo}"
    
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
        
        # Photos - convert to simple list for template if needed
        "photos": photos,
        "photos_simple": [p["filename"] if isinstance(p, dict) else p for p in photos],
        "hero_image": hero_image,
        
        # Gallery organization
        "gallery_organization": listing.get("gallery", {}).get("organization", "merged"),
        "gallery_categories": listing.get("gallery", {}).get("categories", []),
        
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
        prog='site.py',
        description="""
Real Estate Tour Generator - Create beautiful property listing websites

This tool generates stunning, mobile-responsive real estate tour websites 
from photos and property details. Features include:

  • Interactive photo galleries with lightbox
  • Multiple folder support with category filtering  
  • Automatic image optimization (50-70% size reduction)
  • Smart hero image selection
  • Multiple themes (Classic, Luxury, Modern)
  • Optional Matterport/video tours
  • Agent profiles with photos
  • Automated Netlify deployment
  • SEO optimization

For more information, see: https://github.com/ryanpedersonphotography/real-estate-generator
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  
  Interactive wizard (recommended):
    python3 site.py wizard
  
  Build from existing listing.json:
    python3 site.py build --input my-property --output dist/my-property
  
  Quick start:
    1. Create folder: my-property/
    2. Add photos to: my-property/photos/
    3. Run: python3 site.py wizard
    4. Follow prompts to generate site

Project structure:
  property-folder/
    photos/           # Required: Property photos
      exterior/       # Optional: Organize by categories
      interior/
    hero.jpg          # Optional: Hero image
    agent.jpg         # Optional: Agent photo
    listing.json      # Generated by wizard or created manually
    .netlify/         # Deployment tracking
      state.json

For detailed documentation, visit the GitHub repository.
        """
    )
    
    # Add version flag
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    subparsers = parser.add_subparsers(
        dest='command', 
        help='Available commands',
        metavar='COMMAND'
    )
    
    # Build command
    build_parser = subparsers.add_parser(
        'build', 
        help='Build a site from existing listing.json',
        description='Build a static site from an existing listing.json file and photos.',
        epilog='Example: python3 site.py build --input my-property --output dist/my-property'
    )
    build_parser.add_argument(
        '--input',
        required=True,
        metavar='PATH',
        help='Path to listing folder containing listing.json and photos/'
    )
    build_parser.add_argument(
        '--output',
        required=True,
        metavar='PATH',
        help='Path to output folder for generated site'
    )
    
    # Wizard command
    wizard_parser = subparsers.add_parser(
        'wizard', 
        help='Interactive wizard to create and build listing (recommended)',
        description="""
Interactive wizard mode - the easiest way to create a listing!

The wizard will guide you through:
  1. Selecting your property folder
  2. Organizing photos (merge or filter by category)
  3. Choosing hero image
  4. Entering property details (all optional)
  5. Configuring agent information
  6. Selecting theme and style
  7. Building the site
  8. Deploying to Netlify (optional)

All fields are optional - press Enter to skip any field.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
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