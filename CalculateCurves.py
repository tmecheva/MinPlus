import os
import pandas as pd
import xml.dom.minidom as dom
import header
import MinPlus as mp
import numpy as np
import math

class Curves:
    def __init__(self,out_path):
        self.result_path = os.path.join(header.current_directory,out_path,'Result')
        self.curves_path = os.path.join(header.current_directory,out_path,'Curves')
        self.stat_path = 'statistic'
        
        if not os.path.exists(self.curves_path):
            os.makedirs(self.curves_path)
            
        if not os.path.exists(os.path.join(self.curves_path,self.stat_path)):
            os.makedirs(os.path.join(self.curves_path,self.stat_path))
            
    #Calculate Departure curve from a tripinfo file       
    def CalculateArrivalCurveSimulational(self,tripinfoFile):
        doc = dom.parse(tripinfoFile)
        AC = [0]*360
        tripinfo = doc.getElementsByTagName("tripinfo")
            
        for ti in tripinfo:
            arr = ti.getAttribute("depart")
            di = float(arr)/10 #math.ceil(float(d)/10)-1
            AC[int(di)]+=1
            
        for i in range(1,360):
            AC[i]=AC[i]+AC[i-1]
            
        AC[0]=0
        return AC
    
    def CalculateServiceCurveRSPEC(self,speed,Ta):
        ServiceCurve=[0]*360
        for i in range(0,len(ServiceCurve)):
            t=i*10
            if t-Ta<=0:
                ServiceCurve[i] = 0
            else:
                ServiceCurve[i]=speed*(t-Ta)                
        return ServiceCurve
                
    def CalculateDepartureCurveRSPEC(self,arrival,service):      
        departure = mp.MinPlusConvolve(service,arrival)
        return departure          
        
#Calculate Arrival curve from a tripinfo file       
    def CalculateDepartureCurveSimulational(self,tripinfoFile):
        if os.path.isfile(tripinfoFile):
            doc = dom.parse(tripinfoFile)
            DC = [0]*360
            tripinfo = doc.getElementsByTagName("tripinfo")
            
            for ti in tripinfo:
                dep = ti.getAttribute("arrival")
                ai =  math.ceil(float(dep)/10) #math.ceil(float(a)/10)-1
                if ai < 360:
                    DC[ai]+=1
                
            for i in range(1,360):
                DC[i]=DC[i]+DC[i-1]
                                
            return DC
        
    def CheckCurves(self,small,big):
        if len(small)!=len(big):
            return False
        else:
            for i in range(0,len(big)):
                if big[i]<small[i]:
                    return False        
            return True

      
    def FindVDelay(self,ac,dc):
        delay = [0]*len(ac)
        j=0
        i=0
        while j<len(dc) and i<len(ac):
            if dc[j]>=ac[i]:                
                delay[i]=j-i
                if delay[i]<0:
                    delay[i]=0
                i+=1
            else:              
                j+=1
        return delay
    
#Callculate Departure and Arrival curves in a tripinfo directory and calculates service curve and returns single dataframe
    def CalculateDACurves(self,net,interval,to,path):
        arrival = self.CalculateArrivalCurveSimulational(path)
        departureSim = self.CalculateDepartureCurveSimulational(path)
        result=pd.DataFrame({'ACsim':arrival,'DCsim':departureSim})
        result.to_csv(os.path.join(self.curves_path,net+'_'+to+'_'+interval+'.csv'))
        
    def CalculateSCurves(self,path):
        df=pd.read_csv(path)
        arrival=df['ACsim']
        arrival[0] = 0
        departureSim = df['DCsim']
        for delay in header.maxDelay:
            for speed in header.speed:
                service = self.CalculateServiceCurveRSPEC(speed,delay)
                departureAn = self.CalculateDepartureCurveRSPEC(arrival.tolist(),service)
                if self.CheckCurves(departureAn,departureSim):
                    df['DCan'] = departureAn
                    df['SC'] = service
                    df.to_csv(path,index=False)
                    return
        print(path,"not found")

    def CalculateCurvesBacklog(self,f):
        df=pd.read_csv(f)
        df['backlog'] = df['ACsim']-df['DCsim']
        df.to_csv(f,index=False)
        
    def CalculateCurvesDelay(self,f):
        df=pd.read_csv(f)
        df['delay'] = self.FindVDelay(df['ACsim'],df['DCsim'])
        df.to_csv(f,index=False)
        
    def CalculateCurvesDistance(self,f):
        df=pd.read_csv(f)
        df['DCdist']=df['DCsim']-df['DCan']
        df['DCdist'].clip(lower=0, inplace = True)
        df.to_csv(f)
        
    def CalculateCurvesError(self,f):
        df=pd.read_csv(f)
        df['error'] = df['DCan']-df['DCsim']
        df['error'].clip(lower=0, inplace = True)
        df['error'] = df['error']/df['DCsim']
        df.to_csv(f)
        
