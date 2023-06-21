import os
import cv2
import queue
import logging
import adjuster
import numpy as np
from sort import Sort
from datetime import datetime
from knnDetector import knnDetector
logging.basicConfig(level=logging.INFO)

# RTSP_IP = os.environ["RTSP_IP"] if "RTSP_IP" in os.environ else 'xx'
# rtsp_url = f"rtsp://admin:xx@{RTSP_IP}:554/Streaming/Channels/101"

frame_list = []

def save_video():
    num_frame = len(frame_list)
    if num_frame <= 50:
        logging.info("This is a fake alarm. Do not save alarm.")
    else:
        logging.info(f"The total number of frames to save is {num_frame}.")
        frame_shape = frame_list[0].shape
        size = (frame_shape[1], frame_shape[0])
        video_name = datetime.now().strftime("%Y_%m_%d_%H_%M")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(f'{video_name}.avi',fourcc, 25.0, size)
        count = 0
        for frame in frame_list:
            count += 1
            out.write(frame)
            process = "\rprocess:%s\\%s" % (num_frame, count)
            print(process, end='', flush=True)
        frame_list.clear()
        logging.info("The alarm video has been saved.")

def start_detect(rtsp_url):
    fcap = cv2.VideoCapture(rtsp_url)
    fcap.set(cv2.CAP_PROP_FPS, 25)

    detector = knnDetector(history=500, dist2Threshold=400, minArea=10)
    sort = Sort(max_age=3, min_hits=5, iou_threshold=0.1)
    ret,frame = fcap.read()
    adjust = adjuster.Adjuster(start_image=frame, edge=(120, 60))
    
    isAlarm = False
    consecutive_valid_frame = queue.Queue(3) # 连续三帧都检测到才会触发报警
    consecutive_invalid_frame = queue.Queue(3) # 当触发报警之后，如果连续三帧没有检测到，就认为这个报警结束

    while fcap.isOpened():
        ret,frame = fcap.read()
        if frame is None:
            continue

        frame = adjust.debouncing(frame)
        mask, bboxs = detector.detectOneFrame(frame)

        if bboxs != []:
            bboxs = np.array(bboxs)
            bboxs[:, 2:4] += bboxs[:, 0:2]
            trackBox = sort.update(bboxs)
        else:
            trackBox = sort.update()

        if isAlarm == False:
            consecutive_valid_frame.put(len(trackBox))
            print(f'valid: {consecutive_valid_frame.queue}')
            if consecutive_valid_frame.full() == True:
                min_item = 100
                for item in consecutive_valid_frame.queue:
                    if item < min_item:
                        min_item = item
                if min_item == 0:
                    consecutive_valid_frame.get()
                else:
                    isAlarm = True
                    consecutive_valid_frame.queue.clear()
                    logging.info("Trigger an alarm.")

        else:
                for bbox in trackBox:
                    bbox = [int(bbox[i]) for i in range(5)]
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 6)
                    cv2.putText(frame, str(bbox[4]), (bbox[0], bbox[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
                frame_list.append(frame)

                consecutive_invalid_frame.put(len(trackBox))
                print(f'invalid: {consecutive_invalid_frame.queue}')
                if consecutive_invalid_frame.full() == True:
                    count = 0
                    for item in consecutive_invalid_frame.queue:
                        if item == 0:
                            count += 1
                    if count == 3:
                        isAlarm = False
                        consecutive_invalid_frame.queue.clear()
                        logging.info("Start saving the alarm video...")
                        save_video()
                    else:
                        consecutive_invalid_frame.get()

if __name__ == '__main__':
    # logging.info(rtsp_url)
    # get_rtsp_info()
    # test_rtsp()
    
    test_video_path = path = "IMG_4550.MOV"
    start_detect(test_video_path)
    save_video()
    
    