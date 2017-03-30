# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 15:22:52 2017

@author: user15
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 14:31:19 2017

@author: David Smyth
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Oct  8 13:03:32 2016

@author: David Smyth
"""
#==============================================================================
# Add:
# Shenzhen
#==============================================================================

import folium
import numpy as np
import PIL
import urllib.request
from math import atan,degrees
import sys
import os
import re

class Location:
    def __init__(self,description,lat,long):
        self.description=description
        self.lat=lat
        self.long=long
        
    def getLocation(self):
        return [self.description,self.lat,self.long]
        
class Route:
    def __init__(self,description, location1, location2, travelMethod):
        self.description=description
        self.location1=location1
        self.location2=location2
        self.travelMethod=travelMethod
        
    def getRoute(self):
        return [self.description,self.location1.getLocation, self.location2.getLocation,self.travelMethod]
        
        
        
class Map:
    #planeUrl='http://www.airbus.com/typo3temp/_processed_/csm_A380-800_T_a201b2bdd4.png'
    #busUrl='http://www.clipart-box.com/zoom/doubledecker-bus120702.jpg'
    #boatUrl='https://static1.squarespace.com/static/5006453fe4b09ef2252ba068/t/5093a476e4b05d6afda2c8df/1351853179030/r_m_s__titanic_side_plan.png'
    transportUrls={'plane':'http://www.airbus.com/typo3temp/_processed_/csm_A380-800_T_a201b2bdd4.png' , 'bus': 'http://www.clipart-box.com/zoom/doubledecker-bus120702.jpg','boat':'https://static1.squarespace.com/static/5006453fe4b09ef2252ba068/t/5093a476e4b05d6afda2c8df/1351853179030/r_m_s__titanic_side_plan.png'}
    '''Could load map from file or unpickle object, load file for now'''
    def __init__(self, locations=None):
        '''locations should be a file containing the following (automatically written
        by this program):
        route/location,(popup text)____,(latfrom)_____,(longfrom)____,(latto)_____,(longto)____,(Transport method)_______'''
        
        self.map=folium.Map(location=[0,0], tiles='Stamen Terrain',zoom_start=2)
        self.imageNumber=0
        self.locations=[]
        self.routes=[]
        if locations==None:
            #initialise file
            print('Locations not provided')
            sys.exit(0)
                
        else:
            #recreate map
            try:
                print("Opening locations file at %s" % locations)
                self.locationsFile=open(locations,'r+')
                os.chdir(re.findall("(.*)/.*\.csv",string=locations)[0])
                for line in self.locationsFile:
                    journeyDetails=line.split(',')
                    if journeyDetails[0]=='location':
                        #If just a location provided, write the location and popup to the current map
                        print("Added location to map! Popup: %s, Coordinates: %s" % (str(journeyDetails[1]),str(journeyDetails[2:4])))
                        self.addLocationDetails(journeyDetails[1],journeyDetails[2:4],write=False)
                    #add a route to the map
                    elif journeyDetails[0]=='route':
                        #check if transport method provided, if so then write the details to map
                        if journeyDetails[-1].lower()=='plane' or journeyDetails[-1].lower()=='bus' or journeyDetails[-1].lower()=='boat':
                            print("Added route to map! Popup: %s, Type: %s, From %s, To %s" % (str(journeyDetails[1]),str(journeyDetails[-1]),str(journeyDetails[2:4]),str(journeyDetails[4:6])))
                            self.addRoute(journeyDetails[2:4],journeyDetails[4:6],journeyDetails[1],journeyDetails[-1],write=False)
                        #otherwise if only 5 arguments provided, then write the details
                        elif len(journeyDetails)==6:
                            self.addBusRoute(journeyDetails[2:4],journeyDetails[4:6],journeyDetails[1],None,write=False)
                        else:
                            print('Error reading journey details from file, traceback: %s' % ' '.join(journeyDetails))
                    else:
                        print('Error reading locations file, %s is neither route nor location' % journeyDetails[0])
                        sys.exit(0)
                
            except FileNotFoundError:
                print('Could not find the file')
                sys.exit(0)
                
    def formatWriteDetails(self,*args):
        '''Formats write details as comma separated values'''
        return ','.join(list(map(lambda x: str(x),args)))+'\n'
                
    def addLocation(self,location, popUpText, write=True):
        '''adds a popup to lat/long coordinates'''
        #first write to the current map
        folium.Marker(location,popup=popUpText).add_to(self.map)
        #write to locations file if asked to do so
        if write:
            self.locationsFile.write(self.formatWriteDetails('location,',popUpText,str(location[0]),str(location[1])))
        else:
            pass
        
    
        
    def addRoute(self,destFrom,destTo,popUpText,travelMethod=None, write=True):
        #if a travelMethod is provided, then add icon
        destFrom,destTo=list(map(lambda x: float(x),destFrom)),list(map(lambda x: float(x),destTo))
        if travelMethod:
            #need to store a separate image for each route as some images are rotated
            self.imageNumber+=1
            imageFile=travelMethod+str(self.imageNumber)+'.png'
            urllib.request.urlretrieve(self.transportUrls[travelMethod],imageFile)
            #open image using PIL for manipulation
            image=PIL.Image.open(imageFile)
            #Use numpy arrays for vectorization
            fromArray=np.array(destFrom)
            toArray=np.array(destTo)
            #rotate image
            if destFrom[0]>destTo[0]:
                image=image.rotate(90+degrees(atan((toArray-fromArray)[0]/(toArray-fromArray)[1])))
            else:
                image=image.rotate(-90+degrees(atan((toArray-fromArray)[0]/(toArray-fromArray)[1])))
            image.save(imageFile)
            #Place a marker halfway along route with icon specified by the user
            folium.Marker((toArray+fromArray)/2,popup=popUpText, icon=folium.features.CustomIcon(imageFile,icon_size=(50, 50))).add_to(self.map)
        #Trace the route with a semi-transparent line
        folium.PolyLine([destFrom,destTo], color="red", weight=1, opacity=3).add_to(self.map)
        #write the details to locations file for reconstruction 
        if write:
            self.locationsFile.write(self.formatWriteDetails('route',popUpText,destFrom[0],destFrom[1],destTo[0],destTo[1],travelMethod))
        else:
            pass
        
    def closeAll(self):
        self.locationsFile.close()
            
    def saveFile(self,file):
        self.map.save(file)
        

#%%        

Shibuya=[35.6562382,139.6916636]
HongKong=[22.3373636,114.2668898]
Brooklyn=[40.6810763,-73.9106939]
Boston=[42.4368876,-71.073395]
Malaga=[36.6218504,-4.5031117]


m1=Map('Your/chosen/location.csv')
m1.addRoute(HongKong, Malaga, 'Hong Kong to Ao Nang Depart: xxx Return:yyy','plane')
m1.addRoute(HongKong, Shibuya, 'Hong Kong to Narita Depart: xxx Return:  yyy','plane')
m1.addRoute(Malaga, HongKong, 'ABC to Hong Kong Depart: xxx Return:  yyy','plane')
m1.addLocation(Shibuya,'Visited here for 6 weeks, great trip!')
m1.saveFile('Your/chosen/location.html')
m1.closeAll()




