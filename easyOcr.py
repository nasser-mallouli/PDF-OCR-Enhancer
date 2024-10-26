import easyocr
import cv2
import tempfile
from pdf2image import convert_from_path
from io import BytesIO
import numpy as np


class EasyOCRPDFExtractor:
    def __init__(self, languages=["en", "de"]):
        self.reader = easyocr.Reader(languages)

    def _arrange_text_elements(self, detections, y_threshold=10):
        # Sort detections by their y position (top to bottom)
        detections.sort(key=lambda x: (x[0][0][1], x[0][0][0]))

        arranged_text = []
        current_line = []
        current_y = None

        for detection in detections:
            bbox, text, _ = detection
            top_y = min(point[1] for point in bbox)
            left_x = min(point[0] for point in bbox)

            # Start a new line if the y-coordinate difference exceeds the threshold
            if current_y is None or abs(top_y - current_y) > y_threshold:
                if current_line:
                    # Sort the current line's text elements by their x position (left to right)
                    current_line.sort(key=lambda x: x[1])
                    arranged_text.append(" ".join([word[0] for word in current_line]))
                current_line = [(text, left_x)]
                current_y = top_y
            else:
                # Add text to the current line
                current_line.append((text, left_x))

        # Append the last line
        if current_line:
            current_line.sort(key=lambda x: x[1])  # Sort by x position
            arranged_text.append(" ".join([word[0] for word in current_line]))

        return "\n".join(arranged_text)

    def extract_text_from_pdf(self, pdf_file_path):
        text_by_page = {}
        images = convert_from_path(pdf_file_path)

        for i, image in enumerate(images):
            image_bytes = BytesIO()
            image.save(image_bytes, format="JPEG")
            image_bytes.seek(0)

            image_np = np.frombuffer(image_bytes.read(), np.uint8)
            img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

            result = self.reader.readtext(img)
            ordered_text = self._arrange_text_elements(result)

            text_by_page[f"page{i + 1}"] = ordered_text

        return text_by_page


def main():
    pdf_file_path = "866053_DB_2_a.pdf"
    ocr_extractor = EasyOCRPDFExtractor()
    text_by_page = ocr_extractor.extract_text_from_pdf(pdf_file_path)

    # Print all pages
    for page_number, text in text_by_page.items():
        print(f"{page_number}:\n{text}\n")


if __name__ == "__main__":
    main()
