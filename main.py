import yaml
from pathlib import Path
import argparse

from blocks.folder import Folder

SUPPORTED_FOLDERS = {
    'Folder': Folder
}

def load_config(config_path):
    config_path = Path(config_path).resolve()
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)

    root = Path(cfg['root']).resolve()
    image_folder = root / cfg['image']
    annotation_folder = root / cfg['annotation']

    output_raw = cfg.get('output', '').strip()
    output_path = None

    if output_raw:
        output = Path(output_raw)
        if output.is_absolute() or output.parts[0] in {'.', '..'}:
            output_path = output.resolve()
        else:
            output_path = root / output

    folder_type = cfg.get("folder_type", "Folder")
    recursive = cfg.get("recursive_image_folder", True)

    return {
        'folder_type': folder_type,
        'recursive': recursive,
        'image_folder': image_folder,
        'annotation_folder': annotation_folder,
        'output_folder': output_path,
        'annotation_format': cfg.get('format', 'xywhc')  # fallback if not present
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize image annotations from a config YAML.")
    parser.add_argument("-c", "--config", type=str, required=True, help="Path to the YAML config file")
    args = parser.parse_args()
    
    config = load_config(args.config)
    folder_type = SUPPORTED_FOLDERS.get(config['folder_type'], Folder)
    folder = folder_type(**config)
    folder.annotate_images()
