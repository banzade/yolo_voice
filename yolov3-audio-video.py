import cv2
import numpy as np
import time
import os
import imutils
import subprocess
from gtts import gTTS
from pydub import AudioSegment
AudioSegment.converter = "C:/Users/vivek/Desktop/yolov3/ffmpeg-2.1.1-win64-static/bin/ffmpeg.exe"

#loading yolo weights and cfg
#net = cv2.dnn.readNet("yolov3-tiny.weights","yolov3-tiny.cfg")
net = cv2.dnn.readNet("yolov3.weights","yolov3.cfg")
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

layer_names = net.getLayerNames()
outputlayers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0,255,size=(len(classes),3))

#loading image
cap=cv2.VideoCapture(0)
#cap=cv2.VideoCapture("video_file.mp4")
font = cv2.FONT_HERSHEY_PLAIN
starting_time= time.time()
frame_id = 0

while True:
    _,frame= cap.read()
    frame = cv2.flip(frame,1)
    frame_id+=1
    
    (height,width) = frame.shape[:2]
    #detecting objects
    blob = cv2.dnn.blobFromImage(frame,0.00392,(320,320),(0,0,0),True,crop=False) #reduce 416 to 320    

        
    net.setInput(blob)
    outs = net.forward(outputlayers)
    #print(outs[1])


    #Showing info on screen/ get confidence score of algorithm in detecting an object in blob
    class_ids=[]
    confidences=[]
    boxes=[]
    centers = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                #object detected
                box = detection[0:4] * np.array([width,height,width,height])
                (center_x,center_y,w, h) = box.astype("int")
                # center_x= int(detection[0]*width)
                # center_y= int(detection[1]*height)
                # w = int(detection[2]*width)
                # h = int(detection[3]*height)

                #cv2.circle(img,(center_x,center_y),10,(0,255,0),2)
                #rectangle co-ordinaters
                x=int(center_x - w/2)
                y=int(center_y - h/2)
                #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

                boxes.append([x,y,int(w),int(h)]) #put all rectangle areas
                confidences.append(float(confidence)) #how confidence was that object detected and show that percentage
                class_ids.append(class_id) #name of the object tha was detected
                centers.append((center_x, center_y))

    indexes = cv2.dnn.NMSBoxes(boxes,confidences,0.5,0.3)
    texts = []

    if len(indexes) > 0:
        for i in indexes.flatten():
            center_x, center_y = centers[i][0], centers[i][1]

            if center_x <= width/3:
                w_pos = "left "
            elif center_x <= (width/3 *2):
                w_pos = "center "
            else:
                w_pos = "right"
            if center_y <= height/3:
                h_pos = "top "
            elif center_y <= (height/3 * 2):
                h_pos = "mid "
            else:
                h_pos = "bottom "
            texts.append(h_pos + w_pos + classes[class_ids[i]])
    print(texts)

    for i in range(len(boxes)):
        if i in indexes:
            x,y,w,h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence= confidences[i]
            color = colors[class_ids[i]]
            cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
            cv2.putText(frame,label+" "+str(round(confidence,2)*100)+"%",(x,y+30),font,1,(255,255,255),2) 

    elapsed_time = time.time() - starting_time
    fps=frame_id/elapsed_time
    cv2.putText(frame,"FPS:"+str(round(fps,2)),(10,50),font,2,(0,0,0),1)    
    
    cv2.imshow("Image",frame)
    key = cv2.waitKey(1) #wait 1ms the loop will start again and we will process the next frame
    
    if key == 27: #esc key stops the process
        break;
    
    if texts:
        description = ', '.join(texts)
        tts = gTTS(description, lang='en')
        tts.save('tts.mp3')
        tts = AudioSegment.from_mp3("tts.mp3")
        subprocess.call(["ffplay","-nodisp", "-autoexit","tts.mp3"])
    



cap.release()    
cv2.destroyAllWindows()
os.remove("tts.mp3")
