import platform
import psutil
import GPUtil
import subprocess
#import pycuda.driver as cuda
cuda.init()

class SystemInfo:
    def __init__(self):
        self.system_info = {}

    def get_os_info(self):
        self.system_info['Operacional System'] = platform.platform()

    def get_cpu_info(self):
        self.system_info['Processor'] = platform.processor()
        self.system_info['Architecture'] = platform.architecture()[0]
        self.system_info['Clock'] = psutil.cpu_freq().current
        self.system_info['Fisical Cores'] = psutil.cpu_count(logical=False)
        self.system_info['Logical Cores'] = psutil.cpu_count(logical=True)

    def get_memory_info(self):
        memory_info = psutil.virtual_memory()
        self.system_info['Total Memory'] = memory_info.total
        self.system_info['Available Memory'] = memory_info.available

    def get_disk_info(self):
        disk_info = psutil.disk_usage('/')
        self.system_info['Total Storage'] = disk_info.total
        self.system_info['Available Storage'] = disk_info.free

    def get_gpu_clock(self):
        try:
            output = subprocess.check_output(['nvidia-smi', '--query-gpu=clocks.gr', '--format=csv,noheader,nounits'])
            gpu_clock = int(output.strip())
            return gpu_clock
        except Exception as e:
            print(f"Erro ao obter o clock da GPU: {e}")
            return None

    '''def get_total_frequency(self):
        try:
            # Obter o primeiro dispositivo CUDA
            device = cuda.Device(0)
            properties = device.get_attributes()

            # Verificar se a informação sobre a frequência total está disponível
            if cuda.device_attribute.MAX_CLOCK_RATE in properties:
                max_clock_rate = properties[cuda.device_attribute.MAX_CLOCK_RATE] / 1000  # Convertendo para MHz
                return max_clock_rate
            else:
                return None
        except Exception as e:
            print(f"Erro ao obter a frequência total da GPU: {e}")
            return None'''

    '''def get_cuda_cores(self):
        try:
            # Obter o primeiro dispositivo CUDA
            device = cuda.Device(0)
            properties = device.get_attributes()

            # Verificar se a informação sobre CUDA Cores está disponível
            #if cuda.device_attribute.MULTIPROCESSOR_COUNT in properties and cuda.device_attribute.CUDA_CORE_COUNT in properties:
            #    multiprocessor_count = properties[cuda.device_attribute.MULTIPROCESSOR_COUNT]
            #    cuda_cores_per_mp = properties[cuda.device_attribute.CUDA_CORE_COUNT]
            #    cuda_cores = multiprocessor_count * cuda_cores_per_mp
            #    return cuda_cores
            #else:
            return None
        except Exception as e:
            print(f"Erro ao obter a quantidade de CUDA Cores da GPU: {e}")
            return None'''

    '''def get_clock_all(self):

        device = cuda.Device(0)
        properties = device.get_attributes()

        # Verificar se as informações sobre base clock e boost clock estão disponíveis
        if cuda.device_attribute.MAX_CLOCK_RATE in properties and cuda.device_attribute.BASE_CLOCK_RATE in properties:
            max_clock_rate = properties[cuda.device_attribute.MAX_CLOCK_RATE] / 1000  # Convertendo para MHz
            base_clock_rate = properties[cuda.device_attribute.BASE_CLOCK_RATE] / 1000  # Convertendo para MHz
            print(f"Base Clock da GPU: {base_clock_rate} MHz")
            print(f"Boost Clock da GPU: {max_clock_rate} MHz")
        else:
            print("As informações sobre base clock e boost clock não estão disponíveis para este dispositivo.")'''

    def get_gpu_info(self):
        try:
            gpus = GPUtil.getGPUs()
            gpu_info = []
            for gpu in gpus:
                gpu_info.append({
                    'Nome': gpu.name,
                    'VRAM Total': gpu.memoryTotal,
                    'VRAM Usada': gpu.memoryUsed,
                    'VRAM Livre': gpu.memoryFree,
                    'Clock': self.get_gpu_clock(),
                    'Porcentagem de Uso': gpu.load * 100,
                    'Cuda Cores': self.get_cuda_cores(),
                    'Total Clock': self.get_clock_all()
                })
            self.system_info['Placas de Vídeo'] = gpu_info
        except Exception as e:
            self.system_info['Placas de Vídeo'] = "Erro ao obter informações da placa de vídeo: " + str(e)

    def get_system_info(self):
        self.get_os_info()
        self.get_cpu_info()
        self.get_memory_info()
        self.get_disk_info()
        self.get_gpu_info()
        return self.system_info
