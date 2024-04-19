import subprocess
import sys
import math
import os
from pathlib import Path

class Executor:

    def __init__(self, logger, data):
        self.logger = logger
        self.data = data

    def execute_path(self):
        #process = subprocess.run(path)
        path = self.data["masa_path"]
        os.environ["PATH"] = path
        self.logger.info("Exporting MASA-CUDAlign path: "+path)
        #print("process: ", process)

    def execute(self, args):
        command = args.split(" ")# + list(args)
        self.logger.info("MASA-CUDAlign command created: "+ args)
        process = subprocess.run(command)
        return process

    #calculate SRA size
    def calculate_sra_size(self,seq1_length):
        return str(math.ceil(((seq1_length*8)/(1024*1024*1024))*100))

    #strategy definition for stage 4
    def define_strategy(self,score):
        #--stage-4-strategy=$STRATEGY
        strategy = "ORIGINAL_MM"
        #similarity calculation
        seq0_length = int(self.data["seq0_length"])
        seq1_length = int(self.data["seq1_length"])
        #definition of limiar | threshold < 100 -> CPU
        #ver depois
        #threshold = (seq0_length*seq1_length)*0.00000000001
        sim = score / max(seq0_length,seq1_length)

        if(sim > float(self.data["strategy_threshold"])):
            strategy = "MM_GPU"

        return strategy

    #return the score stored at statistics_01 file after termination of stage 1
    def look_for_score(self):
        framework_dir = os.getcwd() + "/" + self.data["work_dir"]
        file = open(framework_dir + "/statistics_01.00", "r")
        lines = file.readlines()
        line = lines[17 - 1]
        print("line:", line)
        sco = line.split(": ")
        print("score[1]: ",int(sco[1]))
        score = int(sco[1])
        file.close()
        return score
        #corrigir para pegar o tempo de execução do estágio 1
    def look_for_time(self):
        framework_dir = os.getcwd() + "/" + self.data["work_dir"]
        file = open(framework_dir + "/statistics_01.00", "r")
        lines = file.readlines()
        line = lines[17 - 1]
        print("line:", line)
        sco = line.split(": ")
        print("score[1]: ",int(sco[1]))
        score = int(sco[1])
        file.close()
        return score

    #somar o tempo total de execução
    def create_masa_command(self):
        current_dir = os.getcwd()
        self.logger.info("Current directory: "+current_dir)

        home = str(Path.home())
        #self.execute_path(dados["masa_path"])
        self.logger.info("Home directory: "+home)
        SRA = self.calculate_sra_size(self.data["seq1_length"])

        self.logger.info("SRA size calculated: "+SRA+"G")
        #stage-1 execution
        command = self.data["command"] + " --disk-size=" + SRA+"G" + " --stage-1" +" --work-dir=" + self.data["work_dir"] + " " + home + self.data["sequence0"] + " " + home + self.data["sequence1"] # + "+dados["task_file"]

        response = self.execute(command)

        print("Stage 1 execution complete: ",response)

        score = self.look_for_score()

        strategy = self.define_strategy(score)

        command = self.data["command"] + " --disk-size=" + SRA+"G" +" --stage-4-strategy=" + strategy + " --work-dir=" + self.data["work_dir"] + " " + home + self.data["sequence0"] + " " + home + self.data["sequence1"] # + "+dados["task_file"]
        response = self.execute(command)

        return command
