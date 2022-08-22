# from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
from landmark import detect_landmarks, normalize_landmarks, plot_landmarks
from mediapipe.python.solutions.face_detection import FaceDetection
import numpy as np
from streamlit_webrtc import AudioProcessorBase,RTCConfiguration,VideoProcessorBase,WebRtcMode,webrtc_streamer
from aiortc.contrib.media import MediaPlayer
from PIL import ImageColor
import streamlit as st


upper_lip = [61, 185, 40, 39, 37, 0, 267, 269, 270, 408, 415, 272, 271, 268, 12, 38, 41, 42, 191, 78, 76]
lower_lip = [61, 146, 91, 181, 84, 17, 314, 405, 320, 307, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

# Left_shadow = [189,221,222,223,224,225,113,130,246,161,160,159,158,157,173]

# Right_shadow = [413,414,442,443,444,445,342,467,260,259,257,258,286,414,384,385,386,387,388,466,263,398,414,286,384,286,258,385,258,257,386,257,259,387,259,260,388,260,467,466,467,359,263]




color = []

option = st.selectbox(
     'How would you like to be contacted?',
     ('color_1', 'color_2', 'color_3', 'color_4', 'color_5'))

if option =='color_1':
    # color = [63, 64, 108] # 212, 44, 45
    color = [10, 5, 120] # 212, 44, 45
    m = '#945E9C'
elif option == 'color_2':
    color = [170, 5, 140]
    m = '#CB1D70'
elif option == 'color_3':
    color = [10, 20, 250]
    m = '#6B3D9A'
elif option == 'color_4':
    color = [107, 182, 203]
    m = '#9DB6CC' 
elif option == 'color_5':
    color = [105, 71, 59]
    m = '#a47551'
else :
    color = [45, 15, 5]


colors = st.color_picker('Pick A Color', m)


class VideoProcessor:
	def recv(self, frame):
         try:
            frm = frame.to_ndarray(format="rgb24")
            ret_landmarks = detect_landmarks(frm, True)
            height, width, _ = frm.shape
            feature_landmarks = None
            feature_landmarks = normalize_landmarks(ret_landmarks, height, width, upper_lip + lower_lip)
            print('color is ',color)
            
            mask= lip_mask(frm,feature_landmarks,color)
            
            output = cv2.addWeighted(frm, 1.0, mask, 0.4, 0.0)
            output = cv2.flip(output,1)
            print('here 1')
            return av.VideoFrame.from_ndarray(output, format='rgb24')
         except:
             VideoProcessor




def lip_mask(src: np.ndarray, points: np.ndarray, color: list):
    """
    Given a src image, points of lips and a desired color
    Returns a colored mask that can be added to the src
    """
    mask = np.zeros_like(src)  # Create a mask
    mask = cv2.fillPoly(mask, [points], color)  # Mask for the required facial feature
    # Blurring the region, so it looks natural
    # TODO: Get glossy finishes for lip colors, instead of blending in replace the region
    mask = cv2.GaussianBlur(mask, (7, 7), 5)
    return mask

def shadow_mask(src: np.ndarray, points: np.ndarray, color: list):
    """
        Given a src image, points of lips and a desired color
        Returns a colored mask that can be added to the src
        """
    print('here 2')   
    mask = np.zeros_like(src)  # Create a mask
    mask = cv2.fillPoly(mask, [points], color)  # Mask for the required facial feature
        # Blurring the region, so it looks natural
        # TODO: Get glossy finishes for lip colors, instead of blending in replace the region
    mask = cv2.GaussianBlur(mask, (7, 7), 5)
    return mask

# ctx =webrtc_streamer(
#     key="example",
#     video_processor_factory=VideoProcessor,
#     rtc_configuration={ # Add this line
#         "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
#     }
# )

# ctx =webrtc_streamer(
#     key="example",
#     video_processor_factory=VideoProcessor,
#     rtc_configuration=RTCConfiguration(
#     {
#       "RTCIceServer": [{
#         "urls": ["stun:stun.l.google.com:19302"],
# 	"username": "user",
# 	"credential": "password",
#       }]
#     }
# )
# )

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun4.l.google.com:19302"]}]}
)

webrtc_ctx = webrtc_streamer(
    key="object-detection",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True
)
