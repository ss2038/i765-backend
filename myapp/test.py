
import io
from PyPDF2 import PdfReader, PdfWriter

    

input_pdf_path = '/Users/shefali/myproject/myapp/Form I-765, Application For Employment Authorization.pdf'
output_pdf = io.BytesIO()

with open(input_pdf_path, 'rb') as input_pdf:
    reader = PdfReader(input_pdf)
    fields = reader.get_form_text_fields()
    writer = PdfWriter()

    # Handle the first page of the form
    page_1_fields = {
        'givenName': 'Shefali',
        'familyName': 'Saxena',
    }
    print(page_1_fields)
    page = reader.pages[0]  # First page
    writer.add_page(page)
    writer.update_page_form_field_values(writer.pages[0], page_1_fields)

    for i in range(1, len(reader.pages)):
        writer.add_page(reader.pages[i])

with open("filled-out.pdf", "wb") as output_stream:
    writer.write(output_stream)
