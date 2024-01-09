#!/usr/bin/env python
# coding: utf-8

# In[4]:


get_ipython().system('pip install boto3')
get_ipython().system('pip install ratelimit')
import requests
import os
import boto3
from botocore.exceptions import NoCredentialsError
from ratelimit import limits, sleep_and_retry

# Your Unsplash access key
access_key = 'CHh4rmov_lygK4hdf2hWHKVw-yD7OxY7Ffp8'

# Your AWS credentials (replace with your actual credentials)
aws_access_key_id = 'AKIARZRONO2KK'
aws_secret_access_key = '6Lba3FCS6vhpt6x7VqsRnRllahrkImYrJ'
aws_region = 'us-east-1'
s3_bucket_name = 'rrr-sourcedump'

# Define the base URL for the Unsplash API
base_url = 'https://api.unsplash.com/search/photos'

# Define the search query
query = 'bokeh street'

# Define the headers with your Unsplash access key
headers = {
    'Authorization': f'Client-ID {access_key}'
}

# Create an S3 client
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

# Limit to 40 requests per hour
@sleep_and_retry
@limits(calls=40, period=3600)  # 40 calls per hour (3600 seconds)
def make_request(page):
    params = {'query': query, 'page': page, 'per_page': 10}
    response = requests.get(base_url, params=params, headers=headers)
    return response

# Create a directory to save the downloaded images
if not os.path.exists(query):
    os.makedirs(query)

# Download and save 50 images (5 pages of 10 images each)
for page in range(1, 6):
    response = make_request(page)

    if response.status_code == 200:
        data = response.json()

        for photo in data['results']:
            image_url = photo['urls']['full']
            image_id = photo['id']
            response = requests.get(image_url)

            if response.status_code == 200:
                # Save the image locally
                local_file_path = os.path.join(query, f'{image_id}.jpg')
                with open(local_file_path, 'wb') as f:
                    f.write(response.content)

                # Upload the image to S3
                s3_key = f"{query}/{image_id}.jpg"
                try:
                    s3.upload_file(local_file_path, s3_bucket_name, s3_key)
                    print(f"Uploaded {image_id}.jpg to S3")
                except NoCredentialsError:
                    print("AWS credentials not available. Upload to S3 failed.")
            else:
                print(f"Failed to download: {image_id}.jpg")
    else:
        print(f"Request failed with status code: {response.status_code}")

