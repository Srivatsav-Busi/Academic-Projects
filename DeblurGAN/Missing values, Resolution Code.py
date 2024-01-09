import boto3
s3_client = boto3.client('s3')

response = s3_client.create_bucket(
    ACL='private',
    Bucket='my-bucket-547487',

)

print(response)

import boto3
import zipfile
import io
import json

# Function code to compare image file names
lambda_code = '''
import json
import boto3

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = 'my-bucket-547487'  
    missing_images = []

    folders = ['Test', 'Train']
    for folder in folders:
        try:
            # List images in 'Blur' and 'Sharp' folders
            blur_response = s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{folder}/Blur/")
            sharp_response = s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{folder}/Sharp/")

            # Extract image file names
            blur_images = set(obj['Key'].split('/')[-1] for obj in blur_response.get('Contents', []))
            sharp_images = set(obj['Key'].split('/')[-1] for obj in sharp_response.get('Contents', []))

            # Compare image file names between 'Blur' and 'Sharp' folders
            missing_in_blur = sharp_images - blur_images
            missing_in_sharp = blur_images - sharp_images

            if missing_in_blur:
                missing_images.extend([f"{folder}/Blur/{img}" for img in missing_in_blur])
            if missing_in_sharp:
                missing_images.extend([f"{folder}/Sharp/{img}" for img in missing_in_sharp])

        except Exception as e:
            missing_images.append(f"Error accessing {folder} folders: {str(e)}")

    if missing_images:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f"Total missing images: {len(missing_images)}, Details: {', '.join(missing_images)}"})
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'All images present'})
        }
'''


# Zip the lambda code
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
    zip_file.writestr('index.py', lambda_code)

# Reset buffer position for reading
zip_buffer.seek(0)

# Create a Lambda client
lambda_client = boto3.client('lambda')

# Create Lambda function
response = lambda_client.create_function(
    FunctionName='CompareImageNames',
    Runtime='python3.8',
    Role='arn:aws:iam::662870958497:role/Lambda',
    Handler='index.lambda_handler',
    Code={
        'ZipFile': zip_buffer.read()
    }
)

print(response)


#####resolution standardization

import boto3
import zipfile
import io

# Function code for image resolution standardization
lambda_code = '''
import json
import cv2
import numpy as np
import boto3

def process_image(path):
    img = cv2.imread(path)
    img = np.asarray(img, dtype="float32")
    img = cv2.resize(img, (128, 128))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img / 255.0
    img = np.reshape(img, (128, 128, 3))
    return img

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = 'my-bucket-547487'  

    try:
        # Retrieve the image file from S3
        image_obj = s3.get_object(Bucket=bucket_name, Key=event['key'])
        image_body = image_obj['Body'].read()

        # Process the image using OpenCV and NumPy
        processed_img = process_image(io.BytesIO(image_body))

        # Convert processed image back to bytes
        processed_bytes = cv2.imencode('.jpg', processed_img)[1].tobytes()

        # Upload the processed image back to S3
        s3.put_object(Bucket=bucket_name, Key=f"processed/{event['key']}", Body=processed_bytes)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': f"Image {event['key']} processed and uploaded"})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
'''

# Zip the lambda code
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
    zip_file.writestr('lambda_function.py', lambda_code)

# Reset buffer position for reading
zip_buffer.seek(0)

# Create a Lambda client
lambda_client = boto3.client('lambda')

# Create Lambda function
response = lambda_client.create_function(
    FunctionName='ResolutionStandardization',
    Runtime='python3.8',
    Role='arn:aws:iam::662870958497:role/ResolutionStandardization',
    Handler='lambda_function.lambda_handler',
    Code={
        'ZipFile': zip_buffer.read()
    }
)

print(response)

