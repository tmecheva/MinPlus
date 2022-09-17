import sys
import os
import header
import subprocess
import xml.etree.ElementTree as ET
import pandas as pd
import xml.dom.minidom as dom
import math
import re
from sklearn.ensemble import IsolationForest

'''
<statistics xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/statistic_file.xsd">
    <vehicles loaded="4076" inserted="4076" running="244" waiting="0"/>
    <teleports total="0" jam="0" yield="0" wrongLane="0"/>
    <safety collisions="0" emergencyStops="3"/>
    <persons loaded="0" running="0" jammed="0"/>
    <vehicleTripStatistics routeLength="1961.58" speed="10.68" duration="201.48" waitingTime="61.69" timeLoss="105.39" departDelay="0.55" departDelayWaiting="-1.00" totalTravelTime="772060.00" totalDepartDelay="2100.20"/>
    <pedestrianStatistics number="0" routeLength="0.00" duration="0.00" timeLoss="0.00"/>
    <rideStatistics number="0"/>
    <transportStatistics number="0"/>
</statistics>
'''

class Statistics:
#Reads values from the stat.xml files in the path/directory and returns python dataframe        
    def CalculateCommonStatistics(self,net,tls):
        dfOut=pd.DataFrame(columns=["arRate","loaded","inserted","passed","routeLength","speed","duration","waitingTime","totalTravelTime","totalDepartDelay"])
        fullpath = os.path.join(header.result_path,net,tls,header.stat_folder)
        for filename in os.listdir(fullpath):
            doc = dom.parse(os.path.join(fullpath,filename))
            statistics = doc.getElementsByTagName("statistics")
            for st in statistics:
                vehicles = st.getElementsByTagName("vehicles")
                loaded = vehicles[0].getAttribute("loaded")
                inserted = vehicles[0].getAttribute("inserted")
                running = vehicles[0].getAttribute("running")
                teleports = st.getElementsByTagName("teleports")
                vehicleTripStatistics = st.getElementsByTagName("vehicleTripStatistics")
                routeLength = vehicleTripStatistics[0].getAttribute("routeLength")
                speed = vehicleTripStatistics[0].getAttribute("speed")
                duration = vehicleTripStatistics[0].getAttribute("duration")
                waitingTime = vehicleTripStatistics[0].getAttribute("waitingTime")
                totalTravelTime = vehicleTripStatistics[0].getAttribute("totalTravelTime")
                totalDepartDelay = vehicleTripStatistics[0].getAttribute("totalDepartDelay")
                            
            cfg=float(os.path.splitext(filename)[0])
            passed = int(inserted) - int(running)
            row={"arRate":float(cfg),"loaded":loaded,"inserted":inserted,"passed":passed,"routeLength":routeLength,"speed":speed,"duration":duration,"waitingTime":waitingTime,"totalTravelTime":totalTravelTime,"totalDepartDelay":totalDepartDelay}
            dfOut=dfOut.append(row,ignore_index = True)
            
        dfOut.sort_values(by=["arRate"],inplace=True,ascending=False)
        return dfOut
    
#Consequently reads trip durations from tripinfo file and return maxDelay for a file 
    def CalculateMaxDelay(self,tripinfoFile):
        doc = dom.parse(tripinfoFile)
        Delay = []
        tripinfo = doc.getElementsByTagName("tripinfo")        
        for ti in tripinfo:
            dur = ti.getAttribute("duration").split('.')[0]            
            Delay.append(int(dur))
            
        ddf = pd.DataFrame(data=Delay)
        iso = IsolationForest()
        yhat = iso.fit_predict(ddf)
        mask = yhat!=-1
        ddf=ddf[mask]
            
        maxDelay=ddf.max()
        filename = os.path.basename(tripinfoFile)
        cfg=float(os.path.splitext(filename)[0])
        row = {'arRate':cfg,'maxDelay':maxDelay}
        return row
    
#Returns dataframe of max delays in a tripinfo directory    
    def CalculateAllMaxDelay(self,net,tls):
        df = pd.DataFrame(columns=['arRate','maxDelay'])
        fullpath = os.path.join(header.result_path,net,tls,header.tripinfo_folder)
        for filename in os.listdir(fullpath):
            df = df.append(self.CalculateMaxDelay(os.path.join(fullpath,filename)),ignore_index=True)
        
        df.sort_values(by=['arRate'],inplace=True,ascending=False)
        df = df.astype({'maxDelay': int, "arRate": float})
        return df

#Concatenates commonStatistics and maxDelay and outputs dataframes   
    def CalculateAllCommonStatistics(self,net,tls):
        df2 = pd.DataFrame(columns = ['arRate','maxDelay'])
        with open(os.path.join(header.result_path,'CommonStatistics.csv'),'a') as f:
            df1=self.CalculateCommonStatistics(net,tls)
            df3=self.CalculateAllMaxDelay(net,tls)

            df2=pd.merge(df1,df3,left_on='arRate',right_on='arRate')
            df2.columns = df2.columns+net+tls
            df2.to_csv(f,sep=';')
    
#Returns dataframe of tls cycle times in a given file    
    def CalculateTLSCycleTimeFile(self,path):
        cfg=str(os.path.basename(path)).replace('.xml','')
        df = pd.DataFrame(columns=['tls',cfg])     
        doc = dom.parse(path)
        tlsList = doc.getElementsByTagName("tlLogic")        
        for tls in tlsList:
            TLSid = tls.getAttribute("id")
            phaseList = tls.getElementsByTagName("phase")
            duration = 0
            for phase in phaseList:
                duration += int(phase.getAttribute("duration"))
            df=df.append({'tls':TLSid,cfg:duration},ignore_index=True)
        return df    
    
#Returns dataframe of tls cycle times in a given directory    
    def CalculateTLSCycleTimeDir(self,directory):
        dflist = []
        for f in os.listdir(directory):
            dflist.append(self.CalculateTLSCycleTimeFile(os.path.join(directory,f)))
            
        result = dflist[0]
        for i in range(1,len(dflist)):
            result = pd.merge(result,dflist[i],on='tls')
            
        result.columns = result.columns.str.replace('tls',os.path.basename(directory))
        
        return result
    
#Concatenates commonStatistics and maxDelay and outputs dataframes   
    def CalculateAllTLSCycleTimes(self,path):
        flist = os.scandir(path)
        with open(os.path.join(path,'CycleTimes.csv'),'w') as f:
            for folder in flist:
                if folder.is_dir() and folder.name!='Coordinated':
                    df=self.CalculateTLSCycleTimeDir(os.path.join(path,folder.name))
                    df.sort_index(axis=1,inplace=True) 
                    df.to_csv(f,sep=';')
                    f.write("\n")

    
st = Statistics()
#st.CalculateAllDACurves(header.result_path)
for net in header.networks:
    for tls in header.tls_ADmethod:
        st.CalculateAllCommonStatistics(net,tls)
#st.CalculateAllTLSCycleTimes(os.path.join(header.out_path,'TLS'))
        

        
        
