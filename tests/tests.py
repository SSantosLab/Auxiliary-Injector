from handlers.streamer import Alert

def runAll():
    runXRay()
    runGRay()
    runNeutrino()
    return 0
class testHandler()
    def __init__(self,mode) -> None:
        self.mode = mode
        self.runTest()

    def runTest(self): 
        # Parse initial GCN into a text block that the slackBot can understand
        self.parsed = self.parseGCN()
        # Make necessary plots
        self.plots = self.makePlots()
        # Make slack posts
        self.postToSlack()
        # Make emails
        self.sendEmails()

    def parseGCN(self):
        if self.mode=="":

        elif self.mode=="":

        elif self.mode=="":


    def makePlots(self):
        
    def postToSlack(self):
        
    def sendEmails(self):
    
