from framework.wrapper import BotoWrapper

class S3:

    def __init__(self):
        self.boto3 = BotoWrapper("s3")

    def list_buckets(self):
        return self.boto3.client.list_buckets()

    def upload_file(self, bucket_name, file_name, file_path):
        return self.boto3.client.upload_file(Bucket=bucket_name, Key=file_name, Filename=file_path)
