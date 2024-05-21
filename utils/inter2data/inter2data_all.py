import multiprocessing
from mango.inter2data.utils.inter2data import inter2data  
import fire
import glob
import os
import shutil

def run_script(map_path, new_map_path):
    inter2data(map_path, new_map_path)


def main(data_path,new_data_path):

    """
    data_path: og data-intermediate folder e.g. ./data-intermediate/

    new_data_path: new data folder e.g. ./data/ (make sure / is added to the end)

    This script is used to convert the intermediate data to the final data format.
    """
    
    paths=[]
    for file_path in glob.glob(os.path.join(data_path,"**/*.all2all.json"), recursive=True):
        map_path= os.path.join("/".join(file_path.split("/")[:-1]))
        new_map_path= map_path.replace(data_path,new_data_path)
        paths.append((map_path, new_map_path))
    processes = []
    for map_path, new_map_path in paths:
        process = multiprocessing.Process(target=run_script, args=(map_path, new_map_path))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()
    print("All processes have completed.")
    # Define the source and destination directories

    
    # Walk through the source directory
    for root, dirs, files in os.walk(data_path):
        for file in files:
            # Check if the file ends with '.walkthrough'
            if file.endswith('.walkthrough'):
                # Construct the full path to the source file
                src_path = os.path.join(root, file)
                dest_path = src_path.replace(data_path,new_data_path)
                
                # Create the destination directory if it doesn't exist
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Copy the file
                shutil.copy2(src_path, dest_path)
    
    # rename the file
    def add_folder_name_as_prefix(root_dir):
        for folder in next(os.walk(root_dir))[1]:  # List only directories directly under root_dir
            full_folder_path = os.path.join(root_dir, folder)
            prefix = f"{folder}."
    
            for root, dirs, files in os.walk(full_folder_path):
                for file in files:
                    if not file.startswith(prefix):
                        old_file_path = os.path.join(root, file)
                        new_file_path = os.path.join(root, f"{prefix}{file}")
                        os.rename(old_file_path, new_file_path)
                        
                    
    add_folder_name_as_prefix(new_data_path)

    print("All .walkthrough files have been copied.")

if __name__ == "__main__":
    
    fire.Fire(main) 