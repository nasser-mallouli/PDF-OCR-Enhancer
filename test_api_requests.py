# test_api_requests.py

import requests
import json
import os


class TestAPIRequests:
    def __init__(self, base_url="http://0.0.0.0:8000"):
        self.base_url = base_url
        self.default_keywords = [
            "Umklemmbar tappings",
            "Betriebsanzeige operating indicator",
            "Restwelligkeit ripple",
        ]

    def test_process_pdf_default_keywords(self, pdf_path):
        """Test PDF processing with default keywords"""
        url = f"{self.base_url}/process_pdf"

        files = {
            "file": (
                os.path.basename(pdf_path),
                open(pdf_path, "rb"),
                "application/pdf",
            )
        }
        data = {"keywords": json.dumps(self.default_keywords)}

        response = requests.post(url, files=files, data=data)
        return response.json()

    def test_process_pdf_custom_keywords(self, pdf_path, custom_keywords):
        """Test PDF processing with custom keywords"""
        url = f"{self.base_url}/process_pdf"

        files = {
            "file": (
                os.path.basename(pdf_path),
                open(pdf_path, "rb"),
                "application/pdf",
            )
        }
        data = {"keywords": json.dumps(custom_keywords)}

        response = requests.post(url, files=files, data=data)
        return response.json()


def main():
    # Initialize the test class
    api_tester = TestAPIRequests()
    pdf_path = "866053_DB_2_a.pdf"  # Replace with your PDF path

    # Test 1: Default keywords
    print("\nTest 1: Default keywords")
    result = api_tester.test_process_pdf_default_keywords(pdf_path)
    print(json.dumps(result, indent=2))

    # Test 2: Custom keywords
    print("\nTest 2: Custom keywords")
    custom_keywords = ["Custom keyword 1", "Custom keyword 2", "Custom keyword 3"]
    result = api_tester.test_process_pdf_custom_keywords(pdf_path, custom_keywords)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
