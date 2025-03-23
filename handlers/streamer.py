# Gamma ray: Einstein probe  gcn.notices.einstein_probe.wxt.alert
# X ray: Swift gcn.notices.swift.bat.guano
# Radio (r): No great option, yet
# Neutrino: IceCube : gcn.notices.icecube.lvk_nu_track_search
import numpy as npi
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy import units as u
import ligo.skymap.plot
from matplotlib import pyplot as plt
import ligo.skymap
import pandas as pd
from astroplan import Observer, FixedTarget
from astroplan import (AltitudeConstraint, AirmassConstraint,AtNightConstraint)
from astroplan import is_observable
from astropy.time import Time
from astroplan.plots import plot_airmass
from astropy.visualization import astropy_mpl_style, quantity_support
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.coordinates import get_sun
from astropy.coordinates import get_body
import datetime
import ephem
import json
import os
from astropy.coordinates import ICRS
from .slack import SlackBot
from .emails import EmailBot

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
            self.inst = inst
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
            self.inst = inst
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
            self.inst = inst
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

    def prepMessage(self):
        finalString = "*Instrument*: {}\n".format(self.inst)+\
                      "*Quality*: {}\n".format(self.quality)+\
                      "*Alert type*: {}\n".format(self.alertType)+\
                      "*Trigger time*: {}\n".format(self.triggerTime)+\
                      "*Alert time*: {}\n".format(self.alertTime)
        if self.ra!=None and self.dec!=None:
            finalString+="*Maximum probablity pointing*: ({},{})\n".format(self.ra,self.dec)
        if self.pointError!=None:
            finalString+="*Pointing error*: {} deg\n".format(self.pointError)             
        if self.far!=None:
            finalString+="*FAR*: {}\n".format(self.far) 
        if self.nCoinc!=1:
            finalString+="*Number of coincident events*: {}\n".format(self.nCoinc)
        if self.comment!=None:
            finalString+="*Comment*: {}+\n".format(self.comment)
        if self.url!=None:
            finalString+="*URL*: {}".format(self.url)
        return finalString

