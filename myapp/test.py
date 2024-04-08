
import io
from PyPDF2 import PdfReader, PdfWriter

    

input_pdf_path = '/Users/seemandharjain/shefali/myproject/myapp/Form I-765, Application For Employment Authorization.pdf'
output_pdf = io.BytesIO()

with open(input_pdf_path, 'rb') as input_pdf:
    reader = PdfReader(input_pdf)
    fields = reader.get_form_text_fields()
    writer = PdfWriter()

    # Handle the first page
    page_1_fields = {
        # Include fields from the start till '4.c'
        'givenName': 'Sam',
        'familyName': 'Jain',
        # Add other fields up to '4.c'
    }
    print(page_1_fields)
    page = reader.pages[0]  # First page
    writer.add_page(page)
    writer.update_page_form_field_values(writer.pages[0], page_1_fields)

    # For any remaining pages, add them without modifications
    for i in range(1, len(reader.pages)):
        writer.add_page(reader.pages[i])

with open("f1illed-out.pdf", "wb") as output_stream:
    writer.write(output_stream)