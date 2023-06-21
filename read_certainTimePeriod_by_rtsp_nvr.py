import cv2
import logging
import time
import datetime

logging.basicConfig(level=logging.INFO)

def change_event_time(event_time):
    time = ""
    for i in event_time:
        if i != '-' and i != ' ' and i != ':':
            time += i
    time = time[:8] + 't' + time[8:]
    return time

def count_video_duration(s_e_list):
    s_timeStamp = convert_str_to_timeStamp(s_e_list[0])
    e_timeStamp = convert_str_to_timeStamp(s_e_list[1])
    video_duration = e_timeStamp - s_timeStamp
    return video_duration

def convert_str_to_timeStamp(str_time):
    timeArray = time.strptime(str_time,"%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    return timeStamp

def construct_rtsp_url(s_t,e_t):
    user = 'xxx'
    pwd = 'xxx'
    ip_channel = 2
    nvr_ip = 'x.x.x.x'

    rtsp_ip = "rtsp://{0}:{1}@{2}:554/Streaming/tracks/" + str(ip_channel) + "01?starttime=" + s_t + "z&endtime=" + e_t + "z"
    rtsp_url = rtsp_ip.format(user, pwd, nvr_ip)
    return rtsp_url

def collect_frames(rtsp_url):
    read_again = True
    frame_list = []
    fcap = cv2.VideoCapture(rtsp_url)
    i = 0
    while fcap.isOpened():
        ret,frame= fcap.read()
        if not ret:
            if read_again == True:
                read_again = False
                continue
            else:
                # video open failed
                print("failed")
                break
        else:
            i += 1
            print(i)
            frame_list.append(frame)
    return frame_list

def save_video(s_t,e_t,video_duration):
    rtsp_url = construct_rtsp_url(s_t,e_t)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(f'{datetime.date.today()}.avi',fourcc, 25.0, (2688,1520),True)

    fcap = cv2.VideoCapture(rtsp_url)
    num_frame = 25 * video_duration # fcap.get(cv2.CAP_PROP_FRAME_COUNT) -> bug
    logging.info(f'需要读取并保存的总帧数是{num_frame}')

    read_again = True
    count = 0

    # frame_list = []
    while fcap.isOpened() and count < num_frame: 
        ret,frame= fcap.read()
        if not ret:
            if read_again == True:
                read_again = False
                continue
            else:
                # video open failed
                logging.info("视频读取失败！")
                break
        else:
            count += 1
            out.write(frame)
            process = "\r进度:%s\\%s" % (num_frame, count)
            print(process, end='', flush=True)

    fcap.release()
    out.release()
    cv2.destroyAllWindows()

def main(args):
    try:
        s_time = f'{args.s_t[0]} {args.s_t[1]}'
        e_time = f'{args.e_t[0]} {args.e_t[1]}'
        video_duration = count_video_duration([s_time,e_time])

        s_t = change_event_time(s_time)
        e_t = change_event_time(e_time)
        save_video(s_t,e_t,video_duration)

    except Exception as e:
        logging.error(e)


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="please input start time and end time.")

    # python3 read_certainTimePeriod_by_rtsp_nvr.py --s_t 2023-03-12 09:05:00 --e_t 2023-03-12 09:06:00
    parser.add_argument("--s_t", '--s_aux',  nargs='+', default="2023-01-01 09:00:00", help="start time")
    parser.add_argument("--e_t", '--e_aux',  nargs='+', default="2023-02-28 09:05:00", help="end time")

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parse_args()
    main(args)
