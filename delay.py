#Concatenates all Departure and Arrival curves and output the dataframe to a csv file
import header
import os
import pandas as pd
import MinPlus
import re  
'''
def FindServiceCurve(f):
    df = pd.read_csv(f,sep=';')
    series=df.filter(regex='Dist*').mean().to_dict()
    result = pd.DataFrame(data=[series.keys(), series.values()]).T
    result.columns=['delay','distance']
    result.set_index('delay',inplace = True)
    min_dist = result['distance'].min()
    delay=str(result[result['distance'] == min_dist].index.values)
    delay_speed=delay.replace('Dist','').replace('[','').replace(']','').replace("'","").split('_',3)
    delay=float(delay_speed[1])
    speed=float(delay_speed[2])
    return MinPlus.CalculateServiceCurveAnalitical(delay,speed)
'''

def FindServiceCurve(f):
    df = pd.read_csv(f,sep=';')
    result=df['SC'].tolist()
    return result

def FindDepartureCurveSim(f):
    df = pd.read_csv(f,sep=';')
    result=df['DCsim'].tolist()
    return result

def FindDepartureCurveAn(f):
    df = pd.read_csv(f,sep=';')
    result=df['DCan'].tolist()
    return result

def FindArrivalCurve(f):
    df = pd.read_csv(f,sep=';')
    result=df['AC'].tolist()
    return result

def CompareSC(n1,n2,n3):
    for tls in header.tls_ADmethod:
        for td in header.period:
            sc1 = FindServiceCurve(os.path.join(header.dc_path,n1+tls+'_'+td+'.csv'))
            sc2 = FindServiceCurve(os.path.join(header.dc_path,n2+tls+'_'+td+'.csv'))
            
            sc3=MinPlus.MinPlusConvolve(sc1,sc2)
            ac3=FindArrivalCurve(os.path.join(header.dc_path,n3+tls+'_'+td+'.csv'))
            dc3an=MinPlus.MinPlusConvolve(ac3,sc3)
            dc3sim=FindDepartureCurveSim(os.path.join(header.dc_path,n3+tls+'_'+td+'.csv'))

            df3=pd.DataFrame(data={'sc1':sc1,'sc2':sc2,'sc3':sc3,'ac3':ac3,'DCsim'+tls+td+n3:dc3sim,'DCan'+tls+td+n3:dc3an})
            df3.to_csv(os.path.join(header.result_path,'SC'+tls+td+n3+'.csv'))
    
def FindSC(path):
    df = pd.read_csv(path,sep=';')
    sc=df.iloc[:, 0]
    for col in df.columns:
        sc = MinPlus.MinFunction(sc,df[col])
    return sc

for net in header.simpleNets:
    FindDC(net)
    FindAC(net)
    FindSC(net)


