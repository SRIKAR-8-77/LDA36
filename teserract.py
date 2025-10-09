import pymupdf as fitz  # PyMuPDF library
import os

def ocr_from_pdf(pdf_path: str) -> str:
    """
    Extracts text directly from a PDF file using FitZ (PyMuPDF).
    This function extracts text from both text-based PDFs and can handle basic layouts.
    
    If the PDF is a scanned image, this function will return very little or no text.
    """
    full_text = ""
    
    try:
        print(f"Opening PDF document at {pdf_path}...")
        # Open the PDF document
        document = fitz.open(pdf_path)
        
        if document.page_count == 0:
            return "Could not open document or document has no pages."

        print(f"Extracting text from {document.page_count} pages...")
        
        for i in range(document.page_count):
            page = document.load_page(i)
            
            # Extract text from the page
            page_text = page.get_text("text") 
            
            full_text += f"--- Page {i + 1} ---\n" + page_text + "\n\n"
            
        document.close()
        
        if not full_text.strip():
             return "No readable text found. Document may be a scanned image."

        return full_text

    except fitz.FileNotFoundError:
        return f"An error occurred: PDF file not found at {pdf_path}"
    except Exception as e:
        return f"An unknown error occurred during PDF processing: {e}"
