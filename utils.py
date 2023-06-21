import cv2

def test_rtsp(rtsp_url):
    fcap = cv2.VideoCapture(rtsp_url)
    # fcap.set(cv2.CAP_PROP_FPS, 25)
    while fcap.isOpened():
        ret,frame = fcap.read()
        cv2.imshow("frame",frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
    fcap.release()

def get_rtsp_info(rtsp_url):
    '''
    set(cv2.CAP_PROP_POS_FRAMES, 200) 读取指定帧
    set(cv2.CAP_PROP_FPS, 25) 设置帧率
    '''
    capture = cv2.VideoCapture(rtsp_url)
    fps = capture.get(cv2.CAP_PROP_FPS)
    size = (int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
    capture.release()