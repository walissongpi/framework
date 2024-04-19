from services.enviroment import SystemInfo
from services.executor import Executor
from services.ec2 import EC2Manager
from services.ec2executor import EC2ApplicationExecutor
from services.main_cloud import MainCLoud
import math
import os
from pathlib import Path

class CloudEnviroment:

    def __init__(self, logger, data, instance_data, cloud_data, gpu_data):
        self.logger = logger
        self.data = data
        self.instance_data = instance_data
        self.cloud_data = cloud_data
        self.gpu_data = gpu_data

    #def execute(self):
    def get_system_info (self):
        self.logger.info("Getting enviroment information...")
        self.logger.info("System information collected.")

        #utilizar equação de previsão de tempo
    #def define_market(self):
    def time_prediction(self):
        m = int(self.data["seq0_length"])
        n = int(self.data["seq1_length"])
        CP = int(self.gpu_data["cores"]) * int(self.gpu_data["boost_clock"])
        BW = int(self.gpu_data["memory_bandwith"])
        BP = 0
        result = -3.036 + (0.979 * math.log10(m * n)) - (0.344 * math.log10(CP)) - (1.001 * math.log10(BW)) + (0.777* math.log10(1 - BP))
        #print(resp)
        minutes = (math.pow(10,result)/60000)*.9
        return minutes

    def start(self):
        self.logger.info("Listing AWS instances...")
        ec2Manager = EC2Manager(self.logger, self.instance_data, self.cloud_data, self.gpu_data)
        instances = ec2Manager.list_instances()
        for instance in instances:
            self.logger.info(instance)

        self.logger.info("Loading input data information...")
        self.logger.info("Sequence 0: "+ self.data["sequence0"])
        self.logger.info("Sequence 1: "+ self.data["sequence1"])

        minutes = "{:.2f}".format(self.time_prediction())
        self.logger.info("Time estimated for sequence aligment: "+ str(minutes)+ " minutes")

        #if time predcted is < market_threshould -> spot else on-demand
        instance_id = None
        ec2 = None
        if minutes < self.cloud_data["market_threshold"] and self.cloud_data["auto_spot_selection"] == "yes":
            self.logger.info("The expected time for sequence alignment ("+minutes+" minutes) is less than the pre-established threshold ("+self.cloud_data["market_threshold"]+" minutes). The execution will be carried out on a Spot instance...")
            self.logger.info("Creating " + self.instance_data["instance_type"] + " Spot instance...")
            instance_id, ec2 = ec2Manager.create_spot_instance()
            input("")
        else:
            self.logger.info("The expected time for sequence alignment ("+minutes+" minutes) is greater than the pre-established threshold ("+self.cloud_data["market_threshold"]+" minutes). The execution will be carried out on an On-demand instance...")
            self.logger.info("Creating "+ self.instance_data["instance_type"]+" On-demand instance...")
            instance_id, ec2 = ec2Manager.create_instance()
            input("")

        if instance_id is None:
            self.logger.error("Unable to initialize instance. Please, start over using local module...");
            return
        else:
            self.logger.info("Instance id: "+instance_id)
            self.logger.info("Starting Executor Handler...")
            ec2_executor = EC2ApplicationExecutor(self.logger, ec2, instance_id, self.instance_data)
            current_dir = os.getcwd()

            destination_folder = "/home/ubuntu/"

            #sending setup script to the instance
            self.logger.info("Sending setup script to the instance...")
            ec2_executor.send_file_to_instance(os.getcwd()+"/"+"setup.sh",destination_folder)

            #set file permission
            self.logger.info("Setting file permission...")
            command = "chmod 777 setup.sh"
            output, error = ec2_executor.run_command_on_instance(command)

            print("Output:", output)
            print("Error:", error)
            command = "sh setup.sh"
            self.logger.info("Running setup script...")
            output, error = ec2_executor.run_command_on_instance(command)

            print("Output:", output)
            print("Error:", error)
            
            #sending configuration files to the instance
            self.logger.info("Sending configuration files to the instance...")
            ec2_executor.send_file_to_instance(os.getcwd()+"/"+"config/cloud.json",destination_folder)
            ec2_executor.send_file_to_instance(os.getcwd()+"/"+"config/gpu.json",destination_folder)
            ec2_executor.send_file_to_instance(os.getcwd()+"/"+"config/input_data.json",destination_folder)
            ec2_executor.send_file_to_instance(os.getcwd()+"/"+"config/instance.json",destination_folder)

            #Run the second main (mainCLoud)

            command = "python3 framework/services/main_cloud.py"

            # Executando o comando na instância EC2
            output, error = ec2_executor.run_command_on_instance(command)
            # Exibindo a saída e erros (se houver)
            print("Output:", output)
            print("Error:", error)


#logger.info("Creating AWS instance...")
#instance = ec2Manager.create_instance("ami-01afb69abc2756b9e", "g4dn.xlarge",1, "walisson-key", ["walisson-group"])

#print(instance)

#instance_id=instance["InstanceId"]


#logger.info("Conectando ao banco de dados")
#logger.warning("Falha ao conectar ao banco de dados")
#logger.error("Tentativa de login inválida")
#logger.critical("Erro crítico no sistema")
