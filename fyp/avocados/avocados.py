import requests
import json
from .image import Images, ImageSerializer
# from xhtml2pdf import pisa
from django.db import models
from django.http import HttpResponse
from django.template.loader import get_template

from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
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

class Avocados(models.Model):
    trade_contract_no = models.CharField(max_length=16)
    role = models.CharField(max_length=16)
    blemished_pc = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    unripe_pc = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    almost_ripe_pc = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    ripe_pc = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    overripe_pc = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    rotten_pc = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    total_blemished = models.IntegerField(default=0)
    total_unripe = models.IntegerField(default=0)
    total_almost_ripe = models.IntegerField(default=0)
    total_ripe = models.IntegerField(default=0)
    total_overripe = models.IntegerField(default=0)
    total_rotten = models.IntegerField(default=0)
    total_quantity = models.IntegerField(default=0)

class AvocadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avocados
        fields = "__all__"

class AvocadosView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        avocados = Avocados.objects.all()
        serializer = AvocadoSerializer(avocados, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        trade_contract_no = dict(request.data)["trade_contract_no"]
        role = dict(request.data)["role"]
        total_blemished = dict(request.data)["total_blemished"]
        total_unripe = dict(request.data)["total_unripe"]
        total_almost_ripe = dict(request.data)["total_almost_ripe"]
        total_ripe = dict(request.data)["total_ripe"]
        total_overripe = dict(request.data)["total_overripe"]
        total_rotten = dict(request.data)["total_rotten"]
        total_quantity = dict(request.data)["total_quantity"]

        def do_after():
            headers = {'Content-Type': 'application/json', 'Accept':'application/json', 'Authorization' : "Token e6eadf4924cf1dcba72e8610de60a2a08aa06a3b"}
            res_dict = {
                "trade_contract_no" : trade_contract_no, "role" : role,
                "total_blemished" : total_blemished, "total_unripe" : total_unripe, 
                "total_almost_ripe" : total_almost_ripe, "total_ripe" : total_ripe, 
                "total_overripe" : total_overripe, "total_rotten" : total_rotten, 
                "total_quantity" : total_quantity
            }
            r = requests.post('https://www.avocados.live/avocados/update-results', data=json.dumps(res_dict), headers=headers)

        if Avocados.objects.filter(trade_contract_no=trade_contract_no, role=role):
            return ResponseThen({"message" : "Image results updating ... Please wait while it finishes updating"}, do_after, status=status.HTTP_200_OK)

        blemished_pc = round(dict(request.data)["blemished_pc"], 1)
        unripe_pc = round(dict(request.data)["unripe_pc"], 1)
        almost_ripe_pc = round(dict(request.data)["almost_ripe_pc"], 1)
        ripe_pc = round(dict(request.data)["ripe_pc"], 1)
        overripe_pc = round(dict(request.data)["overripe_pc"], 1)
        rotten_pc = round(dict(request.data)["rotten_pc"], 1)

        modified_data = helper_function(trade_contract_no, role, blemished_pc, unripe_pc, almost_ripe_pc, ripe_pc, overripe_pc, rotten_pc,
                                        total_blemished, total_unripe, total_almost_ripe, total_ripe, total_overripe, total_rotten, total_quantity)

        serializer = AvocadoSerializer(data=modified_data)  
        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def get_results_by_trade_contract_no_and_role(request, trade_contract_no, role):
    
    avocados = Avocados.objects.filter(trade_contract_no=trade_contract_no, role=role)
    serializer = AvocadoSerializer(avocados, many=True)
    try:
        obj = serializer.data[0]
        return Response(obj, status=status.HTTP_200_OK)
    except IndexError:
        return Response([], status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def update_results_by_trade_contract_no_and_role(request):

    trade_contract_no = dict(request.data)["trade_contract_no"]
    role = dict(request.data)["role"]

    avocados = Avocados.objects.filter(trade_contract_no=trade_contract_no, role=role)
    serializer = AvocadoSerializer(avocados, many=True)

    id = serializer.data[0]['id']
    avocado = Avocados.objects.get(id=id)

    avocado.total_blemished += dict(request.data)["total_blemished"]
    avocado.total_unripe += dict(request.data)["total_unripe"]
    avocado.total_almost_ripe += dict(request.data)["total_almost_ripe"]
    avocado.total_ripe += dict(request.data)["total_ripe"]
    avocado.total_overripe += dict(request.data)["total_overripe"]
    avocado.total_rotten += dict(request.data)["total_rotten"]
    avocado.total_quantity += dict(request.data)["total_quantity"]

    if(avocado.total_quantity != 0):
        if(avocado.total_blemished != 0):
            avocado.blemished_pc = round(((avocado.total_blemished / avocado.total_quantity) * 100), 1)

        if(avocado.total_unripe != 0):
            avocado.unripe_pc = round(((avocado.total_unripe / avocado.total_quantity) * 100), 1)

        if(avocado.total_almost_ripe != 0):
            avocado.almost_ripe_pc = round(((avocado.total_almost_ripe / avocado.total_quantity) * 100), 1)

        if(avocado.total_ripe != 0):
            avocado.ripe_pc = round(((avocado.total_ripe / avocado.total_quantity) * 100), 1)

        if(avocado.total_overripe != 0):
            avocado.overripe_pc = round(((avocado.total_overripe / avocado.total_quantity) * 100), 1)

        if(avocado.total_rotten != 0):
            avocado.rotten_pc = round(((avocado.total_rotten / avocado.total_quantity) * 100), 1)

    avocado.save()

    return Response({"message" : "Image results successfully updated"}, status=status.HTTP_200_OK)


@api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def generate_pdf_report(request, trade_contract_no, role):

    if Images.objects.filter(trade_contract_no=trade_contract_no, uploader_role=role) and Avocados.objects.filter(trade_contract_no=trade_contract_no, role=role):

        if role == 'buyer':
            images = Images.objects.filter(trade_contract_no=trade_contract_no, uploader_role=role)
            avocados = Avocados.objects.filter(trade_contract_no=trade_contract_no, role=role)
            serializer = AvocadoSerializer(avocados, many=True)
            img_serializer = ImageSerializer(images, many=True)

            uploader_name = img_serializer.data[0]['uploader_name']

            id = serializer.data[0]['id']
            avocado = Avocados.objects.get(id=id)

            template_path = 'pdf_report_buyer.html'
            context = {'trade_contract_no': trade_contract_no, 'buyer' : uploader_name, 'blemished_pc' : avocado.blemished_pc, 'unripe_pc' : avocado.unripe_pc, 'almost_ripe_pc' : avocado.almost_ripe_pc, 'ripe_pc' : avocado.ripe_pc, 'overripe_pc' : avocado.overripe_pc, 'rotten_pc' : avocado.rotten_pc, 'images' : images}
            template = get_template(template_path)
            html = template.render(context)

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="' + trade_contract_no + '.pdf"'

            pdf = pisa.CreatePDF(html, dest=response)
            if pdf.err:
                return Response([], status=status.HTTP_400_BAD_REQUEST)

            return response
        else:
            images = Images.objects.filter(trade_contract_no=trade_contract_no, uploader_role=role)
            avocados = Avocados.objects.filter(trade_contract_no=trade_contract_no, role=role)
            serializer = AvocadoSerializer(avocados, many=True)
            img_serializer = ImageSerializer(images, many=True)

            uploader_name = img_serializer.data[0]['uploader_name']

            id = serializer.data[0]['id']
            avocado = Avocados.objects.get(id=id)

            template_path = 'pdf_report_supplier.html'
            context = {'trade_contract_no': trade_contract_no, 'supplier' : uploader_name, 'blemished_pc' : avocado.blemished_pc, 'unripe_pc' : avocado.unripe_pc, 'almost_ripe_pc' : avocado.almost_ripe_pc, 'ripe_pc' : avocado.ripe_pc, 'overripe_pc' : avocado.overripe_pc, 'rotten_pc' : avocado.rotten_pc, 'images' : images}
            template = get_template(template_path)
            html = template.render(context)

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="' + trade_contract_no + '.pdf"'

            pdf = pisa.CreatePDF(html, dest=response)
            if pdf.err:
                return Response([], status=status.HTTP_400_BAD_REQUEST)

            return response
    else:
        return Response({"error" : "No Image results to generate a report"}, status=status.HTTP_400_BAD_REQUEST)

def helper_function(trade_contract_no, role, blemished_pc, unripe_pc, almost_ripe_pc, ripe_pc, overripe_pc, rotten_pc, total_blemished, total_unripe, total_almost_ripe, total_ripe, total_overripe, total_rotten, total_quantity):
    dict = {}
    dict['trade_contract_no'] = trade_contract_no
    dict['role'] = role
    dict['blemished_pc'] = blemished_pc
    dict['unripe_pc'] = unripe_pc
    dict['almost_ripe_pc'] = almost_ripe_pc
    dict['ripe_pc'] = ripe_pc
    dict['overripe_pc'] = overripe_pc
    dict['rotten_pc'] = rotten_pc
    dict['total_blemished'] = total_blemished
    dict['total_unripe'] = total_unripe
    dict['total_almost_ripe'] = total_almost_ripe
    dict['total_ripe'] = total_ripe
    dict['total_overripe'] = total_overripe
    dict['total_rotten'] = total_rotten
    dict['total_quantity'] = total_quantity

    return dict