#!/usr/bin/env python3
"""
Check S3/MinIO storage status
"""

import os
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

# S3 configuration from environment
s3_config = {
    'endpoint_url': os.getenv('S3_ENDPOINT_URL', 'http://135.181.106.12:9000'),
    'aws_access_key_id': os.getenv('S3_ACCESS_KEY_ID', 'minioadmin'),
    'aws_secret_access_key': os.getenv('S3_SECRET_ACCESS_KEY', 'minioadmin'),
    'bucket_name': os.getenv('S3_BUCKET_NAME', 'morphik-storage')
}

def check_s3_storage():
    """Check S3/MinIO storage for files."""
    
    print("=" * 60)
    print("🗄️  S3/MinIO STORAGE CHECK")
    print(f"📍 Endpoint: {s3_config['endpoint_url']}")
    print(f"🪣 Bucket: {s3_config['bucket_name']}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Create S3 client
        s3 = boto3.client(
            's3',
            endpoint_url=s3_config['endpoint_url'],
            aws_access_key_id=s3_config['aws_access_key_id'],
            aws_secret_access_key=s3_config['aws_secret_access_key'],
            verify=False
        )
        
        # Check if bucket exists
        try:
            s3.head_bucket(Bucket=s3_config['bucket_name'])
            print(f"\n✅ Bucket '{s3_config['bucket_name']}' exists\n")
        except ClientError:
            print(f"\n❌ Bucket '{s3_config['bucket_name']}' does not exist\n")
            return False
        
        # List objects in bucket
        response = s3.list_objects_v2(
            Bucket=s3_config['bucket_name'],
            MaxKeys=100
        )
        
        if 'Contents' in response:
            objects = response['Contents']
            print(f"📂 Found {len(objects)} objects in storage:\n")
            
            total_size = 0
            for obj in objects[:10]:  # Show first 10
                size_mb = obj['Size'] / (1024 * 1024)
                total_size += obj['Size']
                print(f"  📄 {obj['Key']:50} ({size_mb:.2f} MB)")
                print(f"     Modified: {obj['LastModified']}")
            
            if len(objects) > 10:
                print(f"\n  ... and {len(objects) - 10} more files")
            
            total_size_mb = total_size / (1024 * 1024)
            print(f"\n📊 Total storage used: {total_size_mb:.2f} MB")
            
            return len(objects) > 0
        else:
            print("✅ Storage is EMPTY - no files found\n")
            return False
            
    except Exception as e:
        print(f"\n❌ Error connecting to S3/MinIO: {e}")
        return False

def clean_s3_storage():
    """Remove all objects from S3 storage."""
    
    print("\n🧹 CLEANING S3 STORAGE...\n")
    
    try:
        s3 = boto3.client(
            's3',
            endpoint_url=s3_config['endpoint_url'],
            aws_access_key_id=s3_config['aws_access_key_id'],
            aws_secret_access_key=s3_config['aws_secret_access_key'],
            verify=False
        )
        
        # List all objects
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=s3_config['bucket_name'])
        
        delete_keys = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    delete_keys.append({'Key': obj['Key']})
        
        if delete_keys:
            # Delete in batches of 1000 (S3 limit)
            for i in range(0, len(delete_keys), 1000):
                batch = delete_keys[i:i+1000]
                s3.delete_objects(
                    Bucket=s3_config['bucket_name'],
                    Delete={'Objects': batch}
                )
                print(f"  ✅ Deleted {len(batch)} objects")
            
            print(f"\n✅ Total deleted: {len(delete_keys)} objects")
        else:
            print("  ℹ️  No objects to delete")
            
    except Exception as e:
        print(f"❌ Error cleaning storage: {e}")

def main():
    has_files = check_s3_storage()
    
    if has_files:
        print("\n" + "=" * 60)
        print("⚠️  FILES FOUND IN S3 STORAGE")
        print("=" * 60)
        
        response = input("\nDo you want to clean S3 storage? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            clean_s3_storage()
            print("\n" + "=" * 60)
            print("✅ S3 STORAGE IS NOW CLEAN")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✅ S3 STORAGE IS ALREADY CLEAN")
        print("=" * 60)

if __name__ == "__main__":
    main()