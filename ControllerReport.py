import pandas as pd
import numpy as np
import os
import header
from datetime import datetime, date

class ControllerReport:
    def __init__(self,out,path):
        self.hdf=[pd.DataFrame(columns=['Detector'])]*24
        self.wdf=[pd.DataFrame(columns=['Detector'])]*24
        self.crpath=os.path.join(out,'CR')

        self.detectors=[]
        self.num=[]
        self.timestamp=[]
        self.df = pd.DataFrame()
        df = pd.read_excel(path,header=[1])
        self.row=0
        self.df = df.drop(df.columns[[1,2,5]],axis=1)
        self.Time = datetime.strptime(self.df.iloc[0,0],"%d.%m.%Y %H:%M:%S")
    
    def WriteValues(self):
        values = pd.DataFrame(data={'Detector':self.detectors,'qPKW':self.num})
        values.set_index('Detector',inplace=True)        
        if self.Time.weekday() in [6,7] or self.Time.date == date(year=2021,day=30,month=4):# or self.Time.date == datetime.date(year=2021,month=5,day=3):
            self.hdf[self.Time.hour] = pd.merge(self.hdf[self.Time.hour],values,how="outer",left_index=True,right_index=True,suffixes=("",self.Time))
        else:
            self.wdf[self.Time.hour] = pd.merge(self.wdf[self.Time.hour],values,how="outer",left_index=True,right_index=True,suffixes=("",self.Time))
            
    def GetValues(self):
        while self.row < self.df.shape[0]:
            currTime=datetime.strptime(self.df.iloc[self.row,0],"%d.%m.%Y %H:%M:%S")
            if self.Time != currTime:
                self.WriteValues()
                self.CleanValues()
            else:
                self.GetValue()                
                self.row +=1
        
    def CleanValues(self):
        self.Time = datetime.strptime(self.df.iloc[self.row,0],"%d.%m.%Y %H:%M:%S")
        self.detectors=[]
        self.num=[]
        self.timestamp=[]
        
    def WriteValuesToCSV(self,i):
        if not os.path.exists(os.path.join(self.crpath)):
            os.makedirs(os.path.join(self.crpath))

        dfH=pd.DataFrame(index=self.hdf[i].index)
        dfW=pd.DataFrame(index=self.wdf[i].index)

        dfH['Time'] = 0
        dfW['Time'] = 0
        dfH['qPKW'] = self.hdf[i].mean(axis = 1).round(0) 
        dfW['qPKW'] = self.wdf[i].mean(axis = 1).round(0)
        dfH['vPKW'] = 13.9
        dfW['vPKW'] = 13.9
        
        dfH = dfH.dropna()
        dfW = dfW.dropna()
        dfH.to_csv(os.path.join(self.crpath,'h'+str(i)+'.csv'),sep=';')
        dfW.to_csv(os.path.join(self.crpath,'w'+str(i)+'.csv'),sep=';')

    def GetValue(self):        
        det = self.df.iloc[self.row,1]
        val = self.df.iloc[self.row,2]
        t = self.df.iloc[self.row,0]
        if type(det) == int and int(det)%2 == 1:
            self.detectors.append("306:"+str(det))
            self.num.append(val)

def CreateConfigFiles(out_path):
    cr = ControllerReport(out_path,os.path.join(header.conf_path,'306'+'.xlsx'))
    cr.GetValues()
        
    for i in range(0,24):
        cr.WriteValuesToCSV(i)
    
                    
                      
    
