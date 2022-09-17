import os

simulation_path = "/home/tedy/Sumo/script/Min-Plus/Sim"
network_path=os.path.join(simulation_path,'net')
sumo_tools_path = "/usr/share/sumo/tools/"
current_directory = os.getcwd()

out_path = os.path.join(current_directory,'Out')
curves_path = os.path.join(out_path,'Curves')
dc_path = os.path.join(curves_path,'DC')
ac_path = os.path.join(curves_path,'AC')
sc_path = os.path.join(curves_path,'SC')
tls_path = os.path.join(out_path,'TLS')
routes_path = os.path.join(out_path,'Routes')
result_path = os.path.join(out_path,'Result')
tripinfo_folder = 'Tripinfo'
stat_folder = 'Stat'

period = ['0.01','0.02','0.03','0.04','0.05','0.06','0.07','0.08','0.09','0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1.0']
speed = [13.8]#,12.5,11.1,9.7,8.3,6.9,5.5]
networks = ['large','Mend-SktP','Izt-HrB','Izt-Mend','Tol-SktP','Tol-SktPL','SktP']
tls_ADmethod = ['Default']#['DefaultAD','CoordinatedAD']#

def CalcMaxDelay():
    maxDelay = []
    for i in range(5,360):
        maxDelay.append(i*10)
    return maxDelay


def CalcBurstSize():
    burstSize = []
    for i in range(1,360):
        burstSize.append(i)
    return burstSize
        
maxDelay=CalcMaxDelay()
burstSize=CalcBurstSize()
