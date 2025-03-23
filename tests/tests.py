import os
import json
from handlers.streamer import Alert

dataDir = "../data/exampleJsons" 

class testHandler()
    def __init__(self,mode) -> None:
        self.mode = mode
        self.runTest()

    def runTest(self):
        if self.mode=="all":
           self.mode="x"
           self.runXRay()
           self.mode="g"
           self.runGRay()
           self.mode="v"
           self.runNeutrino()
        else:
            if self.mode=="x":
                self.runXRay()
            elif self.mode=="v":
                self.runNeutrino()
            elif self.mode=="g":
                self.runGRay()
            else:
                raise ValueError
                print("Mode supplied to testHanlder is invalid. Supplied mode: {}. Valid modes: {}".format(self.mode,["x","v","g"]))

    def runXRay(self):
        self.gcn = json.loads(os.path.join(dataDir,"einstein-probe-example.json"))
        self.parseAlert()
    def runGRay(self):
        self.gcn = json.loads(os.path.join(dataDir,"swift-bat-guano-example.json"))
        self.parseAlert()
    def runNeutrino(self):
        self.gcn = json.loads(os.path.join(dataDir,"icecube-track-alert-example.json"))
        self.parseAlert()
        # Adding a second call here to test over both the track alert and the LVK coordinated search 
        self.gcn = json.loads(os.path.join(dataDir,"icecube-lvk-track-search-example.json"))
        self.parseAlert()

    def parseAlert(self): 
        Alert(self.mode,self.gcn)
