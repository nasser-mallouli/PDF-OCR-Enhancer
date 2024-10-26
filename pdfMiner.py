from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTTextLineHorizontal
import re


class PDFMinerTextExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.text_by_page = {}

    def extract_text(self):
        try:
            for page_number, page_layout in enumerate(
                extract_pages(self.file_path), start=1
            ):
                text_elements = []

                for element in page_layout:
                    if isinstance(element, LTTextBoxHorizontal):
                        for line in element:
                            if isinstance(line, LTTextLineHorizontal):
                                text = line.get_text().strip()
                                bbox = line.bbox  # (x0, y0, x1, y1)
                                text_elements.append({"text": text, "bbox": bbox})

                ordered_text = self._arrange_text_elements(text_elements)
                self.text_by_page[f"page{page_number}"] = ordered_text

        except Exception as e:
            print(f"Error processing PDF: {e}")

    def _arrange_text_elements(self, text_elements, y_threshold=5):
        try:
            # Sort by y1 descending, then x0 ascending
            text_elements.sort(key=lambda x: (-x["bbox"][3], x["bbox"][0]))

            ordered_text = []
            current_line = []
            current_y = None

            for element in text_elements:
                bbox = element["bbox"]
                text = self._clean_text(element["text"])

                if current_y is None or abs(bbox[3] - current_y) > y_threshold:
                    if current_line:
                        ordered_text.append(" ".join(current_line))
                    current_line = [text]
                    current_y = bbox[3]
                else:
                    current_line.append(text)

            if current_line:
                ordered_text.append(" ".join(current_line))

            return "\n".join(ordered_text)

        except Exception as e:
            print(f"Error arranging text: {e}")
            return ""

    def _clean_text(self, text):
        cleaned_text = re.sub(r"^\b[a-zA-Z]\b", "", text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text)
        return cleaned_text.strip()

    def get_text_by_page(self):
        return self.text_by_page


def main():
    pdf_file_path = "866053_DB_2_a.pdf"
    text_extractor = PDFMinerTextExtractor(pdf_file_path)
    text_extractor.extract_text()
    text_by_page = text_extractor.get_text_by_page()

    # Print all pages
    for page, text in text_by_page.items():
        print(f"{page}:\n{text}\n")


# if __name__ == "__main__":
#     main()
