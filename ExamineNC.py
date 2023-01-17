import header
import TrafficDemand as TD
import os
import CalculateCurves as CRV 


#td = TD.TrafficDemand(os.path.join(header.current_directory,'NCOut'))
#td.ExamineDefaultTLS()

mp = CRV.MPCurves('NCOut')
#mp.Curves()

mp.FindSCurves()
mp.IntegralSC(['largeL','largeR'],'large')
mp.IntegralSC(['largeLup','largeLdown'],'largeL')
mp.IntegralSC(['largeRup','largeRdown'],'largeR')

mp.IntegralSC(['3junctions','Metro-SktP'],'4junctions')
mp.IntegralSC(['Izt-Mend','Tol-SktPL'],'3junctions')
mp.IntegralSC(['Metro','SktPR'],'Metro-SktP')
mp.IntegralSC(['Izt-HrB','Mend-SktP'],'Izt-Mend')
mp.IntegralSC(['SktP','Tol-SktP'],'Tol-SktPL')

mp.IntegralStatistics(['large','largeL','largeR','4junctions','3junctions','Metro-SktP','Izt-Mend','Tol-SktPL'])

#mp.MPStatistics()




        
    


    

        
    
    
