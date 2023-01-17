import sys
import os
import header
import pandas as pd
 
    
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


        

        
        
