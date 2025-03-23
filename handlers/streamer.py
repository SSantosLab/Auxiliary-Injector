# Gamma ray: Einstein probe  gcn.notices.einstein_probe.wxt.alert
# X ray: Swift gcn.notices.swift.bat.guano
# Radio (r): No great option, yet
# Neutrino: IceCube : gcn.notices.icecube.lvk_nu_track_search
import numpy as np

subscriptionDict = {
                    "g":"gcn.notices.einstein_probe.wxt.alert",
                    "x":"gcn.notices.swift.bat.guano",
                    "v":"gcn.notices.icecube.lvk_nu_track_search"
                    }

modeInstDict = {"Ice-Cube":"v",
                "BAT-GUANO":"g",
                "WXT":"x"}

class Alert():
    """


    Params:
    ============
    quality 
    ra
    dec 
    alertTime 
    triggerTime 
    far 
    energy 
    alertType 
    alertID 
    shortName 
    pointError 
    nCoinc
    comment
    url
    """



    def __init__(self,mode,gcn_alert):
        self.mode = mode
        self.gcn_alert = gcn_alert
        
        if self.mode=="v":
            self.parseNeutrino()
        elif self.mode=="g":
            self.parseGammaRay()
        elif self.mode=="x":
            self.parseXRay()
        else:
            raise ValueError
                print("Mode supplied to Alert object does not match an allowed mode. Supplied mode: {}. Allowed modes: {}".format(self.mode,["x","v","g"]))

    def parseNeutrino(self,inst="Ice-Cube"):
        """
        
        """

        if inst=="Ice-Cube":
            try self.gcn_alert["additional_info"]:
            # Neutrino only track event
                self.quality = list(self.gcn_alert["additional_info"])[1] # Bronze or Gold
                self.ra = self.gcn_alert["ra"]
                self.dec = self.gcn_alert["dec"]
                self.alertTime = self.gcn_alert["alert_datetime"]
                self.triggerTime = self.gcn_alert["trigger_time"]
                self.far = self.gcn_alert["far"]
                self.energy = self.gcn_alert["nu_energy"]
                self.alertType = self.gcn_alert["alert_type"]
                self.alertID = self.gcn_alert["id"]
                self.shortName = self.gcn_alert["additional_info"]
                self.pointError = self.gcn_alert["ra_dec_error"]
                self.nCoinc = 1
            else:
            # LVK coordinated search
                self.quality = "Platinum"
                self.ra = self.gcn_alert["most_probable_direction"]["ra"]
                self.dec = self.gcn_alert["most_probable_direction"]["dec"]
                self.alertTime = self.gcn_alert["alert_datetime"]
                self.triggerTime = self.gcn_alert["trigger_time"]
                self.alertType = "Coincident Search"  
                self.alertID = self.gcn_alert["ref_ID"] 
                self.shortName = self.gcn_alert["type"]
                baseline = 0
                for event in self.gcn_alert["coincident_events"]:
                    baseline+=event["ra_dec_error"]**2
                self.pointError = np.sqrt(baseline)
                self.nCoinc = self.gcn_alert["coincident_events"]
                self.far = None # Probably best to pull this from the GW GCN?
                self.energy = None
            self.url = None
            self.comment=None 
        else:
            raise ValueError
            print("inst supplied to parseNeutrino is not valid. Provided inst: {}. Valid inst: {}.".format(inst,["Ice-Cube"]))
 
    def parseXRay(self,inst="WXT"):
        """
        
        """

        if inst=="WXT":
            self.quality = "Bronze"
            self.ra = self.gcn_alert["ra"]
            self.dec = self.gcn_alert["dec"]
            self.alertTime = None
            self.triggerTime = self.gcn_alert["trigger_time"]
            self.far = None
            self.energy = "{} count in the range of {}".format(self.gcn_alert["net_count_rate"],self.gcn_alert["image_energy_range"])
            self.alertType = "WXT event"
            self.alertID = self.gcn_alert["id"] 
            self.shortName = "X-ray event from Einstein Probe"
            self.pointError = self.gcn_alert["ra_dec_error"]
            self.nCoinc = None
            self.comment = self.gcn_alert["additional_info"]
            self.url = None
        else:
            raise ValueError
            print("inst supplied to parseXRay is not valid. Provided inst: {}. Valid inst: {}".format(inst,["WXT"]))

    def parseGammaRay(self,inst="BAT-GUANO"):
        """
        
        """
        if inst=="BAT-GUANO":
            self.quality = "Bronze"
            self.ra = None
            self.dec = None
            self.alertTime = self.gcn_alert["alert_datetime"]
            self.triggerTime = self.gcn_alert["trigger_time"]
            self.far = self.gcn_alert["far"]
            self.energy = None
            self.alertType = self.gcn_alert["alert_type"]
            self.alertID = self.gcn_alert["id"]
            self.shortName = self.gcn_alert["follow_up_event"]
            self.pointError = None
            self.nCoinc = 1
            self.comment = "{} classification of event {}".format(self.gcn_alert["follow_up_type"],self.gcn_alert["follow_up_event"])
            self.url = self.gcn_alert["data_archive_page"]
        else:
            raise ValueError
            print("inst supplied to parseGammaRay is not valid. Provided inst: {}. Valid inst: {}.".format(inst,["BAT-GUANO"]))

def handle(gcn_alert):
    """
    gcn_alert is a dict object of the .json message 
    """
    
    try gcn_alert["instrument"]:
        instrument = gcn_alert["instrument"]
    else:
        instrument = "Ice-Cube"
    mode = modeInstDict[instrument]

    alert = Alert(mode,gcn_alert) # Parse the gcn_alert into the Alert object
    
    # Make plots
    # Post messages to slack
    # send emails
