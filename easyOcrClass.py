import easyocr
import cv2
from pdf2image import convert_from_path
from io import BytesIO
import numpy as np
import subprocess
import torch


class EasyOCRPDFExtractor:
    def __init__(self, languages=["en", "de"]):
        self.gpu_info = self._check_gpu_availability()
        try:
            self.reader = easyocr.Reader(languages, gpu=True) if self.gpu_info.get("gpu_available", False) is True else easyocr.Reader(languages) 
            if self.gpu_info.get("gpu_available", False):
                print("GPU is being used for EasyOCR")
            else:
                print("CPU is being used for EasyOCR")
        except RuntimeError as e:
            print(f"Error initializing EasyOCR with GPU: {e}")
            print("Falling back to CPU")
            self.gpu_info["gpu_available"] = False
            self.reader = easyocr.Reader(languages, gpu=False)

    def _check_gpu_availability(self):
        gpu_info = {
            "gpu_available": False,
            "cuda_available": False,
            "gpu_name": None,
            "gpu_memory": None,
            "error": None,
        }

        # Check if CUDA is available through PyTorch
        gpu_info["cuda_available"] = torch.cuda.is_available()

        try:
            # Try to get GPU information using nvidia-smi
            output = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                universal_newlines=True,
            )
            output = output.strip().split(",")
            if len(output) >= 2:
                gpu_info["gpu_name"] = output[0].strip()
                gpu_info["gpu_memory"] = output[1].strip()
                gpu_info["gpu_available"] = True
        except subprocess.CalledProcessError as e:
            gpu_info["error"] = f"nvidia-smi command failed: {e}"
        except FileNotFoundError:
            gpu_info["error"] = (
                "nvidia-smi not found. NVIDIA GPU driver might not be installed."
            )
        except Exception as e:
            gpu_info["error"] = f"Unexpected error checking GPU: {e}"

        # If CUDA is available but nvidia-smi failed, we still consider GPU as available
        if gpu_info["cuda_available"] and not gpu_info["gpu_available"]:
            gpu_info["gpu_available"] = True
            if not gpu_info["error"]:
                gpu_info["error"] = (
                    "CUDA is available, but couldn't get detailed GPU info."
                )

        return gpu_info

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
    print(f"GPU available: {ocr_extractor.gpu_info}")
    text_by_page = ocr_extractor.extract_text_from_pdf(pdf_file_path)

    # Print all pages
    for page_number, text in text_by_page.items():
        print(f"{page_number}:\n{text}\n")


# if __name__ == "__main__":
#     main()
