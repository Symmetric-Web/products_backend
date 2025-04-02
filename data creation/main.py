# Standard library imports
import os
from datetime import datetime, timedelta

# Third-party imports
import pandas as pd
from PIL import Image

import cloudinary
import cloudinary.uploader

import json
from datetime import datetime
from pathlib import Path


# Get the current script's directory
CURRENT_DIR = str(Path().absolute())
# Configuration 
#Get api key from https://console.cloudinary.com/console/
cloudinary.config( 
    cloud_name = "", 
    api_key = "", 
    api_secret = "", # Click 'View API Keys' above to copy your API secret
    secure=True
)


AV_COLLECTION = 'Audio-Visual-Products'
BT_COLLECTION = 'Building-Technology-Products'
NP_COLLECTION = 'Networking-Products'

# Base directories
CSV_BASE_DIR = os.path.join(CURRENT_DIR, 'csv_files')
IMAGES_BASE_DIR = os.path.join(CURRENT_DIR, 'product_images')

def upload_image_to_storage(image_path, prefix='images'):
    try:
        new_index = image_path.split("\\")[-2].split('.png')[0][:10] +"_"+ image_path.split("\\")[-1].split('.png')[0]
        upload_result = cloudinary.uploader.upload(f"{image_path}",public_id=f"{prefix}_{new_index}")
        
        print(f"Uploaded image: {upload_result['secure_url']}")
        return upload_result['secure_url']
        
        
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return ''
    

def add_product_to_firestore(product_data, category, subcategory):
    try:
        # Get the full image path
        image_filename = os.path.basename(product_data['image_url'])
        full_image_path = os.path.join(IMAGES_BASE_DIR, category, subcategory, image_filename)
        print(full_image_path)
        
        # Upload image to Cloud Storage with category-based path
        if category == 'Audio-Visual and Automation':
            blob_prefix = 'av-products'
        elif category == 'Building Technologies':
            blob_prefix = 'bt-products'
        else:
            blob_prefix = 'nt-products'
        
        image_url = upload_image_to_storage(full_image_path, blob_prefix) if os.path.exists(full_image_path) else ''
        
        # Prepare document data
        doc_data = {
            'name': product_data['name'],
            'description': product_data['description'],
            'imageUrl': image_url,
            'createdAt': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'priority': 1,
            'type': subcategory,
            'category': category,
            'subcategory': f'{subcategory} Products'
        }

        return doc_data
        
    except Exception as e:
        print(f"Error adding product: {str(e)}")
        return False
    
def process_category(category_name):
    """Process all Excel files in a category"""
    category_dir = os.path.join(CSV_BASE_DIR, category_name)
    print(category_dir)
    if not os.path.exists(category_dir):
        print(f"Category directory not found: {category_dir}")
        return
    
    print(f"\nProcessing category: {category_name}")
    
    # Process each Excel file in the category
    excel_files = [f for f in os.listdir(category_dir) if f.endswith('.xlsx')]
    
    temp_data = []
    for excel_file in excel_files:
        subcategory = os.path.splitext(excel_file)[0]
        print(f"\nProcessing subcategory: {subcategory}")
        
        # Read Excel file
        excel_path = os.path.join(category_dir, excel_file)
        try:
            df = pd.read_excel(excel_path)
            print(f"Found {len(df)} products in {excel_file}")
            
            # Process each product
            success_count = 0
            # image_files = sorted([f for f in os.listdir(os.path.join(IMAGES_BASE_DIR, category_name, subcategory)) if f.endswith('.png')])
            image_files = sorted([f for f in os.listdir(os.path.join(IMAGES_BASE_DIR, category_name, subcategory)) if f.endswith('.png') and not f.startswith('._')])
            image_files = [int(f.split('.png')[0]) for f in image_files]
            image_files.sort()
            print(image_files)
            for index, row in df.iterrows():
                # Get product name
                product_name = row['Name'] if 'Name' in df.columns else row['name']
                
                # Use sequential image file if available
                image_filename = image_files[index] if index < len(image_files) else ''
                
                product_data = {
                    'name': product_name,
                    'description': row['Description'] if 'Description' in df.columns else row['description'],
                    'image_url': str(image_filename)+'.png'
                }
                
                print(f"Processing product {index + 1}/{len(df)}: {product_data['name']} (Image: {product_data['image_url']})")                
                
                temp_data.append(add_product_to_firestore(product_data, category_name, subcategory))
                success_count += 1
                
                
                
            
            
            # temp_data = json.dumps(temp_data)
        
            print(f"\nSuccessfully uploaded {success_count} out of {len(df)} products from {excel_file}")
        except Exception as e:
            print(f"Error processing {excel_file}: {str(e)}")
    
    
    with open(f"json/{category_name}_products.json", "w") as json_file:
            json.dump(temp_data, json_file,indent=4)
        
        

def main():
    # Process Audio-Visual and Automation products
    process_category('Audio Video Control Products')
    
    # Process Building Technologies products
    process_category('Building Technologies')

    # Process Networking Products products
    process_category('Networking Products')
    
    
    print("\nAll categories processed successfully!")
    print(f"Products uploaded to collections: {AV_COLLECTION}, {BT_COLLECTION}, and {NP_COLLECTION}")

if __name__ == "__main__":
    main()