class RealSimCurves(Curves):
    def __init__(self,out_path):
        Curves.__init__(self,out_path)
        self.w_h=['w','h']
        
    def CalculateDACurves(self,hour,w_h):
        arrival = self.CalculateArrivalCurveSimulational(os.path.join(self.result_path,w_h+hour,'trip.xml'))
        departureSim = self.CalculateDepartureCurveSimulational(os.path.join(self.result_path,w_h+hour,'trip.xml'))
        result=pd.DataFrame({'ACsim':arrival,'DCsim':departureSim})
        result.to_csv(os.path.join(self.curves_path,w_h+hour+'.csv'))
    
    def Curves(self):
        for hour in range(0,23):
            for wh in self.w_h:
                self.CalculateDACurves(str(hour),wh)
                self.CalculateCurvesDelay(os.path.join(self.curves_path,wh+str(hour)+'.csv'))
                self.CalculateCurvesBacklog(os.path.join(self.curves_path,wh+str(hour)+'.csv'))
                self.CalculateSCurves(os.path.join(self.curves_path,wh+str(hour)+'.csv'))
                
    def RealSimStatistic(self):
        acdfw=pd.DataFrame()
        dcdfw=pd.DataFrame()
        scdfw=pd.DataFrame()
        delaydfw=pd.DataFrame()
        backlogdfw=pd.DataFrame()
        
        acdfh=pd.DataFrame()
        dcdfh=pd.DataFrame()
        scdfh=pd.DataFrame()
        delaydfh=pd.DataFrame()
        backlogdfh=pd.DataFrame()
        
        for hour in range(0,23):
            df=pd.read_csv(os.path.join(self.curves_path,'h'+str(hour)+'.csv'))
            acdfh['h'+str(hour)]=df['ACsim']
            dcdfh['h'+str(hour)]=df['DCsim']                
            scdfh['h'+str(hour)]=df['SC']                
            delaydfh['h'+str(hour)]=[df['delay'].max()]
            backlogdfh['h'+str(hour)]=[df['backlog'].max()]
            
        for hour in range(0,23):
            df=pd.read_csv(os.path.join(self.curves_path,'w'+str(hour)+'.csv'))
            acdfw['h'+str(hour)]=df['ACsim']
            dcdfw['h'+str(hour)]=df['DCsim']                
            scdfw['h'+str(hour)]=df['SC']                
            delaydfw['h'+str(hour)]=[df['delay'].max()]
            backlogdfw['h'+str(hour)]=[df['backlog'].max()]
                
        acdfw.to_csv(os.path.join(self.curves_path,self.stat_path,'wac.csv'))
        dcdfw.to_csv(os.path.join(self.curves_path,self.stat_path,'wdc.csv'))
        scdfw.to_csv(os.path.join(self.curves_path,self.stat_path,'wsc.csv'))
        delaydfw.to_csv(os.path.join(self.curves_path,self.stat_path,'wdelay.csv'))
        backlogdfw.to_csv(os.path.join(self.curves_path,self.stat_path,'wbacklog.csv'))  
        
        acdfh.to_csv(os.path.join(self.curves_path,self.stat_path,'hac.csv'))
        dcdfh.to_csv(os.path.join(self.curves_path,self.stat_path,'hdc.csv'))
        scdfh.to_csv(os.path.join(self.curves_path,self.stat_path,'hsc.csv'))
        delaydfh.to_csv(os.path.join(self.curves_path,self.stat_path,'hdelay.csv'))
        backlogdfh.to_csv(os.path.join(self.curves_path,self.stat_path,'hbacklog.csv')) 
        
