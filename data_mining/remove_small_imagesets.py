import os
import shutil


def _remove_folders_with_few_files(root_dir, min_file_count=5):
    """
    This function removes folders with fewer than min_file_count files in the root_dir.
    :param root_dir: path to the root directory
    :param min_file_count: minimum number of files in a directory
    """
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Get the total number of files in the directory
        num_files = len(filenames)

        # If the directory has fewer files than min_file_count and no subdirectories
        if num_files < min_file_count and not dirnames:
            # Remove all files in the directory
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                os.remove(file_path)
                print(f"Removed file: {file_path}")

            # Remove the now empty directory
            os.rmdir(dirpath)
            print(f"Removed folder with fewer than {min_file_count} files: {dirpath}")

def remove_folders_with_few_files():
    """
    A wrapper function to remove folders with fewer than 5 files in the sentinel_images and sentinel_images_no_fire directories.
    :return:
    """
    root_directory = r"/sentinel_images"
    _remove_folders_with_few_files(root_directory)
    root_directory = r"/sentinel_images_no_fire"
    _remove_folders_with_few_files(root_directory)
    print("Folders with fewer than 5 files removal complete.")

if __name__ == "__main__":
    remove_folders_with_few_files()