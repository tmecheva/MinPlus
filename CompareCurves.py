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

def FindArrivalCurveAn(f):
    df = pd.read_csv(f,sep=';')
    result=df['ACan'].tolist()
    return result

def FindArrivalCurveSim(f):
    df = pd.read_csv(f,sep=';')
    result=df['ACsim'].tolist()
    return result

def CalcError(small,big):
    if len(small)!=len(big):
        return False
    else:
        err=[0]*len(big)
        for i in range(0,len(big)):
            if big[i]<small[i]:
                err[i] = ((small[i]-big[i])/big[i])*100
        return sum(err)/len(err)
    
def CompareSC(Nlist,Nintegral):
    ErrorDF = pd.DataFrame()
    for tls in header.tls_ADmethod:
        for td in header.period:
            sc = FindSC(os.path.join(header.sc_path,Nlist[0]+'.csv'))
            df=pd.DataFrame(data={'sc'+Nlist[0]:sc})
            for i in range(1,len(Nlist)):
                sc2 = FindSC(os.path.join(header.sc_path,Nlist[i]+'.csv'))
                df['sc'+Nlist[i]]=sc2
                sc=MinPlus.MinPlusConvolve(sc,sc2)

            ac=FindArrivalCurveSim(os.path.join(header.curves_path,Nintegral+tls+'_'+td+'.csv'))
            acan=FindArrivalCurveAn(os.path.join(header.curves_path,Nintegral+tls+'_'+td+'.csv'))
            dcan=MinPlus.MinPlusConvolve(ac,sc)
            dcsim=FindDepartureCurveSim(os.path.join(header.curves_path,Nintegral+tls+'_'+td+'.csv'))
            
            df['SC'+Nintegral]=sc
            df['AC']=ac
            df['ACan']=acan
            df['DCsim']=dcsim
            df['DCan']=dcan
            
            df.to_csv(os.path.join(header.sc_path,'SC'+tls+td+Nintegral+'.csv'),sep=';')
            e=CalcError(dcan,dcsim)
            print(e)
            ErrorDF[tls+td+Nintegral]=[e]
    ErrorDF.to_csv(os.path.join(header.sc_path,'Errors.csv'),mode='a')
    
def FindSCurves(net):
    if not os.path.exists(header.sc_path):
        os.makedirs(header.sc_path)
    result=pd.DataFrame()
    for tls in header.tls_ADmethod:
        df3=pd.DataFrame()
        for td in header.period:
            result[tls+td]=FindServiceCurve(os.path.join(header.curves_path,net+tls+'_'+td+'.csv'))            
        result.to_csv(os.path.join(header.sc_path,net+'.csv'),sep=';')

def FindSC(f):
    df = pd.read_csv(f,sep=';',index_col=0)
    sc=df.iloc[:, 0]    
    for col in df.columns:
        sc = MinPlus.MinFunction(sc,df[col])
    return sc

def FindDCurves(net):
    if not os.path.exists(header.dc_path):
        os.makedirs(header.dc_path)
    result=pd.DataFrame()
    for tls in header.tls_ADmethod:
        df3=pd.DataFrame()
        for td in header.period:
            result[tls+td]=FindDepartureCurveSim(os.path.join(header.curves_path,net+tls+'_'+td+'.csv'))
        result.to_csv(os.path.join(header.dc_path,net+'.csv'),sep=';')
        
def FindACurves(net):
    if not os.path.exists(header.ac_path):
        os.makedirs(header.ac_path)
    result=pd.DataFrame()
    for tls in header.tls_ADmethod:
        df3=pd.DataFrame()
        for td in header.period:
            result[tls+td]=FindArrivalCurveSim(os.path.join(header.curves_path,net+tls+'_'+td+'.csv'))
        result.to_csv(os.path.join(header.ac_path,net+'.csv'),sep=';')

for net in header.networks:
    FindDCurves(net)
    FindACurves(net)
    FindSCurves(net)
    
CompareSC(['Izt-HrB','Mend-SktP'],'Izt-Mend')
CompareSC(['SktP','Tol-SktP'],'Tol-SktPL')
CompareSC(['Izt-HrB','Mend-SktP','SktP','Tol-SktP'],'large')