class plotMaker():
    def __init__(self,alert):
        self.alert = alert
        self.plotPaths = plotHandler()

    def plotHandler(self):
        """
        Function to call specific plots based on the type of alert
        """

        allPlots = {}

        if self.alert.ra!=None and self.alert.dec!=None:
            ky,val = self.makeSkymap() # Make a skymap
            allPlots[ky] = val

        # Plot other things here, if needed

        return allPlots

    def makeSkymap(self):
        date = str(datetime.date.today())

        center = SkyCoord(self.alert.ra, self.alert.dec, unit="deg")  # defaults to ICRS frame

        event_id = self.alert.alertID 

        fig = plt.figure(figsize=(10, 10), dpi=100)
        plt.annotate('Event Name: {}'.format(event_id) + '\n'
                     + r'Max Prob Coordinates (degrees): ({},{})'.format(center.ra,center.dec) +'\n'
                     + r'Event type: {}'.format(self.alert.alertType) + '\n'
                     + r'Host instrument: {}'.format(self.alert.inst)
                     ,(0.9,0.8))
        plt.box(False)
        plt.xticks([])
        plt.yticks([])

        ax = plt.axes(projection='astro hours mollweide')

        ax_inset = plt.axes(
            [0.9, 0.2, 0.2, 0.2],
            projection='astro zoom',
            center=center,
            radius=10*u.deg)

        for key in ['ra', 'dec']:
            ax_inset.coords[key].set_ticklabel_visible(False)
            ax_inset.coords[key].set_ticks_visible(True)

        #ax.grid()
        #ax_inset.grid()
        ax.mark_inset_axes(ax_inset)
        ax.connect_inset_axes(ax_inset, 'upper right')
        ax.connect_inset_axes(ax_inset, 'lower left')
        ax_inset.scalebar((0.1, 0.1), 5 * u.deg).label()

        if self.alert.pointError!=None:
            # Contour the skymap here with a circle, radius here

        ### Add galactic plane and +- 15 deg to skymap plot

        seanLimit = 15 # The upper and lower limit on the galactic latitude range - typically, this is 15 degrees
        galacticLongitude = np.append(np.arange(0,360.1,step=0.1), 0)

        galacticCenterline = np.full(np.shape(galacticLongitude),0)
        galacticLowerLimit = np.full(np.shape(galacticLongitude),-seanLimit)
        galacticUpperLimit = np.full(np.shape(galacticLongitude),seanLimit)

        galacticCenterlineCoords = SkyCoord(l=galacticLongitude*u.degree,b=galacticCenterline*u.degree,frame='galactic')
        galacticLowerLimitCoords = SkyCoord(l=galacticLongitude*u.degree,b= galacticLowerLimit*u.degree,frame='galactic')
        galacticUpperLimitCoords = SkyCoord(l=galacticLongitude*u.degree,b= galacticUpperLimit*u.degree,frame='galactic')

        # Coordinate transform

        galacticCenterlineCoords = galacticCenterlineCoords.transform_to(ICRS)
        galacticLowerLimitCoords = galacticLowerLimitCoords.transform_to(ICRS)
        galacticUpperLimitCoords = galacticUpperLimitCoords.transform_to(ICRS)

        # plot it

        galaxyKwargs = {"Center": {'ls':'--','color':'black','label':"Galactic centerline"},
                        "Upper limit": {'ls':'--',"color":'black','alpha':0.5,'label':"Galactic latitude limit +/- {} deg".format(seanLimit)},
                        "Lower limit": {'ls':'--',"color":'black','alpha':0.5}}

        for coord,label,galkey in zip([galacticCenterlineCoords,galacticLowerLimitCoords,galacticUpperLimitCoords],["Galactic center","Galactic lower limit","Galactic upper limit"],galaxyKwargs.keys()):
            galRa = coord.ra.wrap_at(180 * u.deg).radian
            galDec = coord.dec.radian
            ax.plot(galRa,galDec,**galaxyKwargs[galkey])


        ax_inset.plot(
            self.alert.ra, self.alert.dec,
            transform=ax_inset.get_transform('world'),
            marker=ligo.skymap.plot.reticle(),
            markersize=30,
            markeredgewidth=3)
        ax.plot(
            self.alert.ra,self.alert.dec,
            transform=ax.get_transform('world'),
            marker=ligo.skymap.plot.reticle(inner=0),
            markersize=10,
            markeredgewidth=3, label = "Max Prob Coord")
        ax.legend(loc = (0.1,1))

        skymap_plot = baseDir+'/initial_skymap.png'
        plt.savefig(skymap_plot,dpi=300, bbox_inches = "tight")
        os.chmod(skymap_plot, 0o0777)

        # Clear the current axes.
        plt.cla()
        # Clear the current figure.
        plt.clf()
        # Closes all the figure windows.
        plt.close('all')

        return skymap_plot,"Skymap"


def handle(gcn_alert,mode):
    """
    gcn_alert is a dict object of the .json message 
    """
    
    try gcn_alert["instrument"]:
        instrument = gcn_alert["instrument"]
    else:
        instrument = "Ice-Cube"
    mode = modeInstDict[instrument]

    alert = Alert(mode,gcn_alert) # Parse the gcn_alert into the Alert object
    
    email_bot = EmailBot(mode=mode)
    slack_bot = SlackBot(mode=mode)

    slack_bot.post_message("","Received GCN for {} trigger, parsing".format(alert.inst))

    # Make plots
    plots = plotMaker(alert)
    plotPaths = plots.plotPaths

    # Post final messages to slack
    slack_bot.post_message("",alert.prepMessage())
    for key, val in zip(plotPaths.keys(),plotPaths.values()):
        slack_bot.post_image(key,val)

    # send emails, if necessary
    # Skipping for now, might come back to this
    
