import json
import requests
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
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

@api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def email(request):

    email = dict(request.data)["email"]
    name = dict(request.data)["name"]
    role = dict(request.data)["role"]
    trade_contract_no = dict(request.data)["trade_contract_no"]
    subject = 'Avocados - Uploaded Images Update'
    message = 'Hi {name}, the images that you have uploaded for {trade_contract_no} have finished successfully. Please log in to your account to see the results now!'.format(name=name, trade_contract_no=trade_contract_no)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

    avocados_dict = {
        "trade_contract_no" : trade_contract_no, "role" : role,
        "blemished_pc" : dict(request.data)["blemished_pc"], "unripe_pc" : dict(request.data)["unripe_pc"], "almost_ripe_pc" : dict(request.data)["almost_ripe_pc"],
        "ripe_pc" : dict(request.data)["ripe_pc"], "overripe_pc" : dict(request.data)["overripe_pc"], "rotten_pc" : dict(request.data)["rotten_pc"],
        "total_blemished" : dict(request.data)["total_blemished"], "total_unripe" : dict(request.data)["total_unripe"], "total_almost_ripe" : dict(request.data)["total_almost_ripe"],
        "total_ripe" : dict(request.data)["total_ripe"], "total_overripe" : dict(request.data)["total_overripe"], "total_rotten" : dict(request.data)["total_rotten"],
        "total_quantity" : dict(request.data)["total_quantity"]
    }

    def do_next():
        headers = {'Content-Type': 'application/json', 'Accept':'application/json', 'Authorization' : "Token e6eadf4924cf1dcba72e8610de60a2a08aa06a3b"}
        r = requests.post('http://www.avocados.live/avocados', data=json.dumps(avocados_dict), headers=headers)
    
    return ResponseThen({"message": "Email successfully sent!"}, do_next, status=status.HTTP_200_OK)