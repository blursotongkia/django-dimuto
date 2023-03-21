import os
import sys
import time
import base64
import datetime
import shutil
import glob
import math
import random
import requests

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing.image import load_img
import cv2

from PIL import Image
from random import randrange
from PIL import Image, ImageDraw, ImageFilter
import argparse

from .utils import label_map_util
from .utils import visualization_utils as vis_util

#TF OD Model Path
CWD_PATH = os.getcwd()

class regression_keras_utility():
    def __init__(self):
        pass

    def load_model(self,path):
        model = tf.keras.models.load_model(path)
        return model
    
    def preprocess_reg(self,reg_input):
        print(reg_input.shape)
        reg_input = cv2.resize(reg_input,(448,448))
        reg_input = np.array(reg_input)
        x = np.expand_dims(reg_input, axis=0)
        print(x.shape)

        predict_datagen = ImageDataGenerator(rescale=1/255,
                                      samplewise_center=True, #Set each sample mean to 0.
                                      samplewise_std_normalization= True) 

        preprocess = predict_datagen.flow(x, batch_size=1)
        batch = preprocess.next()
        batch = batch[0].astype('float16')
        batch = np.expand_dims(batch, axis=0)

        batch = np.vstack([batch])
        return batch

    def _generator(self,dataset_path,target_size=(448,448)):
        print(f"Load Dataset \t => {dataset_path}")
        new_test_datagen = ImageDataGenerator(rescale=1/255,
                                      samplewise_center=True, #Set each sample mean to 0.
                                      samplewise_std_normalization= True) 
        new_test_generator=new_test_datagen.flow_from_directory(directory=f"{dataset_path}",
                                            batch_size=1,
                                            shuffle= False,
                                            target_size=(448,448))
        return new_test_generator

    def predict_weight(self,model,dataset_generator,maxWeight=13.52):
        pred=model.predict(dataset_generator,verbose=1,steps=dataset_generator.samples)
        pred_final = pred * maxWeight
        return abs(pred_final)

    

class I_O_utility():
    def __init__(self):
        pass

    def get_file_paths(self,dir_list):
        file_paths = []  
        for element in dir_list:
            for root, directories, files in os.walk(element):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    file_paths.append(filepath)  
        return file_paths
    
    
    def check_file_ext(self,file,format1=".jpg",format2=".png",printF=False):
        (filepath, ext) = os.path.splitext(file)        # get the file extension
        file_name = os.path.basename(file)              # get the basename for writing to output file
        if ext == format1 or ext == format2:                              # only interested if extension is '.wav'
            path = os.path.join(os.getcwd(),file)
            if printF == True:
                print(f'image_name \t => {file_name}') 
                return path , file_name
            else:
                return path , file_name


class CV_utility():
    def __init__(self):
        pass

    def resize_frame(self,img,scale_percent=50,show=False):
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

        if show:
            try:
                cv2.imshow("result frame",resized)
                cv2.waitKey(0) 
            except KeyboardInterrupt:
                cv2.destroyAllWindows()
                print('existing program')

        return resized

    def write_result(self,frame,filename,main_folder,sub_folder):
        current_path = os.getcwd()
        path = f'{current_path}/{main_folder}/{sub_folder}/'

        try:
            os.makedirs(path)
            cv2.imwrite(f"{path}/{filename}",frame)
        except FileExistsError:
            print(f"Folder exists, Saving to the exsiting path {path}")
            cv2.imwrite(f"{path}/{filename}",frame)
            pass
        except OSError:
            print("Error occuring creating directory")
        else:
            print(f"Result Folder created in {path}")

        return path

    def create_blank(self,width, height, rgb_color = (0,0,0)):
        image = np.zeros((height, width,3), np.uint8)
        color = tuple(reversed(rgb_color))
        image[:] = color
        return image    