class MPCurves(Curves):
    def __init__(self,out_path):
        Curves.__init__(self,out_path)
        self.sc_integral_path = os.path.join(out_path,'Curves','SCconcat')
        self.sc_path = os.path.join(out_path,'Curves','SC')

        if not os.path.exists(self.sc_integral_path):
            os.makedirs(self.sc_integral_path)
            
        if not os.path.exists(self.sc_path):
            os.makedirs(self.sc_path)
            
    def Curves(self):
        for i in header.period:
            for net in header.networks: 
                self.CalculateDACurves(net,i,'',os.path.join(self.result_path,net,header.tripinfo_folder,i+'.xml'))
                self.CalculateCurvesDelay(os.path.join(self.curves_path,net+'__'+i+'.csv'))
                self.CalculateCurvesBacklog(os.path.join(self.curves_path,net+'__'+i+'.csv'))
                self.CalculateSCurves(os.path.join(self.curves_path,net+'__'+i+'.csv'))
                self.CalculateCurvesError(os.path.join(self.curves_path,net+'__'+i+'.csv'))
                self.CalculateCurvesDistance(os.path.join(self.curves_path,net+'__'+i+'.csv'))
                
    def FindSCurves(self):
        for net in header.networks:
            result = pd.DataFrame()
            for td in header.period:
                #print(net,td)
                df=pd.read_csv(os.path.join(self.curves_path,net+'__'+td+'.csv'))
                result[td] = df['SC']
            result.to_csv(os.path.join(self.sc_path,net+'.csv'))
        
    def FindSC(self,f):
        df = pd.read_csv(f,index_col=0)
        sc=df.iloc[:, 0]    
        for col in df.columns:
            sc = mp.MinFunction(sc,df[col])
        return sc
    
    def FindAllSCurves(self):
        df=pd.DataFrame()
        for net in header.networks:
            sc = self.FindSC(os.path.join(self.sc_path,net+'.csv'))
            df[net]=sc
        df.to_csv(os.path.join(self.curves_path,self.stat_path,"AllSC.csv"))
        
    def FindAllACurves(self):
        for net in header.networks:
            df=pd.DataFrame()
            for i in header.period:
                df[net+i] = pd.read_csv(os.path.join(self.curves_path,net+'__'+i+'.csv'))['ACsim']
            df.to_csv(os.path.join(self.curves_path,self.stat_path,net+"AC.csv"))
            
    def FindAllDCurves(self):
        for net in header.networks:
            df=pd.DataFrame()
            for i in header.period:
                df[net+i] = pd.read_csv(os.path.join(self.curves_path,net+'__'+i+'.csv'))['DCsim']
            df.to_csv(os.path.join(self.curves_path,self.stat_path,net+"DC.csv"))
            
    def IntegralSC(self,Nlist,Nintegral):
        for td in header.period:
            sc = self.FindSC(os.path.join(self.sc_path,Nlist[0]+'.csv'))
            df=pd.DataFrame(data={'sc'+Nlist[0]:sc})
            for i in range(1,len(Nlist)):
                sc2 = self.FindSC(os.path.join(self.sc_path,Nlist[i]+'.csv'))
                df['sc'+Nlist[i]]=sc2
                sc=mp.MinPlusConvolve(sc,sc2)
                
            integralCrvs = pd.read_csv(os.path.join(self.curves_path,Nintegral+'__'+td+'.csv'))

            ac=integralCrvs['ACsim']
            ac[0]=0
            dcan=mp.MinPlusConvolve(ac.tolist(),sc)
            df['DCsim']=integralCrvs['DCsim']           
            df['SC'+Nintegral]=sc
            df['AC']=ac
            df['DCan']=dcan
            df.to_csv(os.path.join(self.sc_integral_path,Nintegral+'__'+td+'.csv'))
            
    def CalculateDCDistance(self,junctions,path):
        out_path=os.path.join(path,self.stat_path)
        if not os.path.exists(out_path):
            os.makedirs(out_path)
            
        DCdistDF=pd.DataFrame(index=header.period,columns=junctions)
        for net in junctions:
            for td in header.period:
                df = pd.read_csv(os.path.join(path,net+'__'+td+'.csv'))
                DCdistDF[net][td]=round(df['DCdist'].mean(),2)
        print(DCdistDF)
        print(path)
        DCdistDF.T.to_csv(os.path.join(out_path,'distance.csv'),sep='&')
        
    def CalculateBacklog(self,junctions,path):
        out_path=os.path.join(path,self.stat_path)
        if not os.path.exists(out_path):
            os.makedirs(out_path)
            
        backlogDF=pd.DataFrame(index=header.period,columns=junctions)
        for net in junctions:
            for td in header.period:
                df = pd.read_csv(os.path.join(path,net+'__'+td+'.csv'))
                backlogDF[net][td]=round(df['backlog'].mean(),2)
        backlogDF.T.to_csv(os.path.join(out_path,'backlog.csv'))
        
    def CalculateVDelay(self,junctions,path):
        out_path=os.path.join(path,self.stat_path)
        if not os.path.exists(out_path):
            os.makedirs(out_path)
            
        delayDF=pd.DataFrame(index=header.period,columns=junctions)
        for net in junctions:
            for td in header.period:
                df = pd.read_csv(os.path.join(path,net+'__'+td+'.csv'))
                delayDF[net][td]=round(df['delay'].mean(),2)
        delayDF.T.to_csv(os.path.join(out_path,'delay.csv'),sep='&')
                
    def CalculateError(self,junctions,path):
        out_path=os.path.join(path,self.stat_path)
        if not os.path.exists(out_path):
            os.makedirs(out_path)
            
        errorDF=pd.DataFrame(index=header.period,columns=junctions)
        for net in junctions:
            for td in header.period:
                df = pd.read_csv(os.path.join(path,net+'__'+td+'.csv'))
                errorDF[net][td] = round(df['error'].mean(),2)
        print(path)
        print(errorDF)
        errorDF.T.to_csv(os.path.join(out_path,'error.csv'),sep='&')
        
    def IntegralStatistics(self,jlist):
        for j in jlist:
            for td in header.period:
                f=os.path.join(os.path.join(self.sc_integral_path,j+'__'+td+'.csv'))
                self.CalculateCurvesDistance(f)
                self.CalculateCurvesError(f)
        
        self.CalculateDCDistance(jlist,self.sc_integral_path)
        self.CalculateError(jlist,self.sc_integral_path)
        
    def MPStatistics(self):
        self.FindSCurves()
        self.FindAllSCurves()
        self.FindAllACurves()
        self.FindAllDCurves()
        self.CalculateVDelay(header.networks,self.curves_path)
        self.CalculateBacklog(header.networks,self.curves_path)
        self.CalculateDCDistance(header.networks,self.curves_path)
        self.CalculateError(header.networks,self.curves_path)
        
