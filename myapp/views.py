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

            # Handle the first page
            page_1_fields = {
                
                'Line1a_FamilyName[0]': user.familyName,
                'Line1b_GivenName[0]': user.givenName
                
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
                'Line7_AlienNumber[0]': user.alienRegistrationNumber,
            }
            if len(reader.pages) > 1:
                page = reader.pages[1]  # Second page
                writer.add_page(page)
                print('asdsada',page)
                writer.update_page_form_field_values(page, page_2_fields)

            # Handle the third page
            page_3_fields = {
                'Line19_DOB[0]': user.dateOfBirth.strftime("%m/%d/%Y") if user.dateOfBirth else '',
            }
            if len(reader.pages) > 2:
                page = reader.pages[2]  # Third page
                writer.add_page(page)
                writer.update_page_form_field_values(page, page_3_fields)


            for i in range(3, len(reader.pages)):
                writer.add_page(reader.pages[i])

            writer.write(output_pdf)
            output_pdf.seek(0)

        response = HttpResponse(output_pdf.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{username}_filled_form.pdf"'

        return response


    except UserDetail.DoesNotExist:
        return HttpResponse('User not found', status=404)
