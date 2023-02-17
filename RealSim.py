import sys
import os
import subprocess
import header
import xml.etree.ElementTree as ET
import ControllerReport as cr

class RealSim:
    def __init__(self,path):
        self.out_path=path
        self.network_path=os.path.join(header.network_path,'Izt-Mend.net.xml')
        cr.CreateConfigFiles(os.path.join(header.current_directory,'NCOut'))
        
    def CallFLowRouter(self,cfgfile):       
        cmd = 'python3 {script_path} -n {net_path} -d {detectors_path} -f {conf_path} -o {output_path} -e {flows_path} --params {prm}'.format(
            script_path=os.path.join(header.sumo_tools_path,"detector/flowrouter.py"),
            net_path=self.network_path,
            detectors_path=os.path.join(header.conf_path,"detectors.xml"),
            conf_path=os.path.join(self.out_path,"CR",cfgfile+".csv"),
            output_path=os.path.join(self.out_path,'CR','Result',cfgfile,"route.xml"),
            flows_path=os.path.join(self.out_path,'CR','Result',cfgfile,"flow.xml"),
            prm='\'type=\"type1\"\''
        )
    
        subprocess.run(cmd, shell=True)
        
    def CreateFlowFile(self,cfgfile):
        line="\t<vType id=\"type1\" carFollowModel=\"Wiedemann\" minGap=\"1.5\" security=\"1\" estimation=\"1\" tau=\"0.25\"/>\n"
        lines=''
        with open(os.path.join(self.out_path,'CR','Result',cfgfile,"flow.xml"), "r") as file:
            lines = file.readlines()
            if lines[1].find('carFollowModel'):
                lines[1]=line
            else:
                lines.insert(1,line)
            file.close()
            
        with open(os.path.join(self.out_path,'CR','Result',cfgfile,"flow.xml"), "w") as file:
            file.writelines(lines)
            file.close()
        
    
    def CallDuaRouter(self,cfg):            
        tree = ET.parse(os.path.join(header.conf_path,'duaCFG.xml'))
        root = tree.getroot()
        for el in root:
            for subel in el:
                if subel.tag == 'net-file':
                    subel.set('value',self.network_path)
                if subel.tag == 'route-files':
                    subel.set('value',os.path.join(self.out_path,'CR','Result',cfg,"route.xml")+","+os.path.join(self.out_path,'CR','Result',cfg,'flow.xml'))
                if subel.tag == 'output-file':
                    subel.set('value',os.path.join(self.out_path,'CR','Result',cfg,'Dua.xml'))
        tree.write(os.path.join(self.out_path,'CR','Result',cfg,'duaCFG.xml'))
        
        command='duarouter -c '+os.path.join(self.out_path,'CR','Result',cfg,'duaCFG.xml')
        subprocess.run(command,shell=True)
        
    def CallSumo(self,cfg):
        tree = ET.parse(os.path.join(header.conf_path,"osm.sumocfg"))
        root = tree.getroot()
        for el in root:
            for subel in el:
                if subel.tag == 'route-files':
                    subel.set('value',os.path.join(self.out_path,'CR','Result',cfg,'Dua.xml'))
                if subel.tag == 'additional-files':
                    subel.set('value',os.path.join(header.conf_path,'detectors.xml'))
                if subel.tag == 'statistic-output':
                    subel.set('value',os.path.join(self.out_path,'CR','Result',cfg,'stat.xml'))
                if subel.tag == 'tripinfo-output':
                    subel.set('value',os.path.join(self.out_path,'CR','Result',cfg,'trip.xml'))
                
        tree.write(os.path.join(header.conf_path,"osm.sumocfg"))
        
        command="sumo -c "+os.path.join(header.conf_path,"osm.sumocfg")
        subprocess.run(command,shell=True) 

    def ExecuteSimulations(self,path):
        rs=RealSim(path)
            
        for f in os.listdir(os.path.join(path,'CR')):
            folder = f.replace('.csv','')
            if not os.path.exists(os.path.join(path,'CR','Result',folder)):
                os.makedirs(os.path.join(path,'CR','Result',folder))
            rs.CallFLowRouter(folder)
            rs.CreateFlowFile(folder)
            rs.CallDuaRouter(folder)
            rs.CallSumo(folder)
            
