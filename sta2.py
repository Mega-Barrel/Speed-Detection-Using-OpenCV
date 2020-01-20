import numpy as np
import cv2
import timeit
import datetime
import os
import time

speed_limit = int(input('Enter The Speed Limit: '))

# Initialize the video
cap = cv2.VideoCapture('test1.mp4')
lane_1_1 = []
lane_1_2 = []

mask1 = cv2.imread('m1.jpeg')
mask1 = cv2.cvtColor(mask1, cv2.COLOR_BGR2GRAY)
ret1, thresh_MASK_1 = cv2.threshold(mask1, 127, 255, cv2.THRESH_BINARY_INV)
mask2 = cv2.imread('m2.jpeg')
mask2 = cv2.cvtColor(mask2, cv2.COLOR_BGR2GRAY)
ret2, thresh_MASK_2 = cv2.threshold(mask2, 127, 255, cv2.THRESH_BINARY_INV)

# Create the background subtraction object
method = 1

if method == 0:
    bgSubtractor = cv2.bgsegm.createBackgroundSubtractorMOG()
elif method == 1:
    bgSubtractor = cv2.createBackgroundSubtractorMOG2()
else:
    bgSubtractor = cv2.bgsegm.createBackgroundSubtractorGMG()

# Create the kernel that will be used to remove the noise in the foreground mask
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
kernel_di = np.ones((5, 1), np.uint8)

# define variables
cnt = 0
cnt1 = 0
flag = True
flag1 = True
distance = 0.003

