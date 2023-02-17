import os
current_directory = os.getcwd()

simulation_path = os.path.join(current_directory,'Sim')
network_path=os.path.join(simulation_path,'net')
additional_path=os.path.join(current_directory,'add')
sumo_tools_path = "/usr/share/sumo/tools/"
conf_path = os.path.join(current_directory,'realSimCfg')

#out_path = os.path.join(current_directory,'Out')
#curves_path = os.path.join(out_path,'Curves')
#dc_path = os.path.join(curves_path,'DC')
#ac_path = os.path.join(curves_path,'AC')
#sc_path = os.path.join(curves_path,'SC')
#sc_integral_path = os.path.join(curves_path,'SCintegral')
#tls_path = os.path.join(out_path,'TLS')
#routes_path = os.path.join(out_path,'Routes')
#result_path = os.path.join(out_path,'Result')
tripinfo_folder = 'Tripinfo'
stat_folder = 'Stat'

period = ['1.0','0.9','0.8','0.7','0.6','0.5','0.4','0.3','0.2','0.1']
AVpercent = ['0.0','0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1.0']

speed = [13.8]#[14,13.5,13,12.5,12,11.5,11,10.5,10,9.5,9,8.5,8,7.5,7,6.5,6,5.5,5]
networks = ['Metro','SktP','SktPR','Izt-HrB','Izt-Mend','Tol-SktP','Tol-SktPL','Metro-SktP','Mend-SktP','3junctions','4junctions','large','largeL','largeR','largeLup','largeLdown','largeRup','largeRdown']

Lnetworks = ['large','largeL','largeR','largeLup','largeLdown','largeRup','largeRdown']


tls_ADmethod = ['Default','Adapted','Coordinated']#,'30-90AD']#

def CalcMaxDelay():
    maxDelay = []
    for i in range(5,360):
        maxDelay.append(i*10)
    return maxDelay
        
maxDelay=CalcMaxDelay()
