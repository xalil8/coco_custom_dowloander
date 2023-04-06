import sys, getopt
import argparse
from pycocotools.coco import COCO
import requests
import os
import json
from os import listdir, getcwd
from os.path import join
from functools import reduce
from random import shuffle

def filter_coco(T):
    return (coco_names.index(T[0]) + 1)

def convert(size,box):
    dw = 1./size[0]
    dh = 1./size[1]
    xmin = box[0]
    ymin = box[1]
    xmax = box[2] + box[0]
    ymax = box[3] + box[1]
            
    x = (xmin + xmax)/2
    y = (ymin + ymax)/2     
    w = xmax - xmin
    h = ymax-ymin
            
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h,)

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def download_coco(catid, catname, desired_class_id, download_limit):
    print("Starting Thread for " + catname)
    imgIds = coco.getImgIds(catIds=[catid])
    images = coco.loadImgs(imgIds)
    print(str(len(images)) + " Images found for " + catname)
    ann_ids = coco.getAnnIds(catIds=[catid], iscrowd=None)
    all_ann = coco.loadAnns(ann_ids)
    print(str(len(all_ann)) + " Annotations found for "+ catname)
    print("Download Started...! Category: "+ catname)  
    counter = 0

    for im in images:
        if counter == download_limit:
            print("Limit of " + str(counter) + " Images download for class "  +".")
            break
        image_id = im['id']
        width = im['width']
        height = im['height']
        filename = im["file_name"]


        if os.path.isfile(str(output_folder + filename)):
            print("Skipping... "+str(output_folder + filename))
            continue


        all_annotations = list(filter(lambda item1: item1['image_id'] == image_id,all_ann))
        annotations = list(filter(lambda item3: item3['category_id'] == catid, all_annotations))
        if annotations:
            counter += 1
            with open(output_folder +'%s.txt'%(filename[:-4]), 'a+') as outfile:
                for annotation in annotations:
                    box = annotation['bbox']
                    bb = convert((width,height),box)
                    outfile.write(str(desired_class_id)+" "+" ".join([str(b) for b in bb]) + '\n')
                    
            outfile.close()
            img_data = requests.get(im['coco_url']).content
            with open(output_folder + filename, 'wb') as handler:
                handler.write(img_data)
    print("Download Completed! Category: "+ catname)    
    
    
def main():
    global coco_names
    global output_folder  
    global coco
    global category_ids
    global category_names

    coco_names = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
                  'fire hydrant', 'street sign', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 
                  'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'hat', 'backpack', 'umbrella', 'shoe', 
                  'eye glasses', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 
                  'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'plate', 
                  'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 
                  'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
                  'mirror', 'dining table', 'window', 'desk', 'toilet', 'door', 'tv', 'laptop', 'mouse', 'remote', 
                  'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'blender', 'book', 
                  'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush', 'hair brush']
    

    ##################### ENTER CONF PARAMETERS HERE ###################
    coco = COCO('instances_val2017.json')
    categories_intrest = [["car",0],["truck",1]]
    output_folder = "/home/jovyan/xalil/coco/outputs/"
    image_limit_per_class = 5
    ####################################################################

    
    
    
    category_ids = list(map(filter_coco, categories_intrest))  
    category_names = [row[0] for row in categories_intrest]
    catIds = coco.getCatIds(catNms=category_names)
    os.makedirs(output_folder, exist_ok=True) 

    for catid in catIds:
        catname = coco_names[catid - 1]
        desired_class_id = [x for x in categories_intrest if str(catname) in x][0][1]
        download_coco(catid,catname,desired_class_id,image_limit_per_class)
        imgIds = coco.getImgIds(catIds=[catid])


if __name__ == "__main__": 
    main() 
    print("process Done")