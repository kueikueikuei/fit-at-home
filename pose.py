from argparse import ArgumentParser, SUPPRESS
import json
import os

import cv2
import numpy as np

from modules.inference_engine import InferenceEngine
from modules.input_reader import InputReader
from modules.draw import draw_poses
from modules.parse_poses import parse_poses
import datetime
import math

import wx

def angle(cen, first, second):
    M_PI = 3.1415926535897
    if first[0]<0 and second[0]<0:
        return 0
  
    ma_x = first[0] - cen[0] 
    ma_y = first[1] - cen[1] 
    mb_x = second[0] - cen[0]
    mb_y = second[1] - cen[1]
    v1 = (ma_x * mb_x) + (ma_y * mb_y)
    ma_val = math.sqrt(ma_x * ma_x + ma_y * ma_y) 
    mb_val = math.sqrt(mb_x * mb_x + mb_y * mb_y)
    cosM = v1 / (ma_val * mb_val)
    angleAMB = math.acos(cosM) * 180 / M_PI
    return angleAMB
def slop(x1,x2):
    k=9999
    if (x2[0] - x1[0])!=0:
        k = (x2[1] - x1[1])/(x2[0] - x1[0])
    return abs(k)
def euclidean(x,y):
    return np.linalg.norm(x-y)
def count_jumpup(poses_2d,up,count):
    
    for pose in poses_2d:
        pose = np.array(pose[0:-1]).reshape((-1, 3)).transpose()
        if pose[1,5]<pose[1,18] and pose[1,11]<pose[1,17] and angle(pose[0:2,0],pose[0:2,8],pose[0:2,14])>20 and pose[0,8] > 0 and pose[0,14] > 0:
            up=True
        elif pose[1,5]>pose[1,18] and pose[1,11]>pose[1,17] and angle(pose[0:2,0],pose[0:2,8],pose[0:2,14])<10 and pose[0,8] > 0 and pose[0,14] > 0 and up==True:
            up=False
            count+=1
            #print(count)
    return up,count
def count_situp(poses_2d,up,count):
    
    for pose in poses_2d:
        pose = np.array(pose[0:-1]).reshape((-1, 3)).transpose()
        if (euclidean(pose[0:2,1],pose[0:2,7])<150 and euclidean(pose[0:2,1],pose[0:2,13])<150) and pose[0,12] > 0 and pose[0,13] > 0 and  pose[0,6] > 0 and pose[0,7] > 0 and up==False:
            count+=1
            up=True
        elif (euclidean(pose[0:2,1],pose[0:2,7])>150 and euclidean(pose[0:2,1],pose[0:2,13])>150) and pose[0,12] > 0 and pose[0,13] > 0 and  pose[0,6] > 0 and pose[0,7] > 0 and up==True:
            up=False
    return up,count
def count_squat(poses_2d,up,count):
    for pose in poses_2d:
        pose = np.array(pose[0:-1]).reshape((-1, 3)).transpose()
        if (slop(pose[0:2,6],pose[0:2,7])<0.5 and slop(pose[0:2,12],pose[0:2,13])<0.5) and up==False:
            count+=1
            #print(count)
#             print(slop(pose[0:2,6],pose[0:2,7]))
            up=True
        elif (slop(pose[0:2,6],pose[0:2,7])>2 and slop(pose[0:2,12],pose[0:2,13])>2)  and up==True:
            up=False
#             print(slop(pose[0:2,6],pose[0:2,7]))
    return up,count
def run_video(pathtofile, motion):
    assert motion in ('jumpingjack','situp','squat')
    model = "human-pose-estimation-0001.xml"
    device = "CPU"
    stride = 8
    fx = -1
    base_height = 256
    inference_engine = InferenceEngine(model, device, stride)
    frame_provider = InputReader([pathtofile])
    is_video = frame_provider.is_video
    first=True
    up=False
    count=0
    counts_by_frame=[]
    total_frame = frame_provider.length()
    if total_frame<30:
        total_frame = 30
    dialog = wx.ProgressDialog("Progress", "Video processing...", total_frame, style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE) 
    for frame in frame_provider:
        if first:
            out = cv2.VideoWriter(pathtofile+'_output.avi',cv2.VideoWriter_fourcc(*"MJPG"), 20.0, (int(frame.shape[1]),int(frame.shape[0])))
            first=False
        input_scale = base_height / frame.shape[0]
        scaled_img = cv2.resize(frame, dsize=None, fx=input_scale, fy=input_scale)
        inference_result = inference_engine.infer(scaled_img)
        poses_2d = parse_poses(inference_result, input_scale, stride, fx, is_video)
        draw_poses(frame, poses_2d)
        if motion=="jumpingjack":
            up,count = count_jumpup(poses_2d,up,count)
        elif motion=="situp":
            up,count = count_situp(poses_2d,up,count)
        elif motion=="squat":
            up,count = count_squat(poses_2d,up,count)
        counts_by_frame.append(count)
        out.write(frame.astype('uint8'))
        dialog.Update(len(counts_by_frame))
    
    dialog.Update(total_frame)
    out.release()
    cv2.destroyAllWindows()
    dialog.Destroy()
    return pathtofile+'_output.avi',counts_by_frame
def run_cam(motion):
    assert motion in ('jumpup','situp','squat')
    model = "human-pose-estimation-0001.xml"
    device = "CPU"
    stride = 8
    fx = -1
    base_height = 256
    inference_engine = InferenceEngine(model, device,stride)
    frame_provider = InputReader(["1"])
    is_video = frame_provider.is_video
    up=False
    count=0
    for frame in frame_provider:
        
        input_scale = base_height / frame.shape[0]
        scaled_img = cv2.resize(frame, dsize=None, fx=input_scale, fy=input_scale)
        inference_result = inference_engine.infer(scaled_img)
        poses_2d = parse_poses(inference_result, input_scale, stride, fx, is_video)
        draw_poses(frame, poses_2d)
        if motion=="jumpup":
            up,count = count_jumpup(poses_2d,up,count)
        elif motion=="situp":
            up,count = count_situp(poses_2d,up,count)
        elif motion=="squat":
            up,count = count_squat(poses_2d,up,count)
        cv2.imshow('3D Human Pose Estimation', frame)
        if 0xFF & cv2.waitKey(5)==27:
            break
    cv2.destroyAllWindows()
if __name__ == '__main__':
    motion = 'situp'#,'jumpup','squat'
    # webcam 會用opencv自動產生一個視窗秀出及時的骨架
    run_cam(motion)
    """
    outputfile str 路徑+檔名
    counts_by_frame list(int) 每個frame的次數
    """
    outputfile,counts_by_frame = run_video(pathtofile,filename, motion)
    