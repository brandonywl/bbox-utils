from collections.abc import Sequence

class Annotation(Sequence):
    ANNOTATION_FORMATS = [
        'xyxy', 'ltrb',
        'yxyx', 'tlbr',
        'xywh', 'ltwh',
        'yxwh', 'tlwh',
        'cxcywh', 'cycxwh'
    ]

    def __init__(self, annotation, a_type='xyxy', class_map=None):
        self.class_map = class_map or {}
        self._class = None
        self.confidence = None

        # Extract base format
        if a_type.endswith('cc'):
            fmt, has_conf = a_type[:-2], True
        elif a_type.endswith('c'):
            fmt, has_conf = a_type[:-1], False
        else:
            fmt, has_conf = a_type, False

        if fmt.endswith('n'):
            fmt = fmt[:-1]

        if fmt not in self.ANNOTATION_FORMATS:
            raise ValueError(f"Unknown annotation format: {a_type}")

        # Pad and assign annotation
        coords = annotation[:4]
        if len(annotation) > 4:
            self._class = annotation[4]
        if has_conf and len(annotation) > 5:
            self.confidence = annotation[5]

        self._xyxy = self._convert_to_xyxy(coords, fmt)

    def __getitem__(self, idx):
        return self._xyxy[idx]

    def __len__(self):
        return 4

    def __iter__(self):
        return iter(self._xyxy)

    def __repr__(self):
        base = f"Annotation(xyxy={self._xyxy}"
        if self._class is not None:
            base += f", class={self._class}"
        if self.confidence is not None:
            base += f", conf={self.confidence:.2f}"
        return base + ")"

    def to(self, fmt='xyxy'):
        if fmt == 'xyxy':
            return self._xyxy
        elif fmt == 'xywh':
            x1, y1, x2, y2 = self._xyxy
            return (x1, y1, x2 - x1, y2 - y1)
        elif fmt == 'cxcywh':
            x1, y1, x2, y2 = self._xyxy
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            w = x2 - x1
            h = y2 - y1
            return (cx, cy, w, h)
        elif fmt == 'yxyx':
            x1, y1, x2, y2 = self._xyxy
            return (y1, x1, y2, x2)
        else:
            raise NotImplementedError(f"Conversion to {fmt} not implemented.")

    def _convert_to_xyxy(self, coords, fmt):
        if fmt in ['xyxy', 'ltrb']:
            return tuple(coords)
        elif fmt in ['yxyx', 'tlbr']:
            y1, x1, y2, x2 = coords
            return (x1, y1, x2, y2)
        elif fmt in ['xywh', 'ltwh']:
            x, y, w, h = coords
            return (x, y, x + w, y + h)
        elif fmt in ['yxwh', 'tlwh']:
            y, x, w, h = coords
            return (x, y, x + w, y + h)
        elif fmt == 'cxcywh':
            cx, cy, w, h = coords
            x1 = cx - w / 2
            y1 = cy - h / 2
            x2 = cx + w / 2
            y2 = cy + h / 2
            return (x1, y1, x2, y2)
        elif fmt == 'cycxwh':
            cy, cx, w, h = coords
            x1 = cx - w / 2
            y1 = cy - h / 2
            x2 = cx + w / 2
            y2 = cy + h / 2
            return (x1, y1, x2, y2)
        else:
            raise NotImplementedError(f"Conversion from {fmt} not implemented.")
        

if __name__ == "__main__":
    a = Annotation([1, 2, 3, 4, 5], 'xyxyc')
    print(*a)
    pass