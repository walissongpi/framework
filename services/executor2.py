import subprocess
import sys
import math
import os
from pathlib import Path
from services.decision_maker import DecisionMaker

class Executor2:

    def __init__(self, logger, data, gpu_data):
        self.logger = logger
        self.data = data
        self.gpu_data = gpu_data

    def execute_path(self):
        #process = subprocess.run(path)
        path = self.data["masa_path"]
        os.environ["PATH"] = path
        self.logger.info("Exporting MASA-CUDAlign path: "+path)
        #print("process: ", process)

    def execute(self, args):
        command = args.split(" ")# + list(args)
        self.logger.info("MASA-CUDAlign command created: "+ args)

        home = str(Path.home())
        framework_dir =  home+"/"+self.data["work_dir"]

        process = None
        #with open(framework_dir+'/framework_out.txt', 'w') as outfile:
        #process = subprocess.run(command, shell=True, stdout=outfile, capture_output=True, text=True)
        #process = subprocess.run(command, shell=True)
        os.environ['LD_LIBRARY_PATH'] = '$LD_LIBRARY_PATH:/usr/local/cuda-11.7/lib64'
        os.environ['PATH'] = '$PATH:/usr/local/cuda-11.7/bin'

        process = subprocess.call(command)
        self.logger.info("Process: "+str(process))
        #process = subprocess.run(command)
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

    def calculate_similarity(self, score):
        seq0_length = int(self.data["seq0_length"])
        seq1_length = int(self.data["seq1_length"])
        sim = (score / max(seq0_length,seq1_length))*100
        return sim
    #return the score stored at statistics_01 file after termination of stage 1
    def look_for_score(self):
        home = str(Path.home())
        framework_dir =  home+"/"+self.data["work_dir"]

         #= os.getcwd() + "/framework/" + self.data["work_dir"]
        #file = open(framework_dir + "/statistics_01.00", "r")
        print("framework dir: "+framework_dir)
        file = open(framework_dir + "/status", "r")
        lines = file.readlines()

        line = lines[2]
        print("Passou pela linha aqui")
        print("testando a line:", line)
        sco = line.split(" ")
        print("score[2]: ",int(sco[2]))
        score = int(sco[1])
        file.close()
        return score
        #corrigir para pegar o tempo de execução do estágio 1
    def look_for_time(self):
        home = str(Path.home())
        framework_dir = home + "/" + self.data["work_dir"]
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
        work_dir =  home+"/"+self.data["work_dir"]
        #stage-1 execution
        masa = home + "/MASA-CUDAlign/masa-cudalign-4.0.2.1028/"
        command = masa + self.data["command"] + " --disk-size=" + SRA+"G" + " --stage-1" +" --work-dir=" +work_dir + " " + home + self.data["sequence0"] + " " + home + self.data["sequence1"] # + "+dados["task_file"]
        #exec = "sh framework/execute.sh "+ command
        response = self.execute(command)

        self.logger.info("Stage 1 execution complete: "+str(response))

        score = self.look_for_score()

        sequence_similarity = round(self.calculate_similarity(score))
        self.logger.info("Sequence similarity: "+ str(sequence_similarity))

        decision_maker = DecisionMaker(self.logger, self.data, self.gpu_data, sequence_similarity)
        strategy = decision_maker.decide_strategy_stage4()

        self.logger.info("Stratrgy for stage 4: "+strategy)

        #preciso interromper a instância e executar novamente
        #strategy = self.define_strategy(score)
        command = masa + self.data["command"] + " --disk-size=" + SRA+"G" +" --stage-4-strategy=" + strategy + " --work-dir=" +work_dir+ " " + home + self.data["sequence0"] + " " + home + self.data["sequence1"] # + "+dados["task_file"]

        #stage subsequentes execution

        #response = self.execute(command)
        self.logger.info("It is time to execute subsequente stages on a new and powerful instance");

        return command

    def create_masa_stage_4(self):

        current_dir = os.getcwd()
        self.logger.info("Current directory: "+current_dir)

        home = str(Path.home())
        #self.execute_path(dados["masa_path"])
        self.logger.info("Home directory: "+home)
        SRA = self.calculate_sra_size(self.data["seq1_length"])

        self.logger.info("SRA size calculated: "+SRA+"G")
        work_dir =  home+"/"+self.data["work_dir"]
        #stage-1 execution
        masa = home + "/MASA-CUDAlign/masa-cudalign-4.0.2.1028/"
        command = masa + self.data["command"] + " --disk-size=" + SRA+"G" +" --work-dir=" +work_dir + " " + home + self.data["sequence0"] + " " + home + self.data["sequence1"] # + "+dados["task_file"]
        #exec = "sh framework/execute.sh "+ command
        response = self.execute(command)

        #self.logger.info("Stage 1 execution complete: "+str(response))

        #score = self.look_for_score()

        #sequence_similarity = round(self.calculate_similarity(score))
        #self.logger.info("Sequence similarity: "+ str(sequence_similarity))

        #decision_maker = DecisionMaker(self.logger, self.data, self.gpu_data, sequence_similarity)
        #strategy = decision_maker.decide_strategy_stage4()

        #self.logger.info("Stratrgy for stage 4: "+strategy)

        #preciso interromper a instância e executar novamente
        #strategy = self.define_strategy(score)
        #command = masa + self.data["command"] + " --disk-size=" + SRA+"G" +" --stage-4-strategy=" + strategy + " --work-dir=" +work_dir+ " " + home + self.data["sequence0"] + " " + home + self.data["sequence1"] # + "+dados["task_file"]

        #stage subsequentes execution

        #response = self.execute(command)
        #self.logger.info("It is time to execute subsequente stages on a new and powerful instance");

        return command
