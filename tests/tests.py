import os
import json
from handlers.streamer import Alert
from handlers.streamer import handle

dataDir = "/data/des70.a/data/desgw/O4/Aux-Monitor/data/exampleJsons" 

class testHandler():
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
        with open(os.path.join(dataDir,"einstein-probe-example.json")) as f:
            self.gcn = json.load(f)

        handle(self.gcn,self.mode)
    def runGRay(self):
        with open(os.path.join(dataDir,"swift-bat-guano-example.json")) as f:
            self.gcn = json.load(f)
        handle(self.gcn,self.mode)  
 
    def runNeutrino(self):
        with open(os.path.join(dataDir,"icecube-track-alert-example.json")) as f:
            self.gcn = json.load(f)
        handle(self.gcn,self.mode) 
        # Adding a second call here to test over both the track alert and the LVK coordinated search 
        with open(os.path.join(dataDir,"icecube-lvk-track-search-example.json")) as f:
            self.gcn = json.load(f)
        handle(self.gcn,self.mode)

    def parseAlert(self): 
        Alert(self.mode,self.gcn)
