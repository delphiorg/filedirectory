import os
import yaml
import logging
import subprocess
from datetime import datetime

# --- Configuration ---
REPO_ROOT = "."
DATA_FILE = "_meta/files.yml"
README_FILE = "README.md"
HEADER = "# Delphi.org File Directory"
SUBHEADER = """These are old file downloads I was hosting on [Delphi.org](https://delphi.org/). 
  I believe a few of these were intended to be temporary, so I will be pruning them over time, 
  and adding new ones from time to time. You can also view the [directory on GitHub](https://github.com/delphiorg/filedirectory).
  """

INITIAL_COMMIT_CUTOFF = datetime(2025, 11, 25)

# Files to ignore
IGNORE = {'.git', '.github', '_site', '_data', '_meta', '_config.yml', 
          'scripts', 'Gemfile', 'Gemfile.lock', 'README.md', 'index.md'}

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_file_size(path):
    """Returns human readable file size."""
    try:
        size_bytes = os.path.getsize(path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
    except OSError as e:
        logger.error(f"Error reading size for {path}: {e}")
        return "N/A"

def get_git_date(path):
    """Gets the last commit date for a specific file."""
    try:
        # Get ISO-8601 date from git log for the specific file
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%cd', '--date=iso-strict', path],
            capture_output=True, text=True, check=True
        )
        date_str = result.stdout.strip()
        if date_str:
            # Parse ISO format (handling timezone offset if present)
            # Python 3.7+ handles isoformat nicely
            return datetime.fromisoformat(date_str).replace(tzinfo=None) # naive comparison
    except Exception as e:
        logger.warning(f"Could not get git date for {path}: {e}")
    return None

def main():
    logger.info("Starting sync process...")

    # 1. Load existing manifest
    if os.path.exists(DATA_FILE):
        logger.info(f"Loading existing manifest from {DATA_FILE}")
        with open(DATA_FILE, 'r') as f:
            manifest = yaml.safe_load(f) or []
    else:
        logger.info("No existing manifest found. Creating new one.")
        manifest = []

    manifest_dict = {item['filename']: item for item in manifest}
    
    # 2. Scan Directory
    current_files = set()
    logger.info(f"Scanning directory: {REPO_ROOT}")
    
    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip hidden/ignored dirs
        dirs[:] = [d for d in dirs if d not in IGNORE and not d.startswith('.')]
        
        for file in files:
            if file in IGNORE or file.startswith('.'): continue
            
            rel_path = os.path.relpath(os.path.join(root, file), REPO_ROOT)
            current_files.add(rel_path)
            
            size = get_file_size(rel_path)
            
            # Check git history
            git_date = get_git_date(rel_path)
            display_date = None
            
            if git_date and git_date > INITIAL_COMMIT_CUTOFF:
                display_date = git_date.strftime("%Y-%m-%d")
                # logger.info(f"File {file} is new/updated: {display_date}")
            
            if rel_path in manifest_dict:
                # Update existing entry
                manifest_dict[rel_path]['active'] = True
                manifest_dict[rel_path]['size'] = size
                if display_date:
                    manifest_dict[rel_path]['updated'] = display_date
            else:
                # Add new entry
                logger.info(f"Found new file: {rel_path}")
                manifest_dict[rel_path] = {
                    'filename': rel_path,
                    'size': size,
                    'description': "",
                    'active': True,
                    'updated': display_date
                }

    # 3. Handle Deletions
    for fname, data in manifest_dict.items():
        if fname not in current_files:
            if data.get('active'):
                logger.info(f"Marking missing file as inactive: {fname}")
                
            if data.get('description'):
                data['active'] = False
            else:
                data['delete_me'] = True

    # Rebuild list
    final_manifest = [
        data for data in manifest_dict.values() 
        if not data.get('delete_me')
    ]
    final_manifest.sort(key=lambda x: x['filename'])

    # 4. Save Manifest
    logger.info(f"Saving manifest with {len(final_manifest)} entries.")
    with open(DATA_FILE, 'w') as f:
        yaml.dump(final_manifest, f, sort_keys=False)

    # 5. Generate Markdown
    md_lines = [
        # HEADER, 
        # "",
        SUBHEADER,
        "", 
        "| File | Size | Updated | Description |", 
        "|---|---|---|---|"
    ]
    
    for item in final_manifest:
        name = item['filename']
        desc = item.get('description', '')
        size = item['size']
        updated = item.get('updated') or "" # Defaults to empty string if None
        
        if item['active']:
            # Relative link for direct download/view
            link = f"[{name}]({name})" 
            md_lines.append(f"| {link} | {size} | {updated} | {desc} |")
        else:
            md_lines.append(f"| ~~{name}~~ | N/A | {updated} | {desc} (Deleted) |")

    logger.info(f"Writing index to {README_FILE}")
    with open(README_FILE, 'w') as f:
        f.write("\n".join(md_lines))
    
    logger.info("Sync complete.")

if __name__ == "__main__":
    main()