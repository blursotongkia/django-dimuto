import json
import base64
import requests
from datetime import datetime
from django.db import models
from django.core.files.base import ContentFile
from rest_framework import status, serializers, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes 
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class ResponseThen(Response):
    def __init__(self, data, then_callback, **kwargs):
        super().__init__(data, **kwargs)
        self.then_callback = then_callback

    def close(self):
        super().close()
        self.then_callback()

class Images(models.Model):
    image = models.FileField()
    trade_contract_no = models.CharField(max_length=16)
    uploader_role = models.CharField(max_length=16)
    uploader_name = models.CharField(max_length=64)
    carton_no = models.IntegerField(default=1)
    quantity = models.IntegerField(null=True)
    description = models.CharField(max_length=64, default="avocados")
    date_taken = models.DateTimeField(default=datetime.now, blank=True)
    predicted_image = models.ImageField(blank=True)
    blemished_avocados = models.IntegerField(default=0)
    unripe = models.IntegerField(default=0)
    almost_ripe = models.IntegerField(default=0)
    ripe = models.IntegerField(default=0)
    overripe = models.IntegerField(default=0)
    rotten = models.IntegerField(default=0)

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = "__all__"

class ImageView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request):
        images = Images.objects.all()
        serializer = ImageSerializer(images, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        trade_contract_no = dict((request.data).lists())['trade_contract_no_id'][0]
        uploader_role = dict((request.data).lists())['uploader_role'][0]
        uploader_name = dict((request.data).lists())['uploader_name'][0]
        num_of_cartons = dict((request.data).lists())['num_of_cartons'][0]
        name = dict((request.data).lists())['name'][0]
        email = dict((request.data).lists())['email'][0]
        count = 1
        flag = 1
        
        arr = [{"email" : email, "trade_contract_no" : trade_contract_no, "name" : name, "role" : uploader_role}]
        for i in range(1, int(num_of_cartons)+1):
            try:
                images = dict((request.data).lists())[str(i)]
                for img_name in images:
                    modified_data = modify_input_for_multiple_files(trade_contract_no, img_name, uploader_role, uploader_name, i)
                    print(modified_data)
                    file_serializer = ImageSerializer(data=modified_data)
                    print(file_serializer)
                    if file_serializer.is_valid():
                        file_serializer.save()
                        arr.append(file_serializer.data)
                        count += 1
                    else:
                        flag = 0
            except KeyError:
                continue
        
        def do_after():
            headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
            r = requests.post('http://localhost:8000/ml-prediction', data=json.dumps(arr), headers=headers)

        if flag == 1:
            return ResponseThen(arr, do_after, status=status.HTTP_200_OK)
        else:   
            return Response({"error" : "Error Exception Occurred"}, status=status.HTTP_400_BAD_REQUEST)

class UpdateImage(generics.UpdateAPIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return Images.objects.get(pk=pk)

    def partial_update(self, request, *args, **kwargs):

        email_dict = {}

        total_blemished = 0
        total_unripe = 0
        total_almost_ripe = 0
        total_ripe = 0
        total_overripe = 0
        total_rotten = 0
        total_quantity = 0

        blemished_pc = 0
        unripe_pc = 0
        almost_ripe_pc = 0
        ripe_pc = 0
        overripe_pc = 0
        rotten_pc = 0

        for item in request.data:
            name = item["name"]
            email = item["email"]
            trade_contract_no = item["trade_contract_no"]
            role = item["role"]
            quantity = item['quantity']
            pk = item['id']
            filename = str(pk) + '.jpg'
            encoded_string = item['predicted_image']
            predicted_image = ContentFile(base64.b64decode(encoded_string), name=filename)

            blemished_avocados = item["blemished_avocados"]
            unripe = item["unripe"]
            almost_ripe = item["almost_ripe"]
            ripe = item["ripe"]
            overripe = item["overripe"]
            rotten = item["rotten"]

            total_blemished += blemished_avocados
            total_unripe += unripe
            total_almost_ripe += almost_ripe
            total_ripe += ripe
            total_overripe += overripe
            total_rotten += rotten
            total_quantity += quantity

            instance = self.get_object(pk)
            instance.quantity = quantity
            instance.predicted_image = predicted_image
            instance.blemished_avocados = blemished_avocados
            instance.unripe = unripe
            instance.almost_ripe = almost_ripe
            instance.ripe = ripe
            instance.overripe = overripe
            instance.rotten = rotten
            instance.save()

            if 'email' not in email_dict.keys():
                email_dict['email'] = email
                email_dict['name'] = name
                email_dict['trade_contract_no'] = trade_contract_no
                email_dict['role'] = role

        if(total_blemished != 0):
            blemished_pc = (total_blemished / total_quantity) * 100

        if(total_unripe != 0):
            unripe_pc = (total_unripe / total_quantity) * 100

        if(total_almost_ripe != 0):
            almost_ripe_pc = (total_almost_ripe / total_quantity) * 100

        if(total_ripe != 0):
            ripe_pc = (total_ripe / total_quantity) * 100

        if(total_overripe != 0):
            overripe_pc = (total_overripe / total_quantity) * 100

        if(total_rotten != 0):
            rotten_pc = (total_rotten / total_quantity) * 100


        email_dict["blemished_pc"] = blemished_pc
        email_dict["unripe_pc"] = unripe_pc
        email_dict["almost_ripe_pc"] = almost_ripe_pc
        email_dict["ripe_pc"] = ripe_pc
        email_dict["overripe_pc"] = overripe_pc
        email_dict["rotten_pc"] = rotten_pc

        email_dict["total_blemished"] = total_blemished
        email_dict["total_unripe"] = total_unripe
        email_dict["total_almost_ripe"] = total_almost_ripe
        email_dict["total_ripe"] = total_ripe
        email_dict["total_overripe"] = total_overripe
        email_dict["total_rotten"] = total_rotten
        email_dict["total_quantity"] = total_quantity


        def do_next():
            headers = {'Content-Type': 'application/json', 'Accept':'application/json', 'Authorization' : "Token e6eadf4924cf1dcba72e8610de60a2a08aa06a3b"}
            r = requests.post('https://www.avocados.live/email', data=json.dumps(email_dict), headers=headers)

        return ResponseThen({"message" : "Images has been successfully updated with the predictions"}, do_next, status=status.HTTP_200_OK)

# helper function
def modify_input_for_multiple_files(trade_contract_no, image, uploader_role, uploader_name, carton_no):
    dict = {}
    dict['trade_contract_no'] = trade_contract_no
    dict['image'] = image
    dict['uploader_role'] = uploader_role
    dict['uploader_name'] = uploader_name
    dict['carton_no'] = carton_no

    return dict

@api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def order_by_carton_no(request, trade_contract_no):
    images = Images.objects.filter(trade_contract_no=trade_contract_no).order_by('carton_no')
    serializer = ImageSerializer(images, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def get_company_name_and_role(request, trade_contract_no, uploader_role):
    images = Images.objects.filter(trade_contract_no=trade_contract_no, uploader_role=uploader_role)
    serializer = ImageSerializer(images, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)