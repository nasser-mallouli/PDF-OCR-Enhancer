import difflib

from easyOcrClass import EasyOCRPDFExtractor
from pdfMiner import PDFMinerTextExtractor


class OCRTextCombiner:
    def merge_ocr_texts(self, easyocr_texts, pdfminer_texts, update_keywords):
        def calculate_similarity(text1, text2):
            return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

        merged_texts = {}

        for page_number in easyocr_texts.keys():
            if page_number not in pdfminer_texts:
                merged_texts[page_number] = easyocr_texts[page_number]
                continue

            easyocr_lines = easyocr_texts[page_number].split("\n")
            pdfminer_lines = pdfminer_texts[page_number].split("\n")

            combined_lines = []

            for easyocr_line in easyocr_lines:
                replaced = False

                # Check for keyword matches
                for keyword in update_keywords:
                    if calculate_similarity(easyocr_line, keyword) > 0.8:
                        for pdfminer_line in pdfminer_lines:
                            if calculate_similarity(pdfminer_line, keyword) > 0.8:
                                combined_lines.append(pdfminer_line)
                                replaced = True
                                break
                        if replaced:
                            break

                # Check for lines ending with "( -"
                if not replaced and easyocr_line.strip().endswith("( -"):
                    for pdfminer_line in pdfminer_lines:
                        if calculate_similarity(easyocr_line, pdfminer_line) > 0.8:
                            combined_lines.append(pdfminer_line)
                            replaced = True
                            break

                # If no replacement was made, keep the original EasyOCR line
                if not replaced:
                    combined_lines.append(easyocr_line)

            merged_texts[page_number] = "\n".join(combined_lines)

        return merged_texts

    def extract_and_merge_texts(self, pdf_file_path, update_keywords):
        # Implement EasyOCR processing
        easyocr_extractor = EasyOCRPDFExtractor()
        easyocr_result = easyocr_extractor.extract_text_from_pdf(pdf_file_path)

        # Implement PDFMiner processing
        pdfminer_parser = PDFMinerTextExtractor(pdf_file_path)
        pdfminer_parser.extract_text()
        pdfminer_result = pdfminer_parser.get_text_by_page()

        # Combine results using the merge method
        return self.merge_ocr_texts(easyocr_result, pdfminer_result, update_keywords)


def main():
    # Phrases which we want to update in EasyOCR (from PDFMiner results)
    update_keywords = [
        "Umklemmbar tappings",
        "Betriebsanzeige operating indicator",
        "Restwelligkeit ripple",
    ]

    pdf_file_path = "866053_DB_2_a.pdf"
    ocr_combiner = OCRTextCombiner()
    text_by_page = ocr_combiner.extract_and_merge_texts(pdf_file_path, update_keywords)

    # Print all pages
    for page_number, text in text_by_page.items():
        print(f"{page_number}:\n{text}\n")


# if __name__ == "__main__":
#     main()
