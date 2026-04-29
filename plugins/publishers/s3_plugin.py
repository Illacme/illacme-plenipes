#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omni-Hub S3 Plugin (Modularized)
🛡️ [V17.0]：从核心库剥离，作为独立插件运行。
"""

import os
import boto3
from botocore.config import Config
from plugins.publishers.base import BasePublisher

class S3Publisher(BasePublisher):
    """🚀 [V17.0] S3 发布插件"""
    PLUGIN_ID = "s3"
    
    def push(self, bundle_path: str, metadata: dict) -> dict:
        bucket = self.config.get("bucket")
        region = self.config.get("region", "us-east-1")
        endpoint = self.config.get("endpoint_url")
        prefix = self.config.get("prefix", "")

        access_key = self.config.get("access_key")
        secret_key = self.config.get("secret_key")

        if not bucket or not access_key or not secret_key:
            return {"status": "skipped", "message": "S3 configuration incomplete"}

        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
                endpoint_url=endpoint,
                config=Config(retries={'max_attempts': 5, 'mode': 'standard'})
            )

            file_count = 0
            for root, dirs, files in os.walk(bundle_path):
                for file in files:
                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, bundle_path)
                    s3_path = os.path.join(prefix, relative_path).replace("\\", "/")
                    
                    content_type = "text/plain"
                    if file.endswith(".html"): content_type = "text/html"
                    elif file.endswith(".json"): content_type = "application/json"
                    elif file.endswith(".webp"): content_type = "image/webp"
                    
                    s3.upload_file(
                        local_path, bucket, s3_path,
                        ExtraArgs={'ContentType': content_type}
                    )
                    file_count += 1

            return {"status": "success", "files": file_count}
        except Exception as e:
            return {"status": "error", "message": str(e)}
