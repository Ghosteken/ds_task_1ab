import os


class OCRService:
    def __init__(self):
        self._configured = False
        cmd = os.getenv("TESSERACT_CMD")
        try:
            import pytesseract
            if cmd:
                pytesseract.pytesseract.tesseract_cmd = cmd
            self._configured = True
        except Exception:
            self._configured = False

    def extract_text(self, image_path: str) -> str:
        try:
            import importlib
            from PIL import Image
            pyt = importlib.import_module("pytesseract")
            img = Image.open(image_path)
            text = pyt.image_to_string(img)
            return text.strip()
        except Exception:
            return ""
