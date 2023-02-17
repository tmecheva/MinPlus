import header
import TrafficDemand as TD
import os
import CalculateCurves as CRV 

    
tdAV = TD.TrafficDemand(os.path.join(header.current_directory,'AVOut'))
tdAV.ExamineAV()
av = CRV.TOCurves('AVOut',header.AVpercent)
av.CalcCurves()
av.MPStatistics()


TDtls = TD.TrafficDemand(os.path.join(header.current_directory,'TLSOut'))
TDtls.ExamineAllTLS()
tls = CRV.TOCurves('TLSOut',header.tls_ADmethod)
tls.CalcCurves()
tls.MPStatistics()


        
    


    

        
    
    
