# file_parser.py

import docx
import fitz  # PyMuPDF library

def extract_text_from_docx(file_stream):
    """Reads text content from a .docx file stream."""
    try:
        doc = docx.Document(file_stream)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error reading DOCX file: {e}")
        return None

def extract_text_from_pdf(file_stream):
    """
    Reads text from a .pdf file stream using PyMuPDF, preserving the reading order.
    """
    try:
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        all_text = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Use a more robust sorting method to handle multi-column layouts if necessary
            blocks = page.get_text("dict", sort=True)["blocks"]
            page_text = []
            for block in blocks:
                if 'lines' in block:
                    for line in block['lines']:
                        line_text = "".join([span['text'] for span in line['spans']])
                        page_text.append(line_text)
            all_text.append("\n".join(page_text))
        return "\n\n".join(all_text) # Separate pages by double newline
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None

def read_uploaded_file(uploaded_file):
    """Dispatcher function to read text from either a PDF or DOCX file."""
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    return None