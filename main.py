from services.enviroment import SystemInfo
from services.executor import Executor
from services.local import LocalEnviroment
from services.cloud import CloudEnviroment

import log
import util
from log import Log
import os

options = {
    "1": "Local module",
    "2": "Cloud module",
    "3": "Exit",
}

def show_menu():
    #os.system('clear') or None
    print("\n--------------------------------------------------------------------------------\n")
    print("Welcome to the Adaptive Framework! \n")
    print("This software aims to facilitate the biological sequence alignment process on local or cloud enviroment. It runs over MASA-CUDAling and automatically choose the required parameters to do such process. Enjoy it!")
    print("\n--------------------------------------------------------------------------------\n")

    for id, description in options.items():
        print(f"{id}. {description}")
    print()

    choice = input("Enter your option: ")

    return choice

def execute_action(choice, logger):
    if choice in options:
        if choice == "1":
            logger.info("Starting local module...")
            data = util.openJason("config/input_data.json")
            gpu_data = util.openJason("config/gpu.json")
            local_enviroment = LocalEnviroment(logger, data, gpu_data)
            local_enviroment.start()

        elif choice == "2":
            logger.info("Starting cloud module...")
            cloud_data = util.openJason("config/cloud.json")
            instance_data = util.openJason("config/instance.json")
            data = util.openJason("config/input_data.json")
            gpu_data = util.openJason("config/gpu.json")
            cloud_enviroment = CloudEnviroment(logger, data, instance_data, cloud_data, gpu_data)
            cloud_enviroment.start()
            print("Press ENTER to cotinue...")
        elif choice == "3":
            exit()
        else:
            print("Wrong option.")
    else:
        print("Unknown option.")

logger = Log("Adaptative Framework log file")
logger.debug("Starting the framework...")

while True:
    choice = show_menu()
    if choice.lower() == "exit":
        break
    execute_action(choice, logger)
