from PIL import Image
import cv2


def split_frames(video_file):
    cap = cv2.VideoCapture(video_file)
    num = 1
    while num:
        success, data = cap.read()
        if not success:
            break
        if num % 5 == 0:
            im = Image.fromarray(data)
            im.save("./images/" + str(num) + ".jpg")
            cv2.waitKey(1)
        num += 1
    cap.release()
    return num


split_frames("./cc.mp4")
