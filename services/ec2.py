import boto3
import time


class EC2Manager:
    def __init__(self, logger, instance_data, cloud_data, gpu_data):
        region_name = cloud_data["region"]
        self.ec2 = boto3.client('ec2', region_name=region_name)
        self.logger = logger
        self.instance_data = instance_data
        self.cloud_data = cloud_data
        self.gpu_data = gpu_data

    def list_instances(self):
        response = self.ec2.describe_instances()
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'InstanceId': instance['InstanceId'],
                    'InstanceType': instance['InstanceType'],
                    'State': instance['State']['Name']
                })
        return instances

    def get_instance_information(self, instance_id):
        response = self.ec2.describe_instances(InstanceIds=[instance_id])
        return response

    def start_instance(self, instance_id):
        self.ec2.start_instances(InstanceIds=[instance_id])
        print(f"Instance {instance_id} started.")

    def stop_instance(self, instance_id):
        self.ec2.stop_instances(InstanceIds=[instance_id])
        print(f"Instance {instance_id} stopped.")

    def terminate_instance(self, instance_id):
        self.ec2.terminate_instances(InstanceIds=[instance_id])
        print(f"Instance {instance_id} terminated.")

    def create_instance(self):
        self.logger.info("Creating On-demand instance...")
        response = self.ec2.run_instances(
            ImageId = self.instance_data["image_id"],
            InstanceType = self.instance_data["instance_type"],
            MinCount = self.instance_data["min_count"],
            MaxCount = self.instance_data["max_count"],
            KeyName = self.instance_data["key_name"],
            SecurityGroups = [self.instance_data["security_group"]],
        )["Instances"][0]

        instance_id=response["InstanceId"]
        self.logger.info("On-demand instance created successfully!")

        self.logger.info("On-demand instance ID:" + instance_id)
        self.logger.info("Starting On-demand instance monitor...")
        self.monitor_instance(instance_id)

        return instance_id, self.ec2

    def monitor_instance(self, instance_id):
        while True:

            response = self.ec2.describe_instance_status(
                InstanceIds=[instance_id]
            )
            if len(response['InstanceStatuses']) > 0:
                self.logger.info("Instance running!")
                #self.logger.info("Instance state: "+response['Reservations'][0]['Instances'][0]['State']['Name'])
                self.logger.info("Instance status: "+response['InstanceStatuses'][0]['InstanceStatus']['Status'])
                if response['InstanceStatuses'][0]['InstanceStatus']['Status'] == "ok":
                    self.logger.info("Instance is ready to use!")
                    break;

            '''response = self.ec2.describe_instances(
                InstanceIds=[instance_id]
            )
            if len(response['Reservations']) > 0:
                if response['Reservations'][0]['Instances'][0]['State']['Name'] == 'running':
                    self.logger.info("Instance running!")'''

            time.sleep(5)

    def monitor_spot_request(self,spot_request_id):
        spot_instance_id = None
        while True:
            response = self.ec2.describe_spot_instance_requests(
                SpotInstanceRequestIds=[spot_request_id]
            )
            request_state = response['SpotInstanceRequests'][0]['State']
            self.logger.info("Spot instance request state: "+request_state);

            if request_state in ['fulfilled', 'failed', 'canceled']:
                break

            if request_state == "active":
                self.logger.info("Spot instance created successfully!");
                spot_instance_id = response['SpotInstanceRequests'][0]['InstanceId']
                #self.logger.info("Spot instance ID: "+spot_instance_id)
                break

            time.sleep(5)
        return spot_instance_id

    def create_spot_instance(self):
        spot_params = {
            'InstanceCount': 1,
            'LaunchSpecification': {
                'ImageId': self.instance_data["image_id"],
                'InstanceType': self.instance_data["instance_type"],
                'KeyName': self.instance_data["key_name"],
                'SecurityGroups': [self.instance_data["security_group"]]
            },
            'SpotPrice': str(self.instance_data["spot_price"]),
            'Type': 'one-time'
        }

        response = self.ec2.request_spot_instances(**spot_params)
        spot_request_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']

        self.logger.info("Spot instance requested!")
        self.logger.info("Monitoring instance...")

        spot_instance_id = self.monitor_spot_request(spot_request_id)

        self.logger.info("Spot request information: ")
        self.logger.info("Spot request id: "+spot_request_id)
        self.logger.info(str(response['SpotInstanceRequests'][0]))

        self.logger.info("Spot instance ID:" + spot_instance_id)
        self.logger.info("Starting spot instance monitor...")
        self.monitor_instance(spot_instance_id)

        return spot_instance_id, self.ec2
