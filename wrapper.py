from boto3 import session

class BotoWrapper:

    def __init__(self, service_name):
        self.session = session(region_name=AWS_REGION)
        self.client = self.session.client(service_name)

    def list_objects(self, bucket_name):
        return self.client.list_objects(Bucket=bucket_name)
