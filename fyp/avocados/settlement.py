from django.db import models
from datetime import datetime
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes 
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class Settlement(models.Model):
    trade_contract_no = models.CharField(max_length=16)
    buyer = models.CharField(max_length=64)
    supplier = models.CharField(max_length=64)
    quantity = models.IntegerField()
    claim_amount = models.IntegerField()
    settlement_status = models.CharField(max_length=16, default="Pending")
    created_date = models.DateTimeField(default=datetime.now, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True)

class SettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settlement
        fields = "__all__"

class SettlementView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        settlements = Settlement.objects.all()
        serializer = SettlementSerializer(settlements, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        
        trade_contract_no = dict(request.data)['trade_contract_no'][0]

        if Settlement.objects.filter(trade_contract_no=trade_contract_no):
            return Response({"error" : "Settlement already on-going/completed for this trade contract"}, status=status.HTTP_400_BAD_REQUEST)

        buyer = dict(request.data)['buyer'][0]
        supplier = dict(request.data)['supplier'][0]
        quantity = dict(request.data)['quantity'][0]
        claim_amount = dict(request.data)['claim_amount'][0]

        modified_data = helper_function(trade_contract_no, buyer, supplier, quantity, claim_amount)
        serializer = SettlementSerializer(data=modified_data)
        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_settlement_by_status(request, settlement_status):
    settlements = Settlement.objects.filter(settlement_status=settlement_status)
    serializer = SettlementSerializer(settlements, many=True)

    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_if_settlement_exists(request, trade_contract_no):
    try:
        settlement = Settlement.objects.get(trade_contract_no=trade_contract_no)
    except Settlement.DoesNotExist:
        return Response({"error" : "Settlement does not exist for this trade contract"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = SettlementSerializer(settlement)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_claim_amount_and_status(request, trade_contract_no):
    try:
        settlement = Settlement.objects.get(trade_contract_no=trade_contract_no)
    except Settlement.DoesNotExist:
        return Response({"error" : "Settlement does not exist for this trade contract"}, status=status.HTTP_400_BAD_REQUEST)

    settlement.settlement_status = dict(request.data)["settlement_status"][0]
    settlement.updated_date = datetime.now()
    settlement.claim_amount = dict(request.data)["claim_amount"][0]
    settlement.save()

    return Response({"message": "Claim amount and status successfully updated"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_settlement_status(request, trade_contract_no):

    try:
        settlement = Settlement.objects.get(trade_contract_no=trade_contract_no)
    except Settlement.DoesNotExist:
        return Response({"error" : "Settlement does not exist for this trade contract"}, status=status.HTTP_400_BAD_REQUEST)
    
    settlement.settlement_status = dict(request.data)["settlement_status"][0]
    settlement.updated_date = datetime.now()
    settlement.remarks = dict(request.data)["remarks"][0]
    settlement.save()

    return Response({"message" : "Settlement status has successfully changed"}, status=status.HTTP_200_OK)

def helper_function(trade_contract_no, buyer, supplier, quantity, claim_amount):
    dict = {}
    dict['trade_contract_no'] = trade_contract_no
    dict['buyer'] = buyer
    dict['supplier'] = supplier
    dict['quantity'] = quantity
    dict['claim_amount'] = claim_amount

    return dict