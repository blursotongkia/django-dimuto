import requests
from .contract import ContractSerializer
from .sku import SKUSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

headers = {'Content-Type': 'application/json', 'Accept':'application/json', 'Authorization' : 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImZjODg1ZjQzNTI3YjU1ODZkYjE2MDM5NmY0NTc3MjI3NGU4YTAxMzcyYmZkODk0ZWE3YWI5ZDVkYzBhNmNhNTg4ZDgxNjlkY2RmOTAxMTRjIn0.eyJhdWQiOiIxIiwianRpIjoiZmM4ODVmNDM1MjdiNTU4NmRiMTYwMzk2ZjQ1NzcyMjc0ZThhMDEzNzJiZmQ4OTRlYTdhYjlkNWRjMGE2Y2E1ODhkODE2OWRjZGY5MDExNGMiLCJpYXQiOjE2MTU2OTE4MTQsIm5iZiI6MTYxNTY5MTgxNCwiZXhwIjoxNjE1NzAyNjE0LCJzdWIiOiIzMzgiLCJzY29wZXMiOltdfQ.I2LePl3uqyoOd0tgQKUH3zLc2VwFaUU5vSpPn2nifasevBU5x7FaYTeFZCUgWLkH_ouXLp7RF0Ek7cuUIH3hNS0uAba19aO7wsXarOp8Ko_j-dIOae0DLYAqs5OzGJMMbBwRxiWbEaIoDUzlWlh5ysiFDziZglTsCZskdERWfvZg5thzKLHMo_pCF3NOfGpeBp7GCZr9lDH5nCuux5t4hjmRjx6oWgr9sPnEFjY3SIb7E1IOPI4KhEOhiKjyMpPAS549apSB1jVBQaL__PWaf9mvAuqAK92TKDaBxGtMmwgRwsIrC8U2KnwLYgVYMvJ7Qwpvj6sNg-4cGwpzvzmuj72uLyifWA0UG04b1elPHs44ojYasj4x1ig8u3PUGAjCji-FgKxamzfzjiAKl4ejX5TbcKvCOJVwXJMMP53T1rwk9B1_fX2xyV1sskwqR45gVPE9WnO87yQrOfVdBP_pUxP9uWbB6p3P2-sXIxvEYa6C1VL0STIRB9uPHFj8NjBf2CiDRATd4Fjd4fhL35fUgtoRc5K3UIcRzHKd-Thqu4CJiKxpU_a_E6e4ouYYzTp1y6JFggnKkxBn3JjpXJ3r_w3qOul4BfgsjUfHJRb0HfOL47_5A2kcSxrQYwIps2AtRYTPywTBTFk1Eb7pWhbe6D4RYKOiStnZ-HV2cBqHM4Q'}

@api_view(["POST"])
def get_contracts_and_skus(request):

    r = requests.get('http://sandbox.dimuto.io/api/v5/list-trade-contract-admin/all/1/1/1', headers=headers)

    request_data = r.json()["data"][::-1]

    arr = []

    for data in request_data:

        id = data["id"]
        role = data["role"]
        user_id = data["user_id"]
        currency = data["currency"]
        trade_contract_no = data["trade_contract_no"]

        if(data["purchase_order_no_supplier"] != None and data["purchase_order_no_buyer"] != None):
            reference_no = data["purchase_order_no_buyer"] + ", " + data["purchase_order_no_supplier"]
        else:
            if(data["purchase_order_no_buyer"] != None):
                reference_no = data["purchase_order_no_buyer"]
            else:
                if(data["purchase_order_no_supplier"] != None):
                    reference_no = data["purchase_order_no_supplier"]
                else:
                    reference_no = None
        
        status = data["status"]
        created_at = data["created_at"]
        buyer_name = data["buyer_name"]
        supplier_name = data["supplier_name"]
        name = data["name"]
        company = data["company"]
        total_carton = data["total_carton"]

        total_price = 0.0

        for item in data["product_details"]:

            # sku insert

            # sku_supplier = item["sku"]
            # quantity = item["quantity"]
            # price_buy = item["price_buy"]
            # price_sell = item["price_sell"]

            # sku_data = modify_sku(trade_contract_no, sku_supplier, quantity, price_buy, price_sell, currency)

            # sku_serializer = SKUSerializer(data=sku_data)
            # if sku_serializer.is_valid():
            #     sku_serializer.save()
            #     arr.append(sku_serializer.data)

            if item["price_sell"] != None:
                if float(item["price_sell"]) == 0.0:
                    total_price += float(item["price_buy"])
                else:
                    total_price += float(item["price_sell"])
            else:
                if item["price_buy"] != None:
                    total_price += float(item["price_buy"])

        modified_data = modify_input(id, role, user_id, currency, trade_contract_no, reference_no, status, created_at, buyer_name, supplier_name, name, company, total_carton, total_price)

        serializer = ContractSerializer(data=modified_data)
        if serializer.is_valid():
            serializer.save()
            arr.append(serializer.data)

    return Response(arr)

def modify_sku(trade_contract_no, sku_supplier, quantity, price_buy, price_sell, currency):
    dict = {}
    dict['trade_contract_no'] = trade_contract_no
    dict['sku_supplier'] = sku_supplier
    dict['quantity'] = quantity
    dict['price_buy'] = price_sell
    dict['price_sell'] = price_sell
    dict['currency'] = currency

    return dict

def modify_input(id, role, user_id, currency, trade_contract_no, reference_no, status, created_at, buyer_name, supplier_name, name, company, total_carton, total_price):
    dict = {}
    dict['id'] = id
    dict['role'] = role
    dict['user_id'] = user_id
    dict['currency'] = currency
    dict['trade_contract_no'] = trade_contract_no
    dict['reference_no'] = reference_no
    dict['status'] = status
    dict['create_date'] = created_at
    dict['buyer_name'] = buyer_name
    dict['supplier_name'] = supplier_name
    dict['name'] = name
    dict['company'] = company
    dict['total_carton'] = total_carton
    dict['total_price'] = total_price

    return dict