class TOCurves(Curves):
    def __init__(self,out_path,OptimizationParameter):
        Curves.__init__(self,out_path)
        self.ToParams = OptimizationParameter
        if not os.path.exists(os.path.join(out_path,"Curves")):
            os.makedirs(os.path.join(out_path,"Curves"))
        
    def CalcCurves(self):
        for i in header.period:
            for to in self.ToParams:
                for net in header.Lnetworks: 
                    self.CalculateDACurves(net,i,to,os.path.join(self.result_path,net,to,header.tripinfo_folder,i+'.xml'))
                    self.CalculateCurvesDelay(os.path.join(self.curves_path,net+'_'+to+'_'+i+'.csv'))
                    self.CalculateCurvesBacklog(os.path.join(self.curves_path,net+'_'+to+'_'+i+'.csv'))
     
    def CalculateBacklog(self):
        out_path=os.path.join(self.curves_path,self.stat_path)        
        if not os.path.exists(out_path):
            os.makedirs(out_path)
            
        resultAV=pd.DataFrame()
        #resultTD=pd.DataFrame()

        for net in header.Lnetworks:
            backlogDF=pd.DataFrame(index=header.period,columns=[x+"av" for x in self.ToParams])
            for td in header.period:
                for to in self.ToParams:
                    df = pd.read_csv(os.path.join(self.curves_path,net+'_'+to+'_'+td+'.csv'))
                    backlogDF[to+"av"][td]=df['backlog'].max()
            backlogDF[backlogDF<=0]=np.nan
            backlogDF.to_csv(os.path.join(out_path,net+'bl.csv'))
            
            #resultAV[net] = backlogDF.mean()
            #resultTD[net] = backlogDF.mean(axis=1)
        
        #resultAV[resultAV<0]=np.nan
        #resultAV.to_csv(os.path.join(out_path,'backlog.csv'))
        
    def CalculateVDelay(self):
        out_path=os.path.join(self.curves_path,self.stat_path)
        if not os.path.exists(out_path):
            os.makedirs(out_path)
            
        resultAV=pd.DataFrame()
        #resultTD=pd.DataFrame()
            
        for net in header.Lnetworks:
            delayDF=pd.DataFrame(index=header.period,columns=[x+"av" for x in self.ToParams])
            for td in header.period:
                for to in self.ToParams:
                    df = pd.read_csv(os.path.join(self.curves_path,net+'_'+to+'_'+td+'.csv'))
                    delayDF[to+"av"][td]=df['delay'].max()
            delayDF[delayDF<=0]=np.nan
            delayDF.to_csv(os.path.join(out_path,net+'vd.csv'))
                    
            #resultAV[net] = delayDF.mean()
            #resultTD[net] = delayDF.mean(axis=1)
        #resultAV.to_csv(os.path.join(out_path,'vdelay.csv'))
        
    def CalculateDCurves(self):
        out_path=os.path.join(self.curves_path,self.stat_path)
        if not os.path.exists(out_path):
            os.makedirs(out_path)
                        
        for net in header.Lnetworks:
            for td in header.period:
                resultDC=pd.DataFrame(columns=self.ToParams)
                for to in self.ToParams:
                    df = pd.read_csv(os.path.join(self.curves_path,net+'_'+to+'_'+td+'.csv'))
                    resultDC[to]=df['DCsim']

                resultDC.to_csv(os.path.join(out_path,net+td+'DC.csv'))
                                
    def MPStatistics(self):
        self.CalculateVDelay()
        self.CalculateBacklog()
        #self.CalculateDCurves()




        
        
