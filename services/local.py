from services.enviroment import SystemInfo
from services.executor import Executor

class LocalEnviroment:

    def __init__(self, logger, data, gpu_data):
        self.logger = logger
        self.data = data
        self.gpu_data = gpu_data

    def execute(self):
        self.logger.info("Executing MASA-CUDALign...")
        executor = Executor(self.logger, self.data, self.gpu_data)
        executor.execute_path()
        command = executor.create_masa_command()
        #response = executor.execute(command,1)

    def get_system_info (self):
        self.logger.info("Getting enviroment information...")

        system_info = SystemInfo().get_system_info()
        self.logger.info("Enviroment information: ")
        for key, value in system_info.items():
            self.logger.info(key + ': '+ str(value))

        self.logger.info("System information collected.")

    def start(self):
        self.get_system_info()
        self.execute()
