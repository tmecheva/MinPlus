import os
import pandas as pd
import xml.dom.minidom as dom
import math

import header
import MinPlus as mp

class Curves:
    def __init__(self):
        if not os.path.exists(header.curves_path):
            os.makedirs(header.curves_path)
                 
#Calculate Departure curve from a tripinfo file       
    def CalculateArrivalCurveSimulational(self,tripinfoFile):
        doc = dom.parse(tripinfoFile)
        AC = [0]*360
        tripinfo = doc.getElementsByTagName("tripinfo")
            
        for ti in tripinfo:
            d = ti.getAttribute("depart")
            di = math.ceil(float(d)/10)-1
            AC[di]+=1
            
        for i in range(1,360):
            AC[i]=AC[i]+AC[i-1]
            
        AC[0]=0
                
        return AC
    
#Calculate Arrival curve from a tripinfo file       
    def CalculateDepartureCurveSimulational(self,tripinfoFile):
        if os.path.isfile(tripinfoFile):
            doc = dom.parse(tripinfoFile)
            DC = [0]*360
            tripinfo = doc.getElementsByTagName("tripinfo")
            
            for ti in tripinfo:
                a = ti.getAttribute("arrival")
                ai = math.ceil(float(a)/10)-1
                DC[ai]+=1
                
            for i in range(1,360):
                DC[i]=DC[i]+DC[i-1]
                
            return DC
            
    def CalculateDepartureCurveAnalitical(self,arrival,delay,speed):      
        service = mp.CalculateServiceCurveAnalitical(speed,delay)
        departure = mp.MinPlusConvolve(service,arrival)
        return departure
    
    def CompareDepartureCurves(self,dep1,dep2):
        if len(dep1)!=len(dep2):
            print('ERROR')
        else:
            distance = [0]*len(dep2)
            for i in range(0,len(dep2)):
                distance[i] = dep1[i]-dep2[i]
                if distance[i]<0:
                    return []
            return distance
        
#Callculate Departure and Arrival curves in a tripinfo directory and rturns single dataframe
    def CalculateCurves(self,path,resfile,interval):
        arrival = self.CalculateArrivalCurveSimulational(os.path.join(path,interval+'.xml'))
        departureSim = self.CalculateDepartureCurveSimulational(os.path.join(path,interval+'.xml'))
        if arrival:
            print(resfile+interval)
            arrivalLn = mp.TSPEC(arrival)
            #arrivalLnSR = mp.TSPECSusRate(arrival)
            result=pd.DataFrame({'ACan':arrivalLn,'ACsim':arrival,'DCsim':departureSim})     
            for delay in header.maxDelay:
                for speed in header.speed:
                    departureAn = self.CalculateDepartureCurveAnalitical(arrival,delay,speed)
                    if mp.CheckCurves(departureAn,departureSim):
                        result['DCan'+'_'+str(delay)+'_'+str(speed)] = departureAn
                        result['SC'] = mp.CalculateServiceCurveAnalitical(speed,delay)
                        result.to_csv(os.path.join(header.curves_path,resfile+'_'+interval+'.csv'),sep=';')
                        return
'''
                    departureAn = self.CalculateDepartureCurveAnalitical(arrival,delay,speed)
                    distance = self.CompareDepartureCurves(departureSim,departureAn)
                    if distance:
                        result['DCan'+'_'+str(delay)+'_'+str(speed)] = departureAn
                        result['Dist'+'_'+str(delay)+'_'+str(speed)] = distance          
            result.to_csv(os.path.join(header.dc_path,resfile+'_'+interval+'.csv'),sep=';')
'''
            
crv = Curves()

for net in header.networks:
    for interval in header.period:
        for tls in header.tls_ADmethod:
            crv.CalculateCurves(os.path.join(header.result_path,net,tls,'Tripinfo'),net+tls,interval)



        
        
