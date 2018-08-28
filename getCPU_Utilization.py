##############################################################################
#  Copyright (c) 2018 Intel Corporation
# 
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
##############################################################################
#    File Abstract: 
#    This attempts to get CPU utilization information on a Linux System
#
##############################################################################

from time import sleep
from pprint import pprint as pprint
import time
import sys
import os
import argparse


#Worker class to get cpu load info
class CPULoad(object):
    def __init__(self, period = 1):
        self._period = period #how long to wait when getting 2nd reading

    def calcCPU_Time(self):

        cpu_infoMap = {} 
        with open('/proc/stat','r') as fpStats:
            lines = [line.split(' ') for content in fpStats.readlines() for line in content.split('\n') if line.startswith('cpu')]

            for cpu_line_list in lines:
                if '' in cpu_line_list: cpu_line_list.remove('')
                cpu_line_list = [cpu_line_list[0]]+[float(i) for i in cpu_line_list[1:]]
                cpu_id,user,nice,system,idle,iowait,irq,softrig,steal,guest,guest_nice = cpu_line_list

                Idle=idle+iowait
                NonIdle=user+nice+system+irq+softrig+steal

                Total=Idle+NonIdle
                
                cpu_infoMap.update({cpu_id:{'total':Total,'idle':Idle}})
            return cpu_infoMap

    def getcpuload(self):
        # Remember that Percentage=((Total-PrevTotal)-(Idle-PrevIdle))/(Total-PrevTotal)
        # read 1
        start = self.calcCPU_Time()
        #snooze a bit
        sleep(self._period)
        #read 2
        stop = self.calcCPU_Time()

        cpu_load_List = {}

        for cpu in start:
            Total = stop[cpu]['total']
            PrevTotal = start[cpu]['total']

            Idle = stop[cpu]['idle']
            PrevIdle = start[cpu]['idle']
            CPU_Percentage=((Total-PrevTotal)-(Idle-PrevIdle))/(Total-PrevTotal)*100
            cpu_load_List.update({cpu: CPU_Percentage})
        return cpu_load_List 
        
def WriteData(what,where,verbose):
    if None == where or verbose:
        pprint(what)
        
    if None != where:
        where.write(str(what))
        where.write('\n')
        
def main():
    parser = argparse.ArgumentParser(description='Gets CPU Utilization')

    parser.add_argument("-o", "--output",help="file to write to", type=str)
    parser.add_argument("-t", "--time",help="time (in seconds) to gather CPU Utilization ",type=int, default=10)
    parser.add_argument("-i", "--interval",help="how often to gather the data",type=float,default=1.0)
    parser.add_argument("-p", "--precision",help="number of decimal places",type=int,default=3)
    parser.add_argument("-v", "--verbose",help="write to console as well as to specified output file",action='store_true',default=False)
    
    try:
        args = parser.parse_args()
        if args.time < 1:
           pprint("Minimum run time is one sec")
           return
        
        if None != args.output:
            where = open(args.output,"wt")
        else:
            where = None
            
        if args.interval < .1:
           pprint("Minimum run time is one .1 sec")
           return
        
    except:
        return
        
    
    loadObj = CPULoad(args.interval)        
    printFmtStr = "{0:." + str(args.precision) + "f}"
        
    WriteData("Gathering CPU Utilization every {0} seconds for {1} seconds.".format(args.interval,args.time),where,args.verbose)
    startTime = time.time()
    try:
        while time.time() - startTime < args.time:
            data = printFmtStr.format(loadObj.getcpuload()['cpu'])
            WriteData(data,where,args.verbose)
            
    except: # likely a Ctrl+C, so just break out
        pass
        
    if None != args.output:
        where.close()
        
if __name__ == "__main__":
    main()
        
        