class TF_inference_OD():
    def __init__(self,OD_model_path,pb_graph,labelmap_path,num_classes):
        self.OD_model_path = OD_model_path
        self.pb_graph = pb_graph
        self.labelmap_path = labelmap_path
        self.num_classes = num_classes

    def object_detection_inference(self, request):

        # Path to frozen detection graph .pb file, which contains the model that is used for object detection.
        CWD_PATH = os.getcwd()
        PATH_TO_CKPT = os.path.join(CWD_PATH, self.OD_model_path)
        PATH_TO_CKPT = PATH_TO_CKPT.replace('\\','/')
        model_2_path = '/home/ubuntu/django/ml_api/inference_graph/model 2'

        #loading models
        model_1 = tf.saved_model.load(PATH_TO_CKPT)
        model_2 = tf.saved_model.load(model_2_path)

        arr = []
        email = request.data[0]["email"]
        name = request.data[0]["name"]
        role = request.data[0]["role"]
        trade_contract_no = request.data[0]["trade_contract_no"]
        request.data.pop(0)

        for item in request.data:

            id = item['id']
            image = item['image']
            frame = Image.open(requests.get(image, stream=True).raw)

            width, height = frame.size

            if(width < 600 or height < 600):
                self.labelmap_path = "multi_label_map.pbtxt"
                self.num_classes = 6
        
                category_index = label_map_util.create_category_index_from_labelmap(self.labelmap_path,
                                                                    use_display_name=True)

                class_dict = {
                    1 : "blemish", 
                    2 : "unripe", 
                    3 : "almost ripe", 
                    4 : "ripe", 
                    5 : "overripe", 
                    6 : "rotten"
                }

                result_dict = {
                    "blemish" : 0,
                    "unripe" : 0,
                    "almost ripe" : 0,
                    "ripe" : 0,
                    "overripe" : 0,
                    "rotten" : 0
                }

                image_np = np.array(frame)
                image_tensor = tf.convert_to_tensor(image_np)
                input_tensor = tf.expand_dims(image_tensor, 0)

                detections = model_2(input_tensor)
                num_detections = int(detections.pop('num_detections'))
                detections = {key: value[0, :num_detections].numpy()
                            for key, value in detections.items()}
                # detection_classes should be ints.
                detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

                isCounted = 0
                score_list = []
                for i in range(detections['detection_boxes'].shape[0]):
                    if detections['detection_classes'][i].item() in class_dict:
                        if detections['detection_classes'][i].item() != 1:
                            if detections['detection_scores'] is None or detections['detection_scores'][i].item() > 0.3:    
                                    class_name, score = class_dict[detections['detection_classes'][i]], detections['detection_scores'][i]
                                    score_list.append([class_name, score])
                        else:
                            if detections['detection_scores'] is None or detections['detection_scores'][i].item() > 0.2:
                                if detections['detection_classes'][i] == "blemish" and isCounted == 0:
                                    result_dict["blemish"] += 1
                                    isCounted = 1
                if len(score_list) != 0:
                    score_list.sort(key=lambda x: x[1], reverse=True)
                    result_dict[score_list[0][0]] += 1
                    num_of_detections = 1
                    print(score_list)
                else:
                    num_of_detections = 0
                
                arr.append({"id" : id, "quantity" : num_of_detections, "predicted_image" : "", "email" : email, "name" : name, "trade_contract_no" : trade_contract_no, 
                        "role" : role, "blemished_avocados" : result_dict["blemish"], "unripe" : result_dict["unripe"], "almost_ripe" : result_dict["almost ripe"], 
                        "ripe" : result_dict["ripe"], "overripe" : result_dict["overripe"], "rotten" : result_dict["rotten"], 
                })
            else:
                # getting image from path and converting image to tensor
                image_np = np.array(frame)
                image_tensor = tf.convert_to_tensor(image_np)
                input_tensor = tf.expand_dims(image_tensor, 0)

                self.labelmap_path = "label_map.pbtxt"
                self.num_classes = 1

                category_index = label_map_util.create_category_index_from_labelmap(self.labelmap_path,
                                                                    use_display_name=True)

                detections = model_1(input_tensor)
                num_detections = int(detections.pop('num_detections'))
                detections = {key: value[0, :num_detections].numpy()
                            for key, value in detections.items()}
                detections['num_detections'] = num_detections
                # detection_classes should be ints.
                detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

                timestr = time.strftime("%Y%m%d-%H%M%S")

                os.mkdir("/home/ubuntu/django/ml_api/files/cropped/" + str(id) + '_' + timestr)
                num_of_detections = 0
                for i in range(detections['detection_boxes'].shape[0]):
                    if detections['detection_scores'] is None or detections['detection_scores'][i] > 0.9:
                        box = tuple(detections['detection_boxes'][i].tolist())
                        ymin, xmin, ymax, xmax = box

                        img_name = str(id) + "_" + str(i+1)
                        crop_box = (int(xmin * image_np.shape[1]), int(ymin * image_np.shape[0]), int(xmax * image_np.shape[1]), int(ymax * image_np.shape[0]))
                        crop_box = map(int, crop_box)
                        im = frame.crop((crop_box))
                        im.save('/home/ubuntu/django/ml_api/files/cropped/' + str(id) + '_' + timestr + '/' + img_name + '.jpg')

                        num_of_detections += 1

                image_np_with_detections = image_np.copy()

                #visualising
                vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np_with_detections,
                    detections['detection_boxes'],
                    detections['detection_classes'],
                    detections['detection_scores'],
                    category_index,
                    use_normalized_coordinates=True,
                    max_boxes_to_draw=200,
                    min_score_thresh=.80,
                    agnostic_mode=False)

                img = cv2.cvtColor(image_np_with_detections, cv2.COLOR_RGB2BGR)
                ret, pred_img = cv2.imencode('.jpg', img)
                encoded_img = base64.b64encode(pred_img)
                encoded_str = encoded_img.decode()

                self.labelmap_path = "multi_label_map.pbtxt"
                self.num_classes = 6
            
                category_index = label_map_util.create_category_index_from_labelmap(self.labelmap_path,
                                                                    use_display_name=True)

                class_dict = {
                    1 : "blemish", 
                    2 : "unripe", 
                    3 : "almost ripe", 
                    4 : "ripe", 
                    5 : "overripe", 
                    6 : "rotten"
                }

                result_dict = {
                    "blemish" : 0,
                    "unripe" : 0,
                    "almost ripe" : 0,
                    "ripe" : 0,
                    "overripe" : 0,
                    "rotten" : 0
                }

                list_of_imgs = os.listdir("/home/ubuntu/django/ml_api/files/cropped/" + str(id) + '_' + timestr)
                for img_ in list_of_imgs:
                    # getting image from path and converting image to tensor
                    frame = Image.open(os.path.join("/home/ubuntu/django/ml_api/files/cropped/" + str(id) + '_' + timestr, img_))
                    image_np = np.array(frame)
                    image_tensor = tf.convert_to_tensor(image_np)
                    input_tensor = tf.expand_dims(image_tensor, 0)

                    detections = model_2(input_tensor)
                    num_detections = int(detections.pop('num_detections'))
                    detections = {key: value[0, :num_detections].numpy()
                                for key, value in detections.items()}
                    # detection_classes should be ints.
                    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

                    isCounted = 0
                    score_list = []
                    for i in range(detections['detection_boxes'].shape[0]):
                        if detections['detection_classes'][i].item() in class_dict:
                            if detections['detection_classes'][i].item() != 1:
                                if detections['detection_scores'] is None or detections['detection_scores'][i].item() > 0.35:    
                                        class_name, score = class_dict[detections['detection_classes'][i]], detections['detection_scores'][i]
                                        score_list.append([class_name, score])
                            else:
                                if detections['detection_scores'] is None or detections['detection_scores'][i].item() > 0.2:
                                    if detections['detection_classes'][i] == "blemish" and isCounted == 0:
                                        result_dict["blemish"] += 1
                                        isCounted = 1
                    if len(score_list) != 0:
                        score_list.sort(key=lambda x: x[1], reverse=True)
                        result_dict[score_list[0][0]] += 1

                arr.append({"id" : id, "quantity" : num_of_detections, "predicted_image" : encoded_str, "email" : email, "name" : name, "trade_contract_no" : trade_contract_no, 
                            "role" : role, "blemished_avocados" : result_dict["blemish"], "unripe" : result_dict["unripe"], "almost_ripe" : result_dict["almost ripe"], 
                            "ripe" : result_dict["ripe"], "overripe" : result_dict["overripe"], "rotten" : result_dict["rotten"], 
                })

        return arr
            
    def generate_category_index(self):
        label_map = label_map_util.load_labelmap(os.path.join(CWD_PATH,self.OD_model_path,self.labelmap_path))
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=self.num_classes, use_display_name=True)
        category_index = label_map_util.create_category_index(categories)
        return category_index

    def label_encode(self,classid):
        category_index = self.generate_category_index()
        classes = category_index[classid]["name"]
        return classes

    def OD_encode(self,frame,raw_classes,raw_scores,raw_boxes):
        height,width,channel = frame.shape
        nprehit = raw_scores.shape[1] # 2nd array dimension
        i = 0
        for j in range(nprehit):
            classid = int(raw_classes[i][j])
            classes = self.label_encode(classid)
            scores = raw_scores[i][j]
            bbox = raw_boxes[i][j]      
            b0r = int(bbox[0]*height)            #ymin,xmin,ymax,xmax
            b1r = int(bbox[1]*width)
            b2r = int(bbox[2]*height)
            b3r = int(bbox[3]*width)      
            bbox = [b0r,b1r,b2r,b3r]
            return classes,scores,bbox

    def visualize_result(self,frame,boxes,scores,classes,num):
        category_index = self.generate_category_index()
        # Draw the results of the detection (aka 'visulaize the results')
        vis_util.visualize_boxes_and_labels_on_image_array(
            frame,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            line_thickness=2,
            min_score_thresh=0.85)

        return frame