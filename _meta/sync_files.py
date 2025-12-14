import os
import yaml # Requires PyYAML
from datetime import datetime

# Config
REPO_ROOT = "."
DATA_FILE = "_meta/files.yml"
README_FILE = "README.md"
# Files to ignore
IGNORE = {'.git', '.github', '_site', '_data', '_meta', '_config.yml', 'scripts', 'Gemfile', 'Gemfile.lock', 'README.md', 'index.md'}

def get_file_info(path):
    size_bytes = os.path.getsize(path)
    # Convert to readable format
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def main():
    # 1. Load existing manifest
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            manifest = yaml.safe_load(f) or []
    else:
        manifest = []

    # Convert manifest to dict for easy lookup
    manifest_dict = {item['filename']: item for item in manifest}
    
    # 2. Scan Directory
    current_files = set()
    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip hidden/ignored dirs
        dirs[:] = [d for d in dirs if d not in IGNORE and not d.startswith('.')]
        
        for file in files:
            if file in IGNORE or file.startswith('.'): continue
            
            # Get relative path if you use subfolders, otherwise just filename
            rel_path = os.path.relpath(os.path.join(root, file), REPO_ROOT)
            current_files.add(rel_path)
            
            size = get_file_info(rel_path)
            
            if rel_path in manifest_dict:
                # Update existing entry
                manifest_dict[rel_path]['active'] = True
                manifest_dict[rel_path]['size'] = size
            else:
                # Add new entry
                manifest_dict[rel_path] = {
                    'filename': rel_path,
                    'size': size,
                    'description': "",
                    'active': True
                }

    # 3. Handle Deletions (Files in manifest but not on disk)
    for fname, data in manifest_dict.items():
        if fname not in current_files:
            # If it has a description, keep it but mark inactive
            if data.get('description'):
                data['active'] = False
            else:
                # If no description and no file, remove from manifest completely
                data['delete_me'] = True

    # Rebuild list and sort
    final_manifest = [
        data for data in manifest_dict.values() 
        if not data.get('delete_me')
    ]
    final_manifest.sort(key=lambda x: x['filename'])

    # 4. Save Manifest back to disk
    with open(DATA_FILE, 'w') as f:
        yaml.dump(final_manifest, f, sort_keys=False)

    # 5. Generate Markdown Content
    md_lines = ["# File Directory", "", "| File | Size | Description |", "|---|---|---|"]
    
    for item in final_manifest:
        name = item['filename']
        desc = item.get('description', '')
        size = item['size']
        
        if item['active']:
            link = f"[{name}]({name})" 
            md_lines.append(f"| {link} | {size} | {desc} |")
        else:
            # Strikethrough for deleted
            md_lines.append(f"| ~~{name}~~ | N/A | {desc} (Deleted) |")

    # Write to README.md
    with open(README_FILE, 'w') as f:
        f.write("\n".join(md_lines))

if __name__ == "__main__":
    main()