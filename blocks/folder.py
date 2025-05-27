import csv
import json
from pathlib import Path
from PIL import Image

from blocks.annotations import Annotation

from draw_utils import annotate_image
from tqdm import tqdm


class Folder:
    """
    Generic Folder class to ingest a folder that contains images and annotations. Supports YOLO and COCO format out of the box.
    At the core, this class looks to create the image-annotation pairs for later use / visualization mainly.

    Inherit Folder and edit _ingest_images or _ingest_annotations to support other annotation formats.
    """
    IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.ppm', '.pgm', '.ico']
    ANNOTATION_FORMATS = ['.txt', '.json', '.csv', '.xml']

    def __init__(self, image_folder, annotation_folder, annotation_format, output_folder=None, recursive=True):
        self.image_folder = Path(image_folder)
        self.annotation_folder = Path(annotation_folder)
        self.output_folder = Path(output_folder) if output_folder else None
        self.annotation_format = annotation_format
        self.recursive = recursive
        self.image_annotations = {}  # image_path: [annotations]
        print("Loading images")
        self._ingest_images()
        print("Loading annotations")
        self._ingest_annotations()
        print("Loaded folder!")

    def annotate_images(self):
        """
        Visualizes the images with annotations. 
        """
        if self.output_folder is None:
            print("No output folder set, returning!")
            return
        
        for img_path, annotations in tqdm(self.image_annotations.items(), desc="Annotating images"):
            # if annotations is None:
            #     continue

            relative_path = img_path.relative_to(self.image_folder)
            output_path = self.output_folder / relative_path

            annotate_image(img_path, annotations, output_path)

    def _ingest_images(self):
        """
        Consumes the images in the image folder. Recursively grabs the images to support file structure with class level distinction.
        TODO: Support or compare with COCO json if present.
        """
        search_iter = self.image_folder.rglob("*") if self.recursive else self.image_folder.glob("*")
        for img_file in search_iter:
            if img_file.suffix.lower() in self.IMAGE_FORMATS:
                self.image_annotations[img_file] = None

    def _ingest_annotations(self):
        """
        Detects if we have a single file like json, csv or txt, or a per-image annotations, and applies parsing appropriately.
        """
        
        if self.annotation_folder.is_file():
            annot_files = [self.annotation_folder]
        else:
            annot_files = list(self.annotation_folder.glob("*"))

        if len(annot_files) == 1:
            file = annot_files[0]
            if file.suffix == '.json':
                self._parse_coco_json(file)
            elif file.suffix in ['.csv', '.txt']:
                self._parse_flat_annotations(file)
        else:
            # Multiple annotation files — assume image-paired
            for ann_file in tqdm(annot_files, desc="Loading annotations"):
                if ann_file.suffix.lower() in self.ANNOTATION_FORMATS:
                    img_name = ann_file.stem
                    for img_path in self.image_annotations:
                        if img_path.stem == img_name:
                            self.image_annotations[img_path] = self._parse_single_file_annotation(ann_file, img_path)
                            break

    def _parse_flat_annotations(self, file):
        with open(file, newline='') as f:
            reader = csv.reader(f, delimiter=',' if file.suffix == '.csv' else None)
            for row in reader:
                if len(row) < 6:
                    continue
                filename, x, y, w, h, cls = row[:6]
                img_path = next((p for p in self.image_annotations if p.name == filename), None)
                if img_path:
                    ann = Annotation([float(x), float(y), float(w), float(h), cls], a_type=self.annotation_format)
                    if self.image_annotations[img_path] is None:
                        self.image_annotations[img_path] = []
                    self.image_annotations[img_path].append(ann)

    def _parse_single_file_annotation(self, ann_file, img_path=None):
        anns = []
        width, height = Image.open(img_path).size if 'n' in self.annotation_format else (1, 1)
        with open(ann_file) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
                cls = parts[0]
                x, y, w, h = map(float, parts[1:5])
                confidence = float(parts[5]) if len(parts) > 5 else None

                if 'n' in self.annotation_format:
                    x *= width
                    w *= width
                    y *= height
                    h *= height

                values = [x, y, w, h]
                if self.annotation_format.endswith('c'):
                    values.append(cls)
                if self.annotation_format.endswith('cc') and confidence is not None:
                    values.append(confidence)

                anns.append(Annotation(values, a_type=self.annotation_format))
        return anns

    def _parse_coco_json(self, file):
        with open(file) as f:
            data = json.load(f)

        id_to_filename = {img['id']: img['file_name'] for img in data['images']}
        anns_by_filename = {}

        for ann in data['annotations']:
            bbox = ann['bbox']  # [x, y, w, h]
            image_id = ann['image_id']
            category_id = ann.get('category_id', None)
            filename = id_to_filename[image_id]
            anns_by_filename.setdefault(filename, []).append(
                Annotation(bbox + [category_id], a_type=self.annotation_format)
            )

        for img_path in self.image_annotations:
            anns = anns_by_filename.get(img_path.name)
            if anns:
                self.image_annotations[img_path] = anns