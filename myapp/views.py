from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserDetail
from .serializers import UserDetailSerializer

@api_view(['GET'])
def retrieveDetails(request, username):
    try:
        user = UserDetail.objects.get(username=username)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
    except UserDetail.DoesNotExist:
        return JsonResponse({'message': 'Username does not exist'}, status=404)

@api_view(['POST'])
def createUsername(request):
    serializer = UserDetailSerializer(data=request.data)
    if serializer.is_valid():
        if UserDetail.objects.filter(username=request.data.get('username')).exists():
            return JsonResponse({'message': 'Username already exists'}, status=400)
        serializer.save()
        return JsonResponse({'message': 'Created'})
    else:
        return Response(serializer.errors, status=400)

@api_view(['POST'])
def fillDetail(request):
    username = request.data.get('userDetails').get('username')
    # print(request.data)
    if not username:
        return Response({'error': 'Username is required'}, status=400)
    
    try:
        user = UserDetail.objects.get(username=username)
        serializer = UserDetailSerializer(user, data=request.data.get('userDetails'), partial=True)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'Saved successfully'})
        else:
            return Response(serializer.errors, status=400)
    except UserDetail.DoesNotExist:
        return JsonResponse({'error': 'Username does not exist'}, status=404)



import io
from PyPDF2 import PdfReader, PdfWriter
from django.http import HttpResponse
from .models import UserDetail

@api_view(['GET'])
def fill_pdf(request, username):
    try:
        user = UserDetail.objects.get(username=username)

        input_pdf_path = './myapp/i-765.pdf'
        output_pdf = io.BytesIO()

        with open(input_pdf_path, 'rb') as input_pdf:
            
            reader = PdfReader(input_pdf)
            fields = reader.get_form_text_fields()
            writer = PdfWriter()
            # for page_num in range(len(reader.pages)):
            #     page = reader.pages[page_num]
            #     writer.add_page(page)

            #     if '/Annots' in page:
            #         annots = page['/Annots']

            #         # Print all values of the page's annotations
            #         print(f"--- Page {page_num + 1} Annotations ---")
            #         for annot in annots:
            #             field = annot.get_object()
            #             field_name = field.get('/T').strip('()') if field.get('/T') else None
            #             field_value = field.get('/V') if field.get('/V') else None
            #             field_type = field.get('/FT')  # Field Type
            #             print(f"Field Name: {field_name}, Field Value: {field_value}, Field Type: {field_type}")


            # Handle the first page
            page_1_fields = {
                # Include fields from the start till '4.c'
                
                'Line1a_FamilyName[0]': user.familyName,
                'Line1b_GivenName[0]': user.givenName
                
                # Add other fields up to '4.c'
            }
            if user.renewal:
                page_1_fields['Part1_Checkbox[2]']='/3'
            elif user.replacement:
                page_1_fields['Part1_Checkbox[1]']='/2'
            else:
                page_1_fields['Part1_Checkbox[0]']='/1'
            
            page = reader.pages[0]  # First page
            writer.add_page(page)
            writer.update_page_form_field_values(writer.pages[0], page_1_fields)

            # Handle the second page
            page_2_fields = {
                # Include fields from '5.a' to '18.b'
                'Line7_AlienNumber[0]': user.alienRegistrationNumber,
                # Add other fields up to '18.b'
            }
            if len(reader.pages) > 1:
                page = reader.pages[1]  # Second page
                writer.add_page(page)
                print('asdsada',page)
                writer.update_page_form_field_values(page, page_2_fields)

            # Handle the third page
            page_3_fields = {
                # Include fields from '19.a' to '31.b'
                'Line19_DOB[0]': user.dateOfBirth.strftime("%m/%d/%Y") if user.dateOfBirth else '',
                # Add other fields up to '31.b'
            }
            if len(reader.pages) > 2:
                page = reader.pages[2]  # Third page
                writer.add_page(page)
                writer.update_page_form_field_values(page, page_3_fields)

            # For any remaining pages, add them without modifications
            for i in range(3, len(reader.pages)):
                writer.add_page(reader.pages[i])

            writer.write(output_pdf)
            output_pdf.seek(0)

        response = HttpResponse(output_pdf.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{username}_filled_form.pdf"'

        return response


    except UserDetail.DoesNotExist:
        return HttpResponse('User not found', status=404)
