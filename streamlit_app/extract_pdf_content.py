import PyPDF2
import sys

def extract_pdf_text(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

if __name__ == "__main__":
    pdf_path = "/Users/manjunaths/upwork/Olympus_Analytics_CO1.pdf"
    content = extract_pdf_text(pdf_path)
    print(content)