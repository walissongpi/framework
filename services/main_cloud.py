from services.enviroment import SystemInfo
from services.executor import Executor

import log
import util
from log import Log
import os

class MainCLoud:

    def __init__(self, logger, data):
        self.logger = logger
        self.data = data

    def execute(self):
        #self.logger.info("Executing MASA-CUDALign...")
        executor = Executor(self.logger, self.data)
        executor.execute_path()
        command = executor.create_masa_command()
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
        data = util.openJason("config/input_data.json")

        main = MainCLoud(logger, data)
        main.get_system_info()
        main.execute()
