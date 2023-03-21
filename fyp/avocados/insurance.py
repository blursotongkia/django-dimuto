from django.db import models
from datetime import datetime
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes 
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class Insurance(models.Model):
    trade_contract_no = models.CharField(max_length=16)
    buyer = models.CharField(max_length=64)
    supplier = models.CharField(max_length=64)
    total_price = models.CharField(max_length=64)
    insurance_tier = models.CharField(max_length=64, null=True)
    insurance_premium = models.IntegerField(default=0)
    status = models.CharField(max_length=16, default="Pending")
    created_date = models.DateTimeField(default=datetime.now, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True)

class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = "__all__"

class InsuranceView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        insurances = Insurance.objects.all()
        serializer = InsuranceSerializer(insurances, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        trade_contract_no = dict(request.data)['trade_contract_no'][0]

        if Insurance.objects.filter(trade_contract_no=trade_contract_no):
            return Response({"error" : "Insurance already exists for this Trade Contract"}, status=status.HTTP_400_BAD_REQUEST)

        buyer = dict(request.data)['buyer'][0]
        supplier = dict(request.data)['supplier'][0]
        total_price = dict(request.data)['total_price'][0]
        insurance_tier = dict(request.data)['insurance_tier'][0]
        
        modified_data = helper_function(trade_contract_no, buyer, supplier, total_price, insurance_tier)
        serializer = InsuranceSerializer(data=modified_data)
        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def get_insurance_by_status(request, status):
    insurances = Insurance.objects.filter(status=status)
    serializer = InsuranceSerializer(insurances, many=True)

    return Response(serializer.data)

@api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def check_if_insurance_exists(request, trade_contract_no):
    try:
        insurance = Insurance.objects.get(trade_contract_no=trade_contract_no)
    except Insurance.DoesNotExist:
        return Response({"error" : "Insurance does not exist for this Trade Contract"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = InsuranceSerializer(insurance)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def update_insurance_status(request, trade_contract_no):

    try:
        insurance = Insurance.objects.get(trade_contract_no=trade_contract_no)
    except Insurance.DoesNotExist:
        return Response({"error" : "Insurance does not exist for this Trade Contract"}, status=status.HTTP_400_BAD_REQUEST)

    tier = dict(request.data)["insurance_tier"][0]
    insurance.insurance_tier = tier
    
    if tier.lower() == "t1":
        insurance.insurance_premium = 5000
    elif tier.lower() == "t2":
        insurance.insurance_premium = 10000
    else:
        insurance.insurance_premium = 15000

    insurance.status = dict(request.data)["status"][0]
    insurance.updated_date = datetime.now()
    insurance.remarks = dict(request.data)["remarks"][0]
    insurance.save()

    return Response({"message" : "Insurance status has successfully changed"}, status=status.HTTP_200_OK)

def helper_function(trade_contract_no, buyer, supplier, total_price, insurance_tier):
    dict = {}
    dict['trade_contract_no'] = trade_contract_no
    dict['buyer'] = buyer
    dict['supplier'] = supplier
    dict['total_price'] = total_price
    dict['insurance_tier'] = insurance_tier

    if insurance_tier.lower() == "t1":
        dict['insurance_premium'] = 5000
    elif insurance_tier.lower() == "t2":
        dict['insurance_premium'] = 10000
    else:
        dict['insurance_premium'] = 15000

    return dict