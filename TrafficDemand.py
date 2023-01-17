import subprocess
import sys
import os
import pandas as pdr543rew
import xml.etree.ElementTree as ET
sys.path.append(os.path.join(os.environ.get("SUMO_HOME"), 'tools'))
import traci
import traci.constants as tc
import header

    
class TrafficDemand:
    def __init__(self,out_path):
        self.result_path = os.path.join(out_path,'Result')
        self.routes_path = os.path.join(out_path,'Routes')
        self.tls_path = os.path.join(out_path,'TLS')

        if not os.path.exists(out_path):
            os.makedirs(out_path)
            
        if not os.path.exists(self.routes_path):
            os.makedirs(self.routes_path)
        
        if not os.path.exists(self.result_path):
            os.makedirs(self.result_path)

            
    #Generates random traffic demand with period of generation p
    def CallRandomTrips(self,p,net,av):
        out_dir=os.path.join(self.routes_path,net,av)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            
        if av:
            add = " --trip-attributes='type=\"vdist1\" ' --additional-file "+ os.path.join(header.additional_path,av+'.add.xml')
        else:
            add=""
            
        command='python3 '+os.path.join(header.sumo_tools_path,'randomTrips.py')+' -e 3600 --validate -n '+os.path.join(header.network_path,net+'.net.xml')+' -p '+str(p)+' -L --allow-fringe -o '+os.path.join(out_dir,str(p)+'t.xml') + add
        subprocess.run(command,shell=True)
        
        print(os.path.join(out_dir,str(p)+'t.xml'))
        command = 'duarouter -r '+os.path.join(out_dir,str(p)+'t.xml')+' -n '+os.path.join(header.network_path,net+'.net.xml') +' --routing-algorithm CH --output-file '+os.path.join(out_dir,str(p)+'r.xml')
        subprocess.run(command,shell=True)
        
    #
    def ConfigSumo(self,p,net,tls,av):
        this_out_stat_path = os.path.join(self.result_path,net,tls,av,header.stat_folder)
        this_out_tripinfo_path = os.path.join(self.result_path,net,tls,av,header.tripinfo_folder)
        
        if not os.path.exists(this_out_stat_path):
            os.makedirs(this_out_stat_path)
        if not os.path.exists(this_out_tripinfo_path):
            os.makedirs(this_out_tripinfo_path)
            
        tree = ET.parse(os.path.join(header.simulation_path,"osm.sumocfg"))
        root = tree.getroot()
        for el in root:
            for subel in el:
                if subel.tag == 'net-file':
                    subel.set('value',os.path.join(header.network_path,net+'.net.xml'))
                if subel.tag == 'route-files':
                    subel.set('value',os.path.join(self.routes_path,net,av,str(p)+'r.xml'))
                if subel.tag == 'statistic-output':
                    subel.set('value',os.path.join(this_out_stat_path,str(p)+'.xml'))
                if subel.tag == 'tripinfo-output':
                    subel.set('value',os.path.join(this_out_tripinfo_path,str(p)+'.xml'))
        tree.write(os.path.join(header.simulation_path,"osm.sumocfg"))        
    
    #Calls sumo with default tls
    def CallSumo(self,p,net,tls,av):
        print(net)
        self.ConfigSumo(p,net,tls,av)
        
        if tls=="Default" or tls=="":
            add=""
        else:
            add=" -a "+os.path.join(self.tls_path,net,tls,str(p)+'.xml')
        
        command="sumo -c "+os.path.join(header.simulation_path,"osm.sumocfg")+add
        subprocess.run(command,shell=True)
        
    
    #Calls tlsCycleAdaptation tool for a given traffic demand
    def CalculateAdaptedTLS(self,p,net):        
        adapted_path = os.path.join(self.tls_path,net,"Adapted")
        if not os.path.exists(adapted_path):
            os.makedirs(adapted_path)
                        
        command = 'python3 '+os.path.join(header.sumo_tools_path,'tlsCycleAdaptation.py')+' -n '+os.path.join(header.network_path,net+'.net.xml')+' -r '+os.path.join(self.routes_path,net,str(p)+'r.xml')+' -o '+os.path.join(adapted_path,str(p)+'.xml')

        subprocess.run(command,shell=True)
        
    def CalculateCoordinatedTLS(self,p,net):
        coordinated_path = os.path.join(self.tls_path,net,"Coordinated")
        if not os.path.exists(coordinated_path):
            os.makedirs(coordinated_path)
            
        command = 'python3 '+os.path.join(header.sumo_tools_path,'tlsCoordinator.py')+' -n '+os.path.join(header.network_path,net+'.net.xml')+' -r '+os.path.join(self.routes_path,net,str(p)+'r.xml')+' -o '+os.path.join(coordinated_path,str(p)+'.xml')        
        subprocess.run(command,shell=True)
        
            
    def ExamineAV(self):
        for net in header.networks:
            for i in header.period:
                for av in header.AVpercent:
                    self.CallRandomTrips(i,net,av)
                    self.CallSumo(i,net,'',av)
                    
    def ExamineDefaultTLS(self):
        for net in header.networks:
            for i in header.period:
                self.CallRandomTrips(i,net,'')
                self.CallSumo(i,net,'','')
                
    def ExamineAllTLS(self):
        for net in header.networks:
            for i in header.period:
                self.CallRandomTrips(i,net,'')
                self.CalculateCoordinatedTLS(i,net)
                self.CalculateAdaptedTLS(i,net)
                
                self.CallSumo(i,net,"Coordinated","")
                self.CallSumo(i,net,"Adapted","")
                self.CallSumo(i,net,'Default',"")
'''               
    def ExamineAdaptedTLS(self,net,*args):
        for i in header.period:
            self.CalculateAdaptedTLS(i,net,args)
            self.CallSumoAdapted(i,net,args)
'''
                




        
    


    

        
    
    
