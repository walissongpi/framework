from services.enviroment import SystemInfo
from services.executor2 import Executor2

import log
import util
from log import Log
import os
import time

class MainCLoud2:

    def __init__(self, logger, data, gpu_data):
        self.logger = logger
        self.data = data
        self.gpu_data = gpu_data

    def execute(self):
        #self.logger.info("Executing MASA-CUDALign...")
        executor = Executor2(self.logger, self.data, self.gpu_data)
        executor.execute_path()
        command = executor.create_masa_command()

        #self.logger.info("Trying to replace the instance for a new one...")
        #executor.replace_instance()
        #response = executor.execute(command,1)


    def get_system_info (self):
        #self.logger.info("Getting enviroment information...")

        system_info = SystemInfo().get_system_info()
        self.logger.info("Enviroment information: ")
        for key, value in system_info.items():
            self.logger.info(key + ': '+ str(value))

if __name__ == "__main__":
    logger = Log("Adaptative Framework log file cloud module")
    logger.info("Starting the cloud execution...")
    data = util.openJason(os.getcwd()+"/framework/config/input_data.json")
    gpu_data = util.openJason(os.getcwd()+"/framework/config/gpu.json")

    main = MainCLoud2(logger, data, gpu_data)
    main.get_system_info()
    #medir o tempo aqui

    start = time.time()

    main.execute()

    end = time.time()
    execution_time = end - start
    logger.info("alignment time: "+str(round(execution_time))+" seconds")
    #self.logger.info("Estimated monetary cost: "+ "US$")
