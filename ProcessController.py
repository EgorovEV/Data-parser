import os

import face_alignment
import pandas as pd
import torch
from facenet_pytorch.models.inception_resnet_v1 import InceptionResnetV1

from VideoChecker import VideoChecker
from VideoLoader import VideoLoader
from VideoTrimmer import VideoTrimmer
from utils import load_checkpoints


# class to wrap workflow
# noinspection PyBroadException
class ProcessController(object):

    def __init__(self, loadList="LoadList.csv", trimInterval=20):
        self.loadListPath = loadList
        self.loadList = pd.read_csv(loadList)
        self.interval = trimInterval
        pd.options.mode.chained_assignment = None

    def loadAll(self, rawVideoDir="./dataset/video/raw/"):
        for i in range(len(self.loadList)):
            try:
                url = self.loadList["URL"][i]
                videoLoader = VideoLoader(url, rawVideoDir=rawVideoDir)
                videoLoader.load()
                self.loadList["STATUS"][i] = "LOADED"
            except Exception as e:
                self.loadList["STATUS"][i] = "ERROR"
                print('Failed to upload to ftp: ' + str(e))
                continue

    def trimAll(self, rawVideoDir="./dataset/video/raw/"):
        dir_path = rawVideoDir
        dir = os.listdir(dir_path)
        for elem in dir:
            if elem.count(".mp4") == 1:
                videoTrimmer = VideoTrimmer(dir_path + elem, interval=self.interval)
                videoTrimmer.trim()

    @staticmethod
    def checkAll(rawVideoDir="./dataset/video/raw/"):
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        #model = InceptionResnetV1(pretrained='vggface2').eval()
        device_str = 'cpu' if device == torch.device('cpu') else 'cuda:0'
#         kp_detector = load_checkpoints(config_path='/content/Data-parser/vox-256.yaml',
#                             checkpoint_path='/content/gdrive/My Drive/first-order-motion-model/vox-cpk.pth.tar')
        fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._3D, device='cuda:0')
        raw_dir_path = rawVideoDir
        raw_dir = os.listdir(raw_dir_path)
        for elem in raw_dir:
            path = raw_dir_path + elem
            if path.count(".mp4") == 0:
                check_dir = path
                videoChecker = VideoChecker(check_dir)
                videoChecker.check(fa, device, None, KP_d=None)

    def process(self):

        rawVideoDir = "/content/gdrive/My Drive/dataset/video/raw/"
        self.loadAll(rawVideoDir)
        print("Loaded, trimming!")
        self.trimAll(rawVideoDir)
        print("Trimmed, checking!")
        self.checkAll(rawVideoDir)
