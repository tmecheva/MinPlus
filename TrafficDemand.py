import subprocess
import sys
import os
import pandas as pdr543rew
import xml.etree.ElementTree as ET
sys.path.append(os.path.join(os.environ.get("SUMO_HOME"), 'tools'))
import traci
import traci.constants as tc
import header

    
class TrafficLights:
    def __init__(self):        

        if not os.path.exists(header.out_path):
            os.makedirs(header.out_path)
            
        if not os.path.exists(header.routes_path):
            os.makedirs(header.routes_path)
        
        if not os.path.exists(header.result_path):
            os.makedirs(header.result_path)

            
    #Generates random traffic demand with period of generation p
    def CallRandomTrips(self,p,net):
        d=os.path.join(header.routes_path,net)
        if not os.path.exists(d):
            os.makedirs(d)
            
        command='python3 '+os.path.join(header.sumo_tools_path,'randomTrips.py')+' -e 3600 --validate -n '+os.path.join(header.network_path,net+'.net.xml')+' -p '+str(p)+' -L --allow-fringe -r '+os.path.join(d,str(p)+'.xml')
        subprocess.run(command,shell=True)
        
    #
    def ConfigSumo(self,p,net,tls_path):
        this_tls_stat_path = os.path.join(tls_path,header.stat_folder)
        this_tls_tripinfo_path = os.path.join(tls_path,header.tripinfo_folder)
        
        if not os.path.exists(this_tls_stat_path):
            os.makedirs(this_tls_stat_path)
        if not os.path.exists(this_tls_tripinfo_path):
            os.makedirs(this_tls_tripinfo_path)
            
        tree = ET.parse(os.path.join(header.simulation_path,"osm.sumocfg"))
        root = tree.getroot()
        for el in root:
            for subel in el:
                if subel.tag == 'net-file':
                    subel.set('value',os.path.join(header.network_path,net+'.net.xml'))
                if subel.tag == 'route-files':
                    subel.set('value',os.path.join(header.routes_path,net,str(p)+'.xml'))
                if subel.tag == 'statistic-output':
                    subel.set('value',os.path.join(this_tls_stat_path,str(p)+'.xml'))
                if subel.tag == 'tripinfo-output':
                    subel.set('value',os.path.join(this_tls_tripinfo_path,str(p)+'.xml'))
        tree.write(os.path.join(header.simulation_path,"osm.sumocfg"))        
    
    #Call sumo with adapted tls additional with period p
    def CallSumoAdapted(self,p,net,*args):
        tlsdir = ' '.join(map(str,args)).replace(' ','-').replace('(','').replace(')','').replace(',','').replace("'","")
        this_result_path = os.path.join(header.result_path,net,str(tlsdir)+'AD')
        if not os.path.exists(this_result_path):
            os.makedirs(this_result_path)
            
        self.ConfigSumo(p,net,this_result_path)        
        
        command="sumo -c "+os.path.join(header.simulation_path,"osm.sumocfg")+" -a "+os.path.join(header.tls_path,net,tlsdir,str(p)+'.xml')
        subprocess.run(command,shell=True)
    
    #Calls sumo with default tls
    def CallSumoDefault(self,p,net):
        print(net)
        self.ConfigSumo(p,net,os.path.join(header.result_path,net,"Default"))
        
        command="sumo -c "+os.path.join(header.simulation_path,"osm.sumocfg")
        subprocess.run(command,shell=True)
        
    
    #Calls tlsCycleAdaptation tool for a given traffic demand
    def CalculateAdaptedTLS(self,p,net,*args):        
        if len(args)==2:
            commandSuff = ' -c '+str(args[0])+' -C '+str(args[1])
        else:
            commandSuff=''
            
        tlsdir = ' '.join(map(str,args)).replace(' ','-').replace('(','').replace(')','').replace(',','').replace("'","")             
        tlspath = os.path.join(header.tls_path,net,str(tlsdir))
        print(tlspath)
        
        if not os.path.exists(tlspath):
            os.makedirs(tlspath)
            
        command = 'python3 '+os.path.join(header.sumo_tools_path,'tlsCycleAdaptation.py')+' -n '+os.path.join(header.network_path,net+'.net.xml')+' -r '+os.path.join(header.routes_path,net,str(p)+'.xml')+' -o '+os.path.join(tlspath,str(p)+'.xml')+commandSuff

        subprocess.run(command,shell=True)
        
    def CalculateCoordinatedTLS(self,p,net):
        coordinated_path = os.path.join(header.tls_path,net,"Coordinated")
        if not os.path.exists(coordinated_path):
            os.makedirs(coordinated_path)
            
        command = 'python3 '+os.path.join(header.sumo_tools_path,'tlsCoordinator.py')+' -n '+os.path.join(header.network_path,net+'.net.xml')+' -r '+os.path.join(header.routes_path,net,str(p)+'.xml')+' -o '+os.path.join(coordinated_path,str(p)+'.xml')        
        subprocess.run(command,shell=True)
        
    def ExamineDefaultTLS(self,net):
        for i in header.period:
            self.CallSumoDefault(i,net)
            
    def ExamineCoordinatedTLS(self,net):
        for i in header.period:
            self.CalculateCoordinatedTLS(i,net)
            self.CallSumoAdapted(i,net,"Coordinated")
                
    def ExamineAdaptedTLS(self,net,*args):
        for i in header.period:
            self.CalculateAdaptedTLS(i,net,args)
            self.CallSumoAdapted(i,net,args)
                
    def GenerateAllTirps(self,net):
        for i in header.period:
            self.CallRandomTrips(i,net)    
        

tl=TrafficLights()
for net in header.networks:            
    #tl.GenerateAllTirps(net)    
    #tl.ExamineDefaultTLS(net)    
    tl.ExamineCoordinatedTLS(net)    
    tl.ExamineAdaptedTLS(net,"Default")
    
    #tl.ExamineAdaptedTLS(net,90,120)    
    #tl.ExamineAdaptedTLS(net,90,130)    
    #tl.ExamineAdaptedTLS(net,90,140)
    



        
    


    

        
    
    
