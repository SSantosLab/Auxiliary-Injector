import os
import pickle
import json
from handlers.streamer import Alert
from handlers.streamer import handle

dataDir = "/data/des70.a/data/desgw/O4/Aux-Monitor/data/exampleJsons" 
def parse_json_from_bytes(data_array):
    """
    Takes a list of bytes (like from file.readlines()) and returns the parsed JSON dictionary.
    
    Args:
        data_array (list): List containing bytes, e.g., output of file.readlines()
        
    Returns:
        dict: Parsed JSON dictionary
    """
    if not data_array:
        raise ValueError("Input data array is empty.")
    
    # Assume the first line contains the JSON object
    byte_string = data_array[0]
    # json_string = b"".join(data_array).decode('utf-8').strip() # This is a fix, for multiple lines in the data_array
    # Decode, strip, and fix Pythonisms
    json_string = (byte_string.decode('utf-8').strip()
                   .replace("None", "null")
                   .replace("True", "true")
                   .replace("False", "false")
                  )
    
    # Parse JSON
    parsed_dict = json.loads(json_string)
    
    return parsed_dict
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
        with open(os.path.join(dataDir,"einstein-probe-example.json"),"rb") as f:
            self.gcn = json.load(f) 
            # self.gcn = parse_json_from_bytes(f.readlines())  

        handle(self.gcn,self.mode)
    def runGRay(self):
        with open(os.path.join(dataDir,"swift-bat-guano-example.json"),"rb") as f:
            self.gcn = json.load(f) 
            #self.gcn = parse_json_from_bytes(f.readlines()) 
        handle(self.gcn,self.mode)  
 
    def runNeutrino(self):
        with open(os.path.join(dataDir,"icecube-track-alert-example.json"),"rb") as f:
             self.gcn = parse_json_from_bytes(f.readlines())
             
        handle(self.gcn,self.mode) 
        # Adding a second call here to test over both the track alert and the LVK coordinated search 
        with open(os.path.join(dataDir,"icecube-lvk-track-search-example.json"),"rb") as f:
            #self.gcn = parse_json_from_bytes(f.readlines()) 
            self.gcn = json.load(f)
        handle(self.gcn,self.mode)

    def parseAlert(self): 
        Alert(self.mode,self.gcn)