# Play until the user decides to stop
while True:
    start = timeit.default_timer()
    ret, frame = cap.read()
    frame_og = frame
    l, a, b = cv2.split(frame)
    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(1, 1))
    frame = clahe.apply(l)
    cv2.line(frame_og, (300, 513), (1900, 513), (0, 255, 0), 2)
    cv2.line(frame_og, (300, 482), (1900, 482), (0, 255, 0), 2)
    if ret == True:
        foregroundMask = bgSubtractor.apply(frame)
        foregroundMask = cv2.morphologyEx(foregroundMask, cv2.MORPH_OPEN, kernel)
        foregroundMask = cv2.erode(foregroundMask, kernel, iterations=3)
        foregroundMask = cv2.morphologyEx(foregroundMask, cv2.MORPH_CLOSE, kernel,iterations=6)
        foregroundMask = cv2.dilate(foregroundMask, kernel_di, iterations=7)
        foregroundMask = cv2.medianBlur(foregroundMask,5)
        thresh = cv2.threshold(foregroundMask, 25, 255, cv2.THRESH_BINARY)[1]
        thresh1 = np.bitwise_and(thresh, thresh_MASK_1)
        thresh2 = np.bitwise_and(thresh, thresh_MASK_2)
        contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        try:
            hierarchy = hierarchy[0]
        except:
            hierarchy = []
        for contour, hier in zip(contours, hierarchy):
            areas = [cv2.contourArea(c) for c in contours]
            max_index = np.argmax(areas)
            cnt = contours[max_index]
            (x, y, w, h) = cv2.boundingRect(cnt)
            cx = int((w / 2) + x)
            cy = int((h / 2) + y)
            if w > 10 and h > 10:
                cv2.rectangle(frame_og, (x - 10, y - 10), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame_og, (cx, cy), 5, (0, 0, 255), -1)

        if cy > 482 and w > 70 and h > 100:
            if flag is True and cy < 513:
                start_time = datetime.datetime.now()
                flag = False
            if cy > 513 and cy < 600:
                later = datetime.datetime.now()
                seconds = (later - start_time).total_seconds()
                if seconds <= 0.2:
                    print("diff 0")
                else:
                    print("seconds : " + str(seconds))
                    if flag is False:
                        speed = ((distance) / (36.6 *(seconds))) * 3600 * 90
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        cv2.putText(frame_og, str(int(speed)), (x, y), font, 2, (255, 255, 255), 8, cv2.LINE_AA)
                        cv2.putText(frame, str(int(speed)), (x, y), font, 2, (255, 255, 255), 8, cv2.LINE_AA)
                        # if not os.path.exists(path):
                        #     os.makedirs(path)
                        if int(speed) > speed_limit and w > 70 and h > 100:
                            roi = frame[y-50:y + h, x:x + w]
                            cv2.imshow("Lane_1", roi)
                            lane_1_1.append(roi)
                            # write_name = 'corners_found' + str(cnt1) + '.jpg'
                            # cv2.imwrite(write_name, roi)
                            # cv2.imwrite(os.path.join(path, 'carimage_l2_' + str(cnt1)) + '.jpg', roi)
                            cnt += 1
                    flag = True
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame, str(int(speed)), (x, y), font, 2, (255, 255, 255), 8, cv2.LINE_AA)

        contours1, hierarchy1= cv2.findContours(thresh2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        try:
            hierarchy1 = hierarchy1[0]
        except:
            hierarchy1 = []

        for contour1, hier1 in zip(contours1, hierarchy1):
            areas1 = [cv2.contourArea(c) for c in contours1]
            max_index1 = np.argmax(areas1)
            cnt1 = contours1[max_index1]
            (x1, y1, w1, h1) = cv2.boundingRect(cnt1)
            cx1 = int((w1 / 2) + x1)
            cy1 = int((h1 / 2) + y1)
            if w1 > 10 and h1 > 10:
                cv2.rectangle(frame_og, (x1 - 10, y1 - 10), (x1 + w1, y1 + h1), (255, 255, 0), 2)
                cv2.circle(frame_og, (cx1, cy1), 5, (0, 255, 0), -1)

        if cy1 > 482 and w1 > 70 and h1 > 100:
            if flag1 is True and cy1 < 513:
                start_time1 = datetime.datetime.now()
                flag1 = False
            if cy1 > 513 and cy1 < 600:
                later1 = datetime.datetime.now()
                seconds1 = (later1 - start_time1).total_seconds()
                if seconds1 <= 0.2:
                    print("diff1 0")
                else:
                    print("seconds1 : " + str(seconds1))
                    if flag1 is False:
                        speed1 = ((distance) / (36.6 *(seconds1))) * 3600 * 90
                        speed1 = speed1 - 10
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        cv2.putText(frame_og, str(int(speed1)), (x1, y1), font, 2, (255, 255, 255), 8, cv2.LINE_AA)
                        cv2.putText(frame, str(int(speed1)), (x1, y1), font, 2, (255, 255, 255), 8, cv2.LINE_AA)
                        # if not os.path.exists(path):
                        #     os.makedirs(path)
                        if int(speed1) > speed_limit and cy1 <= 720 and w1 > 70 and h1 > 100:
                            roi = frame[y1-50:y1 + h1, x1:x1 + w1]
                            cv2.imshow("Lane_2", roi)
                            lane_1_2.append(roi)
                            #cv2.imwrite(os.path.join('Offenders/', 'carimage_l2_' + str(cnt1)) + '.jpg', roi)
                            cnt1 += 1
                    flag1 = True
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame_og, str(int(speed1)), (x1, y1), font, 2, (255, 255, 255), 8, cv2.LINE_AA)
        #cv2.imshow('background subtraction', foregroundMask)
        #cv2.imshow('Sub',thresh)
        #cv2.imshow('Sub', thresh1)
        #cv2.imshow('Sub', frame)
        cv2.imshow('backgroundsubtraction', frame_og)
        stop = timeit.default_timer()
        time = stop-start
        print('One_frame = ',time)
        k = cv2.waitKey(1) & 0xff
        if k == ord('q'):
            break
    else:
        break
v = 0
u = 0
print('Saving.....')
for la in lane_1_1:
    cv2.imwrite('Offenders/lane1/'+'Lane'+str(v)+'.jpeg',la)
    v+=1
for li in lane_1_2:
    cv2.imwrite('Offenders/lane2/'+str(v)+'.jpeg',li)
    u+=1
cap.release()
cv2.destroyAllWindows()

