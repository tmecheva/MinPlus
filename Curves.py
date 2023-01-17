#Concatenates all Departure and Arrival curves and output the dataframe to a csv file
import pandas as pd
import xml.dom.minidom as dom
import os
import numpy as np
import header
import MinPlus as mp
import statistics

def CalcError(small,big):
    if len(small)!=len(big):
        return False
    else:
        err=[0]*len(big)
        for i in range(0,len(big)):
            if big[i]<small[i]:
                err[i] = ((small[i]-big[i])/big[i])
        return sum(err)/len(err)
    

def CalcDistance(small,big):
    if len(small)!=len(big):
        return False
    else:
        dist=[0]*len(big)
        for i in range(0,len(big)):
            if big[i]>small[i]:
                dist[i] = big[i]-small[i]
        return sum(dist)*100/sum(small)
    
def FindSmallerCurve(c1,c2):
    if len(c1)!=len(c2):
        return []
    if c2[len(c1)-1]<c1[len(c1)-1]:
        return c2
    else:
        return c1
    
def FindSmallerSCurve(df):
    sc  = [1000]*df.shape[0]
    for col in df.columns:
        for i in range(0,df.shape[0]):
            if df[col][i]<sc[i]:
                sc = df[col]
                break;
    return sc
    
def FindArrivalCurveSim(f):
    df = pd.read_csv(f)
    result=df['ACsim'].tolist()
    return result

def FindArrivalCurveAn(f):
    df = pd.read_csv(f)
    result=df['ACan'].tolist()
    return result

def FindServiceCurve(f):
    df = pd.read_csv(f)
    result=df['SC'].tolist()
    return result

def FindDepartureCurveSim(f):
    df = pd.read_csv(f)
    result=df['DCsim'].tolist()
    return result

def FindDepartureCurveAn(f):
    df = pd.read_csv(f,sep=';')
    result=df['DCan'].tolist()
    return result

def FindArrivalCurveSim(f):
    df = pd.read_csv(f,sep=';')
    result=df['ACsim'].tolist()
    return result

def CalculateDepartureCurveTSPEC(arrival,delay,speed,delay1,speed1):      
    service = CalculateServiceCurveTSPEC(delay,speed,delay1,speed1)
    departure = mp.MinPlusConvolve(service,arrival)
    return departure

def CalculateServiceCurveTSPEC(delay,speed,bs,speed1):
    c1=CalculateServiceCurveRSPEC(speed,delay)
    c2=mp.CreateLineFunction(speed1,bs*speed)
    ServiceCurve=mp.MinFunction(c1,c2)
    for i in range(0,len(ServiceCurve)):
        if ServiceCurve[i]<0:
            ServiceCurve[i] = 0               
    return ServiceCurve


def TSPEC(arr):
    p=MaxRate(arr)
    r=ACLinear(arr)[0]
    for burst in header.burstSize:
        b=p*burst
        f1=mp.CreateLineFunction(p,1)
        f2=mp.CreateLineFunction(r,b)
        f1[0]=0
        f2[0]=0
        minF = mp.MinFunction(f1,f2)
        if CheckCurves(arr,minF):
            return minF
        
    return []

def MaxRate(arr):
    slope=0
    for i in range(1,len(arr)):
        slope=max(slope,arr[i]-arr[i-1])
    return slope

def ACLinear(y):
    x=[0]*len(y)
    for i in range(0,len(x)):
        x[i]=i
    return np.polyfit(x,y,1)


def SustainableRate(arr):
    slope=[]
    for i in range(0,len(arr)-1):
        s=arr[i+1]-arr[i]
        if s!=0:
            slope.append(s)
    return statistics.median(slope)

def TSPECSusRate(arr):
    p=SustainableRate(arr[:int(len(arr)/2)])
    r=SustainableRate(arr[int(len(arr)/2):])
    print(p,r)
    for burst in header.burstSize:
        b=p*burst
        f1=mp.CreateLineFunction(p,0)
        f2=mp.CreateLineFunction(r,b)
        f1[0]=0
        f2[0]=0
        minF = mp.MinFunction(f1,f2)
        if CheckCurves(arr,minF):
            return minF

    return minF

def SCurveOffset(df):
    offset=0
    for col in df.columns:
        for i in range(0,df.shape[0]):
            if df[col][i]==0 and offset<i:
                offset+=1
            elif df[col][i]>0:
                break;
    return offset
    
