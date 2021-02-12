import time

import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
detector_params = cv2.SimpleBlobDetector_Params()
detector_params.filterByArea = True
detector_params.maxArea = 1500
detector = cv2.SimpleBlobDetector_create(detector_params)


def detect_faces(img, cascade):
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    coords = cascade.detectMultiScale(gray_frame, 1.3, 5)
    if len(coords) > 1:
        biggest = (0, 0, 0, 0)
        for i in coords:
            if i[3] > biggest[3]:
                biggest = i
        biggest = np.array([i], np.int32)
    elif len(coords) == 1:
        biggest = coords
    else:
        return None
    for (x, y, w, h) in biggest:
        frame = img[y:y + h, x:x + w]
    return frame


def detect_eyes(img, cascade):
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    eyes = cascade.detectMultiScale(gray_frame, 1.3, 5)  # detect eyes
    width = np.size(img, 1)  # get face frame width
    height = np.size(img, 0)  # get face frame height
    left_eye = None
    right_eye = None
    for (x, y, w, h) in eyes:
        if y > height / 2:
            pass
        eyecenter = x + w / 2  # get the eye center
        if eyecenter < width * 0.5:
            left_eye = img[y:y + h, x:x + w]
        else:
            right_eye = img[y:y + h, x:x + w]
    return left_eye, right_eye


def cut_eyebrows(img):
    height, width = img.shape[:2]
    eyebrow_h = int(height / 4)
    img = img[eyebrow_h:height, 0:width]  # cut eyebrows out (15 px)

    return img


def blob_process(img, threshold, detector):
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(gray_frame, threshold, 255, cv2.THRESH_BINARY)
    img = cv2.erode(img, None, iterations=2)
    img = cv2.dilate(img, None, iterations=4)
    img = cv2.medianBlur(img, 5)
    keypoints = detector.detect(img)
    return keypoints


def nothing(x):
    pass


def main():
    cap = cv2.VideoCapture(1)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640, 480))

    cv2.namedWindow('image')
    cv2.createTrackbar('left', 'image', 0, 255, nothing)
    cv2.createTrackbar('right', 'image', 0, 255, nothing)

    count = 0
    sum = 0
    countdown = 0
    countup = 0
    cd = 0
    while True:
        _, frame = cap.read()
        face_frame = detect_faces(frame, face_cascade)
        if face_frame is not None:
            countup = 0
            hf,wf = face_frame.shape[:2]
            cv2.rectangle(face_frame, (0,0), (hf,wf),(255,0,255),2)
            eyes = detect_eyes(face_frame, eye_cascade)
            for eye in eyes:
                if eye is not None:
                    threshold = 42
                    eye = cut_eyebrows(eye)
                    #print(eye)
                    keypoints = blob_process(eye, threshold, detector)
                    h,w = eye.shape[:2]
                    cv2.rectangle(eye,(0,0),(h+10,w -20),(255,255,0),2)
                    eye = cv2.drawKeypoints(eye, keypoints, eye, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                    coord_pts_x = ([keypoints[idx].pt[0] for idx in range(0, len(keypoints))])
                    if coord_pts_x != []:
                        count += 1
                        sum += coord_pts_x[0]
                        #print(coord_pts_x)
                        if count == 30:
                            avg = sum / 30
                            print(avg)
                            count = 0
                            sum = 0
                            left = cv2.getTrackbarPos('left', 'image')
                            right = cv2.getTrackbarPos('right', 'image')
                            if avg >= right or avg <= left:
                                cd += 30
        else:
            countup += 1
            if countup > 20:
                if countdown == 0:
                    countdown += 5
        if cd > 0:
            cv2.putText(frame, 'Not Paying Attention', (50, 75), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2,
                        (255, 255, 255), 2, cv2.LINE_AA)
            cd -= 1
        if countdown > 0:
            cv2.putText(frame, 'Please Return', (50, 75), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2,
                        (255, 255, 255), 2, cv2.LINE_AA)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            out.write(frame)
            countdown -= 1

        cv2.imshow('image', frame)
        out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()