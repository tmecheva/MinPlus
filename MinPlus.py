import sys
import os
import header
import pandas as pd
import numpy as np
import statistics 
    
def CreateLineFunction(a,b):
    result=[0]*360
    for i in range(0,len(result)):
        result[i]=a*i+b
    return result

def MaxFunction(a,b):
    if len(a) != len(b):
        print('Error!!!')
        return
    else:
        z=[0]*len(a)
        for x in range(0,len(z)):
            z[x]=max(a[x],b[x])

    return z

def MinFunction(a,b):
    if len(a) != len(b):
        print('Error!!!')
        return
    else:
        z=[0]*len(a)
        for x in range(0,len(z)):
            z[x]=min(a[x],b[x])

    return z
                    
def MinPlusConvolve(arr1p,arr2p):
    arr1=arr1p.copy()
    arr2=arr2p.copy()
    if len(arr1) != len(arr2):
        print('Error!!!')
        return
    else:
        lenght =len(arr1)
        z=[0]*lenght
        z[0] = arr1[0]+arr2[0]

        for x in range(1,lenght):
                
            a1=arr1[x]-arr1[x-1]
            a2=arr2[x]-arr2[x-1]
            
            if arr1[x]-arr1[0]<arr2[x]-arr2[0]:
                a=a1
            elif arr1[x]-arr1[0]>arr2[x]-arr2[0]:
                a=a2
            else:
                a=max(a1,a2)
                
            z[x]=z[x-1]+a
            
            if a1==0 and arr1[x]==0:
                arr2.insert(x-1,arr2[x-1])
            elif a2==0 and arr2[x]==0:
                arr1.insert(x-1,arr1[x-1])

        return z

def CalculateServiceCurveAnalitical(speed,Ta):
    ServiceCurve=[0]*360
    for i in range(0,len(ServiceCurve)):
        t=i*10
        if t-Ta<=0:
            ServiceCurve[i] = 0
        else:
            ServiceCurve[i]=speed*(t-Ta)                
    return ServiceCurve

def MaxRate(arr):
    slope=0
    for i in range(1,len(arr)):
        slope=max(slope,arr[i]-arr[i-1])
    return slope

def SustainableRate(arr):
    slope=[]
    for i in range(0,len(arr)-1):
        s=arr[i+1]-arr[i]
        if s!=0:
            slope.append(s)
    return statistics.multimode(slope)[0]

def CheckCurves(small,big):
    if len(small)!=len(big):
        return False
    else:
        for i in range(0,len(big)):
            if big[i]<small[i]:
                return False        
        return True

def TSPECSusRate(arr):
    p=MaxRate(arr)
    r=SustainableRate(arr)
    for burst in header.burstSize:
        b=p*burst
        f1=CreateLineFunction(p,1)
        f2=CreateLineFunction(r,b)
        f1[0]=0
        f2[0]=0
        minF = MinFunction(f1,f2)
        if CheckCurves(arr,minF):
            return minF

    return []

def TSPEC(arr):
    p=MaxRate(arr)
    r=ACLinear(arr)[0]
    for burst in header.burstSize:
        b=p*burst
        f1=CreateLineFunction(p,1)
        f2=CreateLineFunction(r,b)
        f1[0]=0
        f2[0]=0
        minF = MinFunction(f1,f2)
        if CheckCurves(arr,minF):
            return minF
        
    return []

def ACLinear(y):
    x=[0]*len(y)
    for i in range(0,len(x)):
        x[i]=i
    return np.polyfit(x,y,1)
    
def Convolve(a,b,c,d,e,f,g,h):
    x0 = CreateLineFunction(0,0)
    
    f1 = CreateLineFunction(a,b)    
    f2 = CreateLineFunction(c,d)
    
    f3 = CreateLineFunction(e,f)
    f6= CreateLineFunction(g,h)
        
    x=MinFunction(f1,f2)
    y=MinFunction(x,f3)

    f5=MaxFunction(y,x0)
    f4=MaxFunction(f6,x0)
    
    result = pd.DataFrame(data=f5,columns=['f5'])
    result['f4'] = f4
    z = pd.DataFrame(data = MinPlusConvolve(f4,f5),columns=['Z'])
    result = pd.concat([result,z],axis=1)        
    result.to_csv(os.path.join(header.out_path,'Convolution.csv'),sep=';')
    
#Convolve(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]),int(sys.argv[7]),int(sys.argv[8]))


        

        
        
