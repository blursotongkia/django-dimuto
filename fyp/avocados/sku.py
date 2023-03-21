from django.db import models
from rest_framework import status, serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes 
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class SKU(models.Model):
    trade_contract_no = models.CharField(max_length=16)
    sku_fruit_type = models.CharField(max_length=16)
    sku_supplier = models.CharField(max_length=64)
    sku_trader = models.CharField(max_length=64)
    sku_buyer = models.CharField(max_length=64)
    quantity_cartons = models.IntegerField()
    total_sell_price = models.CharField(max_length=64)
    currency = models.CharField(max_length=16)

class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = "__all__"

class SKUViewSet(ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = SKUSerializer
    queryset = SKU.objects.all()

@api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def get_sku_by_trade_contract_no(request, trade_contract_no):
    skus = SKU.objects.filter(trade_contract_no=trade_contract_no)
    serializer = SKUSerializer(skus, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)