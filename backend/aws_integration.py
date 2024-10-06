# backend/aws_integration.py

import boto3
from botocore.exceptions import ClientError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AWSIntegration:
    def __init__(self, access_key=None, secret_key=None, region='us-east-2'):
        self.region = region
        if access_key and secret_key:
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
        else:
            # Use default credentials (e.g., IAM roles)
            self.s3 = boto3.client('s3', region_name=region)
    
    def get_existing_buckets(self):
        try:
            response = self.s3.list_buckets()
            buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
            logger.info(f"Retrieved buckets: {buckets}")
            return buckets
        except ClientError as e:
            logger.error(f"Error listing buckets: {e}")
            return []
    
    def create_s3_bucket(self, bucket_name):
        try:
            # Validate bucket name
            if not self.validate_bucket_name(bucket_name):
                logger.error(f"Invalid bucket name: {bucket_name}")
                return False
    
            # Check if bucket already exists
            existing_buckets = self.get_existing_buckets()
            if bucket_name in existing_buckets:
                logger.error(f"Bucket '{bucket_name}' already exists.")
                return False
    
            # Create bucket
            if self.region == 'us-east-1':
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                location = {'LocationConstraint': self.region}
                self.s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
            logger.info(f"Bucket '{bucket_name}' created successfully.")
            return True
        except ClientError as e:
            logger.error(f"Failed to create bucket '{bucket_name}': {e}")
            return False
    
    def generate_presigned_url(self, bucket_name, object_key, expiration=3600):
        try:
            url = self.s3.generate_presigned_url('get_object',
                                                 Params={'Bucket': bucket_name, 'Key': object_key},
                                                 ExpiresIn=expiration)
            logger.info(f"Generated presigned URL for {object_key}: {url}")
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL for {object_key}: {e}")
            return None
    
    def validate_bucket_name(self, bucket_name):
        """Validate the S3 bucket name according to AWS guidelines."""
        import re
        pattern = re.compile(r'^[a-z0-9.-]{3,63}$')
        if not pattern.match(bucket_name):
            return False
        if '..' in bucket_name or '.-' in bucket_name or '-.' in bucket_name:
            return False
        if not re.match(r'^[a-z0-9]', bucket_name) or not re.match(r'[a-z0-9]$', bucket_name):
            return False
        return True
