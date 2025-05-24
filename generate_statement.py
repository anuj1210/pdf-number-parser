from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import pdfplumber
import re
import os
from contacts import get_name_for_number, CONTACTS

def is_airtel_number(number):
    # This is a simplified check - you might want to update this with actual Airtel number prefixes
    airtel_prefixes = ['944', '945', '946', '947', '948', '949']
    return any(number.startswith(prefix) for prefix in airtel_prefixes)

def categorize_call(number):
    # Assuming numbers starting with same first 3 digits are local
    # You might want to update this logic based on your specific requirements
    if number.startswith('99'):  # Example: considering 99* as local
        if is_airtel_number(number):
            return "1.a to other mobiles"
        return "1.a to other mobiles"
    else:
        if is_airtel_number(number):
            return "2.a to airtel mobile"
        return "2.b to other mobiles"

def extract_call_records_from_pdf(input_pdf_path):
    """Extract and categorize call records from the input PDF"""
    call_records = []
    current_section = None
    
    with pdfplumber.open(input_pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            lines = text.split('\n')
            
            print(f"\nProcessing page {page_num}")
            for line_num, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                
                # Check for section headers
                if "1.Local Calls" in line:
                    current_section = "1.Local Calls"
                    continue
                elif "2.STD Calls" in line:
                    current_section = "2.STD Calls"
                    continue
                elif "1.a to other mobiles" in line:
                    current_section = "1.a to other mobiles"
                    continue
                elif "2.a to airtel mobile" in line:
                    current_section = "2.a to airtel mobile"
                    continue
                elif "2.b to other mobiles" in line:
                    current_section = "2.b to other mobiles"
                    continue
                
                # Skip header lines and totals
                if any(header in line for header in ["S.no", "YOUR ITEMIZED", "volume", "Relationship number", "TOTAL", "Page", "Airtel"]):
                    continue
                
                # Print raw line for debugging
                print(f"Raw line {line_num}: {line}")
                
                # Split the line into two potential records
                # Each record follows the pattern: serial date time number duration pulse amount
                records_pattern = r'(\d+)\s+(\d{2}/[A-Z]{3}/\d{4})\s+(\d{2}:\d{2}:\d{2})\s+(\d{10})\s+(\d{2}:\d{2})\s+(\d+)\s+(\d+\.\d{2})'
                
                matches = list(re.finditer(records_pattern, line))
                
                for match in matches:
                    serial, date, time, number, duration, pulse, amount = match.groups()
                    serial_int = int(serial)
                    
                    if current_section:
                        print(f"Found record with S.No: {serial} in section {current_section}")
                        
                        name = get_name_for_number(number)
                        print(f"Looking up number: {number}, Found name: {name}")
                        
                        category = current_section
                        # Store records in exact order they appear in PDF
                        call_records.append((serial_int, category, [serial, date, time, number, name, duration, pulse, amount]))
    
    # Keep records in the exact order they were found in the PDF
    return call_records

def create_statement(input_pdf_path, output_filename="new_statement.pdf"):
    # Extract call records from input PDF
    call_records = extract_call_records_from_pdf(input_pdf_path)
    
    if not call_records:
        print("No call records found in the input PDF!")
        return

    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20
    )
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=20
    )
    
    elements.append(Paragraph("YOUR ITEMIZED STATEMENT", title_style))
    elements.append(Spacer(1, 20))

    # Headers for the table
    headers = ['Sr No.', 'Date', 'Time', 'Number', 'Name', 'Duration/\nvolume', 'Pulse', 'Amount']

    # Create sections
    sections = {
        "1.Local Calls": {
            "1.a to other mobiles": []
        },
        "2.STD Calls": {
            "2.a to airtel mobile": [],
            "2.b to other mobiles": []
        }
    }

    # Organize records into sections
    for serial_int, category, record in call_records:
        if category.startswith("1."):
            sections["1.Local Calls"]["1.a to other mobiles"].append((serial_int, record))
        elif category.startswith("2."):
            if "airtel" in category:
                sections["2.STD Calls"]["2.a to airtel mobile"].append((serial_int, record))
            else:
                sections["2.STD Calls"]["2.b to other mobiles"].append((serial_int, record))

    # Create tables for each section
    for main_section, subsections in sections.items():
        elements.append(Paragraph(main_section, section_style))
        
        for subsection, records in subsections.items():
            if records:  # Only create subsection if it has records
                elements.append(Paragraph(subsection, section_style))
                
                # Sort records by serial number (S.No from input PDF) as integer
                sorted_records = sorted(records, key=lambda x: int(x[0]))
                
                table_data = [headers]
                for _, record in sorted_records:
                    table_data.append(record)

                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 10))

    # Build the PDF
    doc.build(elements)
    print(f"New PDF created with {len(call_records)} call records: {output_filename}")

if __name__ == "__main__":
    # Get the path to Downloads folder
    downloads_path = os.path.expanduser("~/Downloads")
    
    # Path to your input PDF file in Downloads
    input_pdf = os.path.join(downloads_path, "MF2629I002189456.pdf")
    
    # Path where you want to save the output PDF
    output_pdf = os.path.join(downloads_path, "names_MF2629I002189456.pdf")
    
    # Generate the new statement with names
    create_statement(input_pdf, output_pdf)
    print(f"Input PDF: {input_pdf}")
    print(f"Output PDF will be saved to: {output_pdf}") 