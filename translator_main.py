import fitz  # PyMuPDF
import easyocr
from deep_translator import GoogleTranslator

# FIX FOR PYTHON 3.13 'cgi'
try:
    import cgi
except ImportError:
    import sys, legacy_cgi
    sys.modules['cgi'] = legacy_cgi

def overlay_translation(input_pdf, output_pdf):
    # 1. Initialize
    print("--- Initializing OCR and Translator ---")
    reader = easyocr.Reader(['hi', 'en'])
    translator = GoogleTranslator(source='hi', target='en')
    
    doc = fitz.open(input_pdf)

    for page_num in range(len(doc)):
        print(f"Processing Page {page_num + 1}...")
        page = doc.load_page(page_num)
        
        # Get image for OCR
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        
        # 2. Get text with coordinates
        # result format: [([[x,y], [x,y], ...], "text", confidence), ...]
        ocr_results = reader.readtext(img_bytes)
        
        for (bbox, text, prob) in ocr_results:
            if prob < 0.2: continue # Skip low confidence
            
            try:
                # 3. Translate the specific snippet
                translated_text = translator.translate(text)
                
                # 4. Map OCR coordinates back to PDF coordinates
                # EasyOCR uses image pixels, PDF uses points (1/72 inch)
                # Since we used Matrix(2,2), we divide coordinates by 2
                (tl, tr, br, bl) = bbox
                pdf_rect = fitz.Rect(tl[0]/2, tl[1]/2, br[0]/2, br[1]/2)
                
                # 5. Clean the area (White out the Hindi)
                page.draw_rect(pdf_rect, color=(1, 1, 1), fill=(1, 1, 1))
                
                # 6. Insert English text
                # We use a small font size to try and fit the box
                page.insert_textbox(pdf_rect, translated_text, 
                                   fontsize=8, 
                                   fontname="helv", 
                                   align=1) # Center align
            except Exception as e:
                print(f"Skipping a snippet: {e}")

    # 7. Save as a new PDF
    doc.save(output_pdf)
    doc.close()
    print(f"✅ Success! Formatted PDF saved to: {output_pdf}")

if __name__ == "__main__":
    INPUT = r'D:\vidyaPY\translator\bpsc.pdf'
    OUTPUT = r'D:\vidyaPY\translator\bpsc_translated_fixed_layout.pdf'
    overlay_translation(INPUT, OUTPUT)