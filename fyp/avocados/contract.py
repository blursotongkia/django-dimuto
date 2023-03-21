from datetime import datetime
from django.db import models
from rest_framework import status, serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class Contract(models.Model):
    trade_contract_no = models.CharField(max_length=16)
    company = models.CharField(max_length=64)
    status = models.CharField(max_length=16)
    my_role = models.CharField(max_length=16)
    buyer_name = models.CharField(max_length=64)
    supplier_name = models.CharField(max_length=64)
    reference_no = models.CharField(max_length=16)
    total_price = models.CharField(max_length=16)
    create_date = models.DateTimeField(default=datetime.now, blank=True)
    last_update = models.DateTimeField(default=datetime.now, blank=True)
    currency = models.CharField(max_length=3)
    inco_terms = models.CharField(max_length=3)
    payment_terms = models.CharField(max_length=3)

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"

class ContractViewSet(ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = ContractSerializer
    queryset = Contract.objects.all()

@api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def get_trade_contract_by_id(request, trade_contract_no, company):

    if company == "Universal Insurance Co.":
        contracts = Contract.objects.filter(trade_contract_no=trade_contract_no)
        serializer = ContractSerializer(contracts, many=True)
        try:
            obj = serializer.data[0]
            return Response(obj, status=status.HTTP_200_OK)
        except IndexError:
            return Response([], status=status.HTTP_400_BAD_REQUEST)
    
    contracts = Contract.objects.filter(trade_contract_no=trade_contract_no, company=company)
    serializer = ContractSerializer(contracts, many=True)
    try:
        obj = serializer.data[0]
        return Response(obj, status=status.HTTP_200_OK)
    except IndexError:
        return Response([], status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def get_trade_contracts_by_company(request, company):
    if company == "Universal Insurance Co.":
        contracts = Contract.objects.all()
        serializer = ContractSerializer(contracts, many=True)
    else:
        contracts = Contract.objects.filter(company=company)
        serializer = ContractSerializer(contracts, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def get_role_by_company(request, trade_contract_no, company):

    try:
        contract = Contract.objects.get(trade_contract_no=trade_contract_no)
    except Contract.DoesNotExist:
        return Response({"error" : "Trade contract does not exist."}, status=status.HTTP_400_BAD_REQUEST)

    if company == "Universal Insurance Co.":
        return Response({"role" : "insurer"}, status=status.HTTP_200_OK)

    if contract.company.lower() == company.lower():
        return Response({"role" : contract.my_role.lower()}, status=status.HTTP_200_OK)
    else:
        if contract.my_role.lower() == "buyer":
            if contract.supplier_name.lower() == company.lower():
                return Response({"role" : "supplier"}, status=status.HTTP_200_OK)
        else:
            if contract.buyer_name.lower() == company.lower():
                return Response({"role" : "supplier"}, status=status.HTTP_200_OK)
        
    return Response({"error" : "Company role not found in this trade contract number."}, status=status.HTTP_400_BAD_REQUEST)