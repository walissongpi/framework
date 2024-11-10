import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from services.enviroment import SystemInfo

class DecisionMaker:
    def __init__(self, logger, data, gpu_data, sequence_similarity):
        self.logger = logger
        analyser = SystemInfo()
        self.cpu_data = analyser.get_system_info()
        self.data = data
        self.gpu_data = gpu_data
        self.sequence_similarity = sequence_similarity

    def calculate_gpu_grade(self):
        # Input variables
        memory_bandwidth = ctrl.Antecedent(np.arange(0, 400, 1), 'memory_bandwidth')  # GB/s
        computional_power = ctrl.Antecedent(np.arange(0, 800, 1), 'computional_power')
        # Output variable
        classification = ctrl.Consequent(np.arange(0, 11, 1), 'classification')

        # Membership functions for memory bandwidth
        memory_bandwidth['low'] = fuzz.trapmf(memory_bandwidth.universe, [0, 0, 60, 100])
        memory_bandwidth['medium'] = fuzz.trapmf(memory_bandwidth.universe, [80, 100, 180, 290])
        memory_bandwidth['high'] = fuzz.trapmf(memory_bandwidth.universe, [220, 300, 400, 400])

        # Membership functions for CUDA Cores amount
        computional_power['low'] = fuzz.trapmf(computional_power.universe, [0,0, 90, 130])
        computional_power['medium'] = fuzz.trapmf(computional_power.universe, [110, 150, 350, 450])
        computional_power['high'] = fuzz.trapmf(computional_power.universe, [390, 430, 800, 800])

        # Membership functions for classification
        classification['low'] = fuzz.trapmf(classification.universe, [0, 0, 2, 4])
        classification['medium'] = fuzz.trapmf(classification.universe, [3, 4, 5, 6])
        classification['high'] = fuzz.trapmf(classification.universe, [5, 7, 10, 10])

        #memory_bandwidth.view()
        #computional_power.view()
        # Rules
        rule1 = ctrl.Rule((memory_bandwidth['low'] | memory_bandwidth['medium']) &
                          (computional_power['low']), classification['low'])

        rule2 = ctrl.Rule((memory_bandwidth['medium'] | memory_bandwidth['high']) &
                          (computional_power['low']), classification['low'])

        rule3 = ctrl.Rule((memory_bandwidth['medium'] | memory_bandwidth['high']) &
                          (computional_power['medium']), classification['medium'])

        rule4 = ctrl.Rule( memory_bandwidth['high'] & (computional_power['high']), classification['high'])
        # Control system
        classification_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4])
        classification_simulator = ctrl.ControlSystemSimulation(classification_ctrl)

        power = (int(self.gpu_data["cores"]) * int(self.gpu_data["boost_clock"]))/10000
        classification_simulator.input['memory_bandwidth'] = int(self.gpu_data["memory_bandwidth"])
        classification_simulator.input['computional_power'] = int(power)

        # Compute the result
        classification_simulator.compute()

        # Print the result
        grade = classification_simulator.output['classification']
        print("MX-150: ", grade)
        #classification.view(sim=classification_simulator)

        return grade

    def decide_strategy_stage4(self):
            # Defining input variables
        sequence_size = ctrl.Antecedent(np.arange(1, 101, 0.001), 'Sequence_Size')
            #sequence_similarity
        similarity = ctrl.Antecedent(np.arange(1, 101, 0.1), 'Sequence_Similarity')
        cpu_cores = ctrl.Antecedent(np.arange(1, 17, 1), 'CPU_Cores')
        cpu_freq = ctrl.Antecedent(np.arange(1, 5, 0.1), 'CPU_Frequency')
        gpu = ctrl.Antecedent(np.arange(1, 11, 0.1), 'GPU')
        ram_memory = ctrl.Antecedent(np.arange(1, 65, 1), 'RAM_Memory')
            #output variable
        execution_device = ctrl.Consequent(np.arange(0, 11, 1), 'Execution_Device')
            #membership functions for each variable (Million)
        sequence_size['small'] = fuzz.trapmf(sequence_size.universe, [0.001,1, 3, 10])
        sequence_size['medium'] = fuzz.trapmf(sequence_size.universe, [3, 8,12, 23])
        sequence_size['large'] = fuzz.trapmf(sequence_size.universe, [10,23, 50, 60])
        sequence_size['huge'] = fuzz.trapmf(sequence_size.universe, [50,60, 100, 100])

        similarity['low'] = fuzz.trapmf(similarity.universe, [0,0, 20,30])
        similarity['medium'] = fuzz.trapmf(similarity.universe, [25, 40, 50, 70])
        similarity['high'] = fuzz.trapmf(similarity.universe, [60, 70, 100, 100])

        cpu_cores['few'] = fuzz.trapmf(cpu_cores.universe, [1, 1, 2, 4])
        cpu_cores['some'] = fuzz.trapmf(cpu_cores.universe, [2,4 ,8, 12])
        cpu_cores['many'] = fuzz.trapmf(cpu_cores.universe, [8, 12,16, 16])

        cpu_freq['low'] = fuzz.trimf(cpu_freq.universe, [1, 1, 2])
        cpu_freq['medium'] = fuzz.trimf(cpu_freq.universe, [1.5, 2, 3])
        cpu_freq['high'] = fuzz.trimf(cpu_freq.universe, [2.5, 4, 4])

        ram_memory['low'] = fuzz.trapmf(ram_memory.universe, [1, 1,4, 8])
        ram_memory['medium'] = fuzz.trapmf(ram_memory.universe, [4,8, 16, 24])
        ram_memory['high'] = fuzz.trapmf(ram_memory.universe, [16,32, 64, 64])

        gpu['low'] = fuzz.trapmf(gpu.universe, [0, 0, 2.5, 3])
        gpu['medium'] = fuzz.trapmf(gpu.universe, [2.5, 3, 5, 6])
        gpu['high'] = fuzz.trapmf(gpu.universe, [5.5, 6, 10,10])

            # membership function visualization
        #sequence_size.view()
        #cpu_cores.view()
        #cpu_freq.view()
        #ram_memory.view()
        #gpu.view()
        #similarity.view()

        execution_device['CPU'] = fuzz.trimf(execution_device.universe, [0, 0, 5])
        execution_device['GPU'] = fuzz.trimf(execution_device.universe, [4, 10, 10])

            # Defining fuzzy rules
        rule1 = ctrl.Rule(sequence_size['small'] & cpu_cores['few'] & cpu_freq['low'] & ram_memory['low'] & (gpu['low'] | gpu['medium'] | gpu['high']) & similarity['high'], execution_device['GPU'])
        rule2 = ctrl.Rule(sequence_size['small'] & cpu_cores['few'] & cpu_freq['low'] & ram_memory['low'] & (gpu['low'] | gpu['medium'] | gpu['high']) & (similarity['low'] | similarity['medium']), execution_device['CPU'])
        rule3 = ctrl.Rule(sequence_size['medium'] & cpu_cores['some'] & cpu_freq['medium'] & ram_memory['medium'] & gpu['medium'] & (similarity['medium'] | similarity['high']), execution_device['GPU'])
        rule4 = ctrl.Rule(sequence_size['medium'] & cpu_cores['some'] & cpu_freq['medium'] & ram_memory['medium'] & gpu['medium'], execution_device['GPU'])
        rule5 = ctrl.Rule((sequence_size['large'] | sequence_size['huge']) & (gpu['high'] | gpu['medium']) & (similarity['medium'] | similarity['high']) , execution_device['GPU'])
        rule6 = ctrl.Rule((sequence_size['large'] | sequence_size['huge']) & (gpu['low'] | gpu['medium']) & (similarity['low'] | similarity['medium']) , execution_device['GPU']) #alterar aqui
        rule7 = ctrl.Rule(sequence_size['small'] & (similarity['low']  | similarity['medium'] | similarity['high']) , execution_device['CPU'])
            # Creating the control system
        device_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7])
        execution_sys = ctrl.ControlSystemSimulation(device_ctrl)
            # Setting input values
        execution_sys.input['Sequence_Size'] = float(self.data["seq1_length"])/(1024*1024*1024)
        execution_sys.input['CPU_Cores'] = int(self.cpu_data["Fisical Cores"])
        execution_sys.input['CPU_Frequency'] = float(self.cpu_data["Clock"])
        execution_sys.input['RAM_Memory'] = int(self.cpu_data["Total Memory"])
        execution_sys.input['GPU'] = round(self.calculate_gpu_grade(),1)
        execution_sys.input['Sequence_Similarity'] = self.sequence_similarity

            # Computing the result
        execution_sys.compute()

            # Getting the result
        result =  execution_sys.output['Execution_Device']
        print("Execution Device:", result)
        #execution_device.view(sim=execution_sys)

        #strategy = "ORIGINAL_MM"  #mudei aqui para testes
        strategy = "MM_GPU"
        if result >= 5:
            strategy = "MM_GPU"

        return strategy
