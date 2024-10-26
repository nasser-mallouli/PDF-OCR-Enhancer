import tempfile
import os
from baseOCRProcessor import OCRTextCombiner
from easyOcr import EasyOCRPDFExtractor
from fastapi import FastAPI, File, UploadFile, Response, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pdfMiner import PDFMinerTextExtractor
import uvicorn
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_KEYWORDS = [
    "Umklemmbar tappings",
    "Betriebsanzeige operating indicator",
    "Restwelligkeit ripple",
]


@app.get("/", tags=["Root"])
async def root():
    """Redirects the user to the API documentation."""
    return Response(
        status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/docs"}
    )


@app.post("/process_pdf", tags=["OCR"])
async def process_pdf(
    file: UploadFile = File(...), keywords: str = Form(json.dumps(DEFAULT_KEYWORDS))
):
    """
    Process a PDF file using OCR and return the extracted text by page.

    - **file**: PDF file to process
    - **keywords**: JSON string containing list of keywords to update
    """
    try:
        # Parse the keywords JSON string
        try:
            update_keywords = json.loads(keywords)
            if not isinstance(update_keywords, list):
                update_keywords = DEFAULT_KEYWORDS
        except json.JSONDecodeError:
            update_keywords = DEFAULT_KEYWORDS

        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(await file.read())
            temp_pdf_path = temp_pdf.name

        # Create an instance of the OCRTextCombiner
        ocr_combiner = OCRTextCombiner()
        text_by_page = ocr_combiner.extract_and_merge_texts(
            temp_pdf_path, update_keywords
        )

        # Convert the result to a format suitable for JSON response
        result = {str(page): text for page, text in text_by_page.items()}

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": str(e)}
        )
    finally:
        # Clean up the temporary file
        if "temp_pdf_path" in locals():
            os.unlink(temp_pdf_path)


@app.post("/process-pdf-easyocr", tags=["OCR"])
async def process_pdf_easyocr(file: UploadFile = File(...)):
    """
    Process a PDF file with text arrangement (in reading order).
    """
    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        # Process the PDF with text arrangement
        ocr_extractor = EasyOCRPDFExtractor()
        text_by_page = ocr_extractor.extract_text_from_pdf(temp_file_path)

        # Clean up the temporary file
        os.unlink(temp_file_path)

        return JSONResponse(content={"text_by_page": text_by_page})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/process-pdf-pdfminer", tags=["OCR"])
async def process_pdf_pdfminer(file: UploadFile = File(...)):
    """
    Process a PDF file with text arrangement (in reading order).
    """
    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        # Process the PDF with text arrangement
        text_extractor = PDFMinerTextExtractor(temp_file_path)
        text_extractor.extract_text()
        text_by_page = text_extractor.get_text_by_page()

        # Clean up the temporary file
        os.unlink(temp_file_path)

        return JSONResponse(content={"text_by_page": text_by_page})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
