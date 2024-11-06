from services.enviroment import SystemInfo
from services.executor2 import Executor2
from services.ec2 import EC2Manager
from services.ec2executor import EC2ApplicationExecutor
import math
import os
from pathlib import Path

class CloudEnviroment2:

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
        BW = int(self.gpu_data["memory_bandwidth"])
        BP = 0
        result = -3.036 + (0.979 * math.log10(m * n)) - (0.344 * math.log10(CP)) - (1.001 * math.log10(BW)) + (0.777* math.log10(1 - BP))
        #print(resp)
        minutes = (math.pow(10,result)/60000)*.9
        return minutes

    def replace_instance(self, ec2):
        try:
            #ec2_client = boto3.client('ec2')
            new_instance_type = self.instance_data["new_instance_type"]
            self.logger.info("Trying to replacing...")
            self.ec2.stop_instances(InstanceIds=[self.instance_id])
            print(f'Instance {self.instance_id} is being interruped...')

            waiter = self.ec2.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=[self.instance_id])
            print(f'Instance {self.instance_id} Stopped.')

            self.ec2.modify_instance_attribute(InstanceId=self.instance_id, Attribute='instanceType', Value=new_instance_type)
            print(f'Instance changed to {new_instance_type}.')
            self.ec2.start_instances(InstanceIds=[self.instance_id])
            print(f'Instance {self.instance_id} is being started...')

            waiter = self.ec2.get_waiter('instance_running')
            waiter.wait(InstanceIds=[self.instance_id])
            print(f'Instance {self.instance_id} is running.')

        except Exception as e:
            print(f'Error when replacing instance: {e}')

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

            spot_price = ec2Manager.get_spot_price()
            if spot_price:
                msg = "The current spot price for "+self.instance_data["instance_type"]+ " in " + self.cloud_data["region"]+" region is $" + spot_price
                self.logger.info(msg)
            else:
                msg = "Unable to find out the spot price for "+self.instance_data["instance_type"]+" in "+self.cloud_data["region"] +" region"
                self.logger.info(msg)

            instance_id, ec2 = ec2Manager.create_spot_instance()
            input("Press ENTER to continue execution...")
        else:
            if self.cloud_data["auto_spot_selection"] != "yes":
                self.logger.info("Automatic Spot Instance selection is disabled. The execution will be carried out in an on-demand instance.")
            else:
                self.logger.info("The expected time for sequence alignment ("+minutes+" minutes) is greater than the pre-established threshold ("+self.cloud_data["market_threshold"]+" minutes). The execution will be carried out on an On-demand instance...")

            self.logger.info("Creating "+ self.instance_data["instance_type"]+" On-demand instance...")

            price = ec2Manager.get_instance_price()
            if price:
                msg = "The current on-demand price for "+self.instance_data["instance_type"]+ " in " + self.cloud_data["region"]+" region is $" + price +" per hour"
                self.logger.info(msg)
            else:
                msg = "Unable to find out the on-demand price for "+self.instance_data["instance_type"]+" in "+self.cloud_data["region"] +" region"
                self.logger.info(msg)

            instance_id, ec2 = ec2Manager.create_instance()
            input("Press ENTER to continue execution...")

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
            ec2_executor.send_file_to_instance(os.getcwd()+"/"+"prepare.sh",destination_folder)

            #set file permission
            self.logger.info("Setting up file permission...")
            command = "chmod +x prepare.sh"
            output, error = ec2_executor.run_command_on_instance(command)

            print("Output:", output)
            print("Error:", error)
            command = "sh prepare.sh "+self.gpu_data["arch"]
            self.logger.info("Running setup script...")
            output, error = ec2_executor.run_command_on_instance(command)

            print("Output:", output)
            print("Error:", error)

            destination_folder = "/home/ubuntu/framework/config"
            #sending configuration files to the instance
            self.logger.info("Sending configuration files to the instance...")
            ec2_executor.send_file_to_instance(os.getcwd()+"/"+"config/cloud.json",destination_folder)
            ec2_executor.send_file_to_instance(os.getcwd()+"/"+"config/gpu.json",destination_folder)
            ec2_executor.send_file_to_instance(os.getcwd()+"/"+"config/input_data.json",destination_folder)
            ec2_executor.send_file_to_instance(os.getcwd()+"/"+"config/instance.json",destination_folder)

            destination_folder = "/home/ubuntu/framework"
            self.logger.info("Sending execution script file to the instance...")
            ec2_executor.send_file_to_instance(os.getcwd()+"/"+"execute.sh",destination_folder)
            self.logger.info("Setting up file permission...")
            command = "chmod +x framework/execute.sh"
            output, error = ec2_executor.run_command_on_instance(command)
            # Exibindo a saída e erros (se houver)
            print("Output:", output)
            print("Error:", error)

            self.logger.info("Running executor cloud module...")
            command = "python3 "+destination_folder+"/main_cloud2.py"

            output, error = ec2_executor.run_command_on_instance(command)

            #interromper a instância neste ponto e reiniciar a execução
            self.logger.info("Passou aqui...")
            self.logger.info("Trying to replacing instance...")

            self.replace_instance(ec2)

            print("Output:", output)
            print("Error:", error)
