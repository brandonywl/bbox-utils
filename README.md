# Visualisation Utils

## Out of the box works for COCO and YOLO annotated datasets. 
Works with annotation formats xywh, cxcywhn, and inclusion of class and confidence. xywh and ltwh are treated as equivalent.

## Supporting other annotation types
Inherit from the Folder class and manipulate the _ingest_images and _ingest_annotations function to fit your annotation format.

## Using your dataset
Update the data.yaml to include root (main directory for the data), image (relative path to root where the images exist), annotation (relative path to the annotation file or folder containing the annotations), and output (include ./ or ../ to have relative pathing to the cwd, or drop the ./ or ../ to have relative to the root, or absolute pathing).

## Visualizing

Run from the root directory of the project.

```
python main.py -c cfg/data.yaml
```


## TODOs:
From the folder and annotations, can export the folder into another annotation format (i.e. COCO/YOLO)
