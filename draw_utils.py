import cv2

COLORS = {
    'r': (0, 0, 255),
    'g': (0, 255, 0),
    'b': (255, 0, 0),
}

def draw_box(image, class_id, *annotation, color='r'):
    color = COLORS.get(color.lower(), (0, 0, 255))
    thickness = 2

    x_min, y_min, x_max, y_max = map(int, annotation)
    label = f"Class {class_id}"

    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color, thickness)
    cv2.putText(image, label, (x_min, y_min - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
    return image

def annotate_image(image_path, annotations, output_path):
    image = cv2.imread(str(image_path))

    annotations = [] if annotations is None else annotations
    for ann in annotations:
        x1, y1, x2, y2 = ann.to('xyxy')
        image = draw_box(image, ann._class, x1, y1, x2, y2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)
