from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import io

print("Loading PaddleOCR engine (first run downloads models ~500MB)...")

_ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en",
    show_log=False
)

print("PaddleOCR ready")


def extract_text_from_image(image_bytes: bytes) -> str:
    try:
        pil_img = Image.open(io.BytesIO(image_bytes))

        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        img_array = np.array(pil_img)

        result = _ocr.ocr(img_array, cls=True)

        lines = []

        if result:
            for detection in result[0]:
                text = detection[1][0]
                confidence = detection[1][1]

                if confidence >= 0.5:
                    lines.append(text)

        if not lines:
            return "Could not read text from this image."

        return " ".join(lines).strip()

    except Exception as e:
        return f"OCR error: {str(e)}"