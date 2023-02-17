import header
import TrafficDemand as TD
import os
import CalculateCurves as CRV
import RealSim as RS

#generate real traffic demand and execute simulations
#rs=RS.RealSim(os.path.join(header.current_directory,'NCOut'))
#rs.ExecuteSimulations(os.path.join(header.current_directory,'NCOut'))
mp = CRV.RealSimCurves('NCOut/CR')
#mp.Curves()
mp.RealSimStatistic()

#generate synthetic traffic demand and execute simulations
#td = TD.TrafficDemand(os.path.join(header.current_directory,'NCOut'))
#td.ExamineDefaultTLS()

#mp = CRV.MPCurves('NCOut')
#mp.Curves()
#mp.MPStatistics()

'''
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
'''



        
    


    

        
    
    
