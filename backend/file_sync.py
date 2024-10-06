# backend/file_sync.py

import os
import threading
import boto3
from botocore.exceptions import ClientError
from backend.config_manager import ConfigManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileSync:
    def __init__(self, progress_callback=None, status_callback=None):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        self.sync_folder = self.config.get('sync_folder')
        self.bucket_name = self.config.get('bucket_name')
        self.region = self.config.get('region')
        self.aws_access_key = self.config.get('aws_access_key')
        self.aws_secret_key = self.config.get('aws_secret_key')
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.sync_thread = None
        self.stop_event = threading.Event()

        # Initialize S3 client with conditional credentials
        self.s3_client = self.initialize_s3_client()

    def initialize_s3_client(self):
        if self.aws_access_key and self.aws_secret_key:
            return boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region
            )
        else:
            return boto3.client(
                's3',
                region_name=self.region
            )

    def sync(self):
        """Perform synchronization with the S3 bucket."""
        logger.info("Starting synchronization process.")
        self.update_status("Starting synchronization...")

        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name)
            total_objects = 0
            for page in pages:
                if 'Contents' in page:
                    total_objects += len(page['Contents'])
            logger.info(f"Total objects in bucket: {total_objects}")

            # Now perform the sync using boto3's upload_file
            for root, dirs, files in os.walk(self.sync_folder):
                for file in files:
                    if self.stop_event.is_set():
                        logger.info("Synchronization stopped by user.")
                        self.update_status("Synchronization stopped.")
                        return
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.sync_folder)
                    s3_key = relative_path.replace("\\", "/")  # For Windows paths
                    try:
                        self.update_status(f"Uploading: {s3_key}")
                        if self.progress_callback:
                            self.progress_callback(1, current_file=s3_key)
                        self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
                        logger.info(f"Uploaded {s3_key} to bucket {self.bucket_name}.")
                    except ClientError as e:
                        logger.error(f"Failed to upload {s3_key}: {e}")
                        # Optionally, you can notify the UI of the error
            # After all uploads, indicate completion
            if self.progress_callback:
                self.progress_callback(0, current_file=None)
            self.update_status("Synchronization completed.")
            logger.info("Synchronization completed successfully.")
        except ClientError as e:
            self.update_status(f"Error during synchronization: {e}")
            logger.error(f"Error during synchronization: {e}")

    def start_sync(self):
        """Start the synchronization in a separate thread."""
        if not self.sync_thread or not self.sync_thread.is_alive():
            self.stop_event.clear()
            self.sync_thread = threading.Thread(target=self.sync, daemon=True)
            self.sync_thread.start()
            logger.info("Synchronization thread started.")
        else:
            logger.info("Synchronization is already running.")

    def stop_sync(self):
        """Stop the synchronization process."""
        self.stop_event.set()
        if self.sync_thread:
            self.sync_thread.join()
            logger.info("Synchronization thread stopped.")

    def update_status(self, message):
        """Update the status in the UI."""
        if self.status_callback:
            self.status_callback(message)
