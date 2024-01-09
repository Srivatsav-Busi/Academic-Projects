import os
import cv2
import numpy as np

def process_images(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get the list of subfolders (Test and Train) in the input folder (S3)
    subfolders = [f.path for f in os.scandir(input_folder) if f.is_dir()]

    for subfolder in subfolders:
        # Get the folder name (Test or Train) without the path
        base_folder_name = os.path.basename(subfolder)

        # Create a new folder with a prefix (resized_)
        new_subfolder = os.path.join(output_folder, f"resized_{base_folder_name}")
        os.makedirs(new_subfolder, exist_ok=True)

        # Get the list of sub-subfolders (blur and sharp) in each subfolder (Test or Train)
        subsubfolders = [f.path for f in os.scandir(subfolder) if f.is_dir()]

        for subsubfolder in subsubfolders:
            # Get the sub-subfolder name (blur or sharp) without the path
            subsubfolder_name = os.path.basename(subsubfolder)

            # Create a new sub-subfolder with a prefix (resized_)
            new_subsubfolder = os.path.join(new_subfolder, f"resized_{subsubfolder_name}")
            os.makedirs(new_subsubfolder, exist_ok=True)

            # Get a list of all files in the current sub-subfolder
            image_files = [f for f in os.listdir(subsubfolder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

            for image_file in image_files:
                # Read the image
                image_path = os.path.join(subsubfolder, image_file)
                img = cv2.imread(image_path)

                # Check if the image is successfully loaded
                if img is not None:
                    # Resize the image to 128x128 pixels
                    img = cv2.resize(img, (128, 128))

                    # Convert BGR to RGB
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                    # Normalize pixel values to be between 0 and 1
                    img = img / 255.0

                    # Save the resized image to the new sub-subfolder
                    output_path = os.path.join(new_subsubfolder, f"resized_{image_file}")
                    cv2.imwrite(output_path, cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))

                    print(f"Resized and saved: {output_path}")

if __name__ == "__main__":
    # Replace 'input_folder' with the path to the S3 folder
    input_folder = input("Enter the path to the S3 folder:/Users/srivatsavbusi/S3 ")

    # Replace 'output_folder' with the path where you want to save the resized images
    output_folder = input("Enter the path to the output folder: /Users/srivatsavbusi/ResizedS3")

    process_images(input_folder, output_folder)
