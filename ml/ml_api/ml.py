import io
import json
import requests
from .ml_class import *

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

# Import utilites
from .utils import label_map_util
from .utils import visualization_utils as vis_util
import random

#Shrimp_utility_class
cv_func = CV_utility()

#initialization
random_value = random.randint(1,100)
count = 0
count1= 0
new = 0 

#TF OD Model Path
CWD_PATH = os.getcwd()
OD_model_path = 'ml_api/inference_graph'
pb_graph = 'saved_model.pb'
labelmap_path='label_map.pbtxt'
num_classes= 1

headers = {'Content-Type': 'application/json', 'Accept':'application/json', 'Authorization' : "Token e6eadf4924cf1dcba72e8610de60a2a08aa06a3b"}

class ResponseThen(Response):
    def __init__(self, data, then_callback, **kwargs):
        super().__init__(data, **kwargs)
        self.then_callback = then_callback

    def close(self):
        super().close()
        self.then_callback()

@api_view(["POST"])
def get_prediction(request):

    #Object Detection
    OD_func = TF_inference_OD(OD_model_path,pb_graph,labelmap_path,num_classes)                   
    #Declare OD API Class
    arr = OD_func.object_detection_inference(request)
    
    def do_after():
        r = requests.patch('http://localhost:7000/images/update/', data=json.dumps(arr), headers=headers)

    return ResponseThen(arr, do_after, status=status.HTTP_200_OK)
