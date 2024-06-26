import os
import shutil


def remove_folders_with_few_files(root_dir, min_file_count=5):
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


if __name__ == "__main__":
    root_directory = r"\sentinel_images"
    # root_directory = r"\sentinel_images_no_fire"
    remove_folders_with_few_files(root_directory)
    print("Folders with fewer than 5 files removal complete.")
