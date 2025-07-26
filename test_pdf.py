#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from io import BytesIO
from fpdf import FPDF

# Test modern FPDF approach
def test_modern_pdf():
    print("Testing modern PDF generation...")
    
    test_text = """नमस्ते! यह एक परीक्षण है। भारत एक महान देश है जहाँ अनेक भाषाएँ बोली जाती हैं। हिंदी, मराठी, बंगाली, तमिल, तेलुगु और अन्य भारतीय भाषाएँ यहाँ प्रचलित हैं। यह टेस्ट यह देखने के लिए है कि PDF में टेक्स्ट सही तरीके से रेंडर हो रहा है या नहीं।"""
    
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Add font (modern syntax)
        font_path = os.path.join("assets", "NotoSansDevanagari-Regular.ttf")
        if not os.path.exists(font_path):
            print(f"Font file not found: {font_path}")
            return False
            
        pdf.add_font("Noto", "", font_path)  # No uni=True parameter
        pdf.set_font("Noto", size=14)
        
        # Title
        pdf.cell(0, 15, "Modern PDF Test - Hindi", align="C")
        pdf.ln(20)
        
        # Set content font
        pdf.set_font("Noto", size=12)
        
        # Clean text
        clean_text = ' '.join(test_text.split())
        
        # Method: Split by sentences and handle properly
        sentences = clean_text.replace('।', '।|').split('|')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(sentence) > 80:
                # Split long sentences by words
                words = sentence.split()
                current_chunk = ""
                
                for word in words:
                    test_chunk = current_chunk + " " + word if current_chunk else word
                    if len(test_chunk) <= 70:
                        current_chunk = test_chunk
                    else:
                        if current_chunk:
                            pdf.multi_cell(0, 8, current_chunk, align="L")
                            pdf.ln(2)
                        current_chunk = word
                
                if current_chunk:
                    pdf.multi_cell(0, 8, current_chunk, align="L")
                    pdf.ln(2)
            else:
                pdf.multi_cell(0, 8, sentence, align="L")
                pdf.ln(2)
        
        # Save using modern syntax
        output = BytesIO()
        pdf_bytes = pdf.output()  # Modern FPDF returns bytes
        output.write(pdf_bytes)
        
        # Save to file
        with open("modern_test_output.pdf", "wb") as f:
            f.write(output.getvalue())
        
        print("✓ Modern PDF test successful: modern_test_output.pdf")
        return True
        
    except Exception as e:
        print(f"✗ Modern PDF test failed: {e}")
        return False

if __name__ == "__main__":
    test_modern_pdf()
