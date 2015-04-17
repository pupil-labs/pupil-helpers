import numpy as np
import cv2
import cPickle as pickle
import os
import csv

"""
Simple utility script that calculates the positions of markers from the surface metrics reports
using the `m_to_screen` transformation matrix and writes to a csv file.  
"""


def denormalize(pos, (width, height), flip_y=False):
    """
    denormalize
    """
    x = pos[0]
    y = pos[1]
    x *= width
    if flip_y:
        y = 1-y
    y *= height
    return x,y

def load_object(file_path):
    file_path = os.path.expanduser(file_path)
    with open(file_path,'rb') as fh:
        return pickle.load(fh)

def ref_surface_to_img(pos,m_to_screen):
    shape = pos.shape
    pos.shape = (-1,1,2)
    new_pos = cv2.perspectiveTransform(pos,m_to_screen )
    new_pos.shape = shape
    return new_pos

def get_marker_positions_pixels(surf_data_file):
    corners = [[0,0],[0,1],[1,1],[1,0]]
    data = []
    for d,i in zip(srf_data_file,range(len(srf_data_file))):
        if d is not None:
            data.append([i,[denormalize(ref_surface_to_img(np.array(c,dtype=np.float32),d['m_to_screen']),(1280,720)) for c in corners]])
        else:
            data.append([i,None])    
    return data


def write_csv(file_path, data, csv_file_name="marker_positions_pixels.csv"):
    with open(os.path.join(os.path.expanduser(file_path),csv_file_name),'wb') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter='\t',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(('frame_number', 'marker_positions_in_pixels'))
        for i in data:
            csv_writer.writerow((i[0],i[1]))


if __name__ == '__main__':
    # change the below variables for your recording directory
    data_dir = "~/Desktop/Sandbox/Marker_Demo_Unboxing"
    metrics_dir = "metrics_0-5993"
    metrics_file = "srf_positions_box_front"

    srf_data_file = load_object(os.path.join(data_dir,metrics_dir,metrics_file))
    write_csv(os.path.join(data_dir,metrics_dir),get_marker_positions_pixels(srf_data_file))
