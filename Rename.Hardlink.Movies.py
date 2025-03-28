import os
import re
import pathlib
from tkinter import Tk, filedialog

# Function to extract the movie name and year from the filename
def extract_name_and_year(filename):
    # Step 1: Put file name in a temporary variable and remove all dots and parentheses
    temp_filename = filename.replace('.', ' ').replace('(', '').replace(')', '')
    
    # Step 2: Look for a 4-digit number between 1920 and 2030 as the year
    year_pattern = r'(\d{4})'  # Pattern to match any 4-digit number
    year_match = re.search(year_pattern, temp_filename)
    
    if year_match:
        year = year_match.group(1)

        # Ensure the year is valid (between 1920 and 2030)
        if 1920 <= int(year) <= 2030:
            # Step 3: Extract the name (remove the year part)
            name = temp_filename.split(year)[0].strip()

            # Return the extracted name and year
            return name.strip(), year
    
    # If no valid year was found, return None
    return None, None

# Function to determine the source (REMUX, WEB-DL, etc.) and quality
def extract_source_and_quality(filename):
    sources = ['REMUX', 'WEB-DL', 'Webrip', 'BluRay', 'DVD']
    qualities = ['480p', '720p', '1080p', '4K']
    source = None
    quality = None

    # Check for qualities first (e.g., 1080p, 720p, etc.)
    for qual in qualities:
        if qual in filename:
            quality = qual
            break

    # Now check for REMUX and other sources (if not already found)
    if 'REMUX' in filename.upper():
        source = 'Remux'
    else:
        for src in sources:
            if src.lower() in filename.lower():
                source = src
                break
    
    # Default source is BluRay if none was found
    if not source:
        source = 'BluRay'
    
    return source, quality

# Function to process the files in folder 1 and extract necessary data
def process_files_in_folder(folder_path):
    file_data = []
    skipped_files = []  # To store files that are already properly named

    for root, dirs, files in os.walk(folder_path):
        # Only process .mkv or .mp4 files
        video_files = [f for f in files if f.endswith('.mkv') or f.endswith('.mp4')]

        if root == folder_path:
            # In the root folder, process all video files
            for video in video_files:
                file_path = os.path.join(root, video)
                name, year = extract_name_and_year(video)
                
                print(f"Processing file: {video}")
                print(f"Extracted Name: {name}, Extracted Year: {year}")

                if name is None or year is None:
                    print(f"Skipping file (unable to extract name/year): {file_path}")
                    skipped_files.append(file_path)
                    continue
                
                source, quality = extract_source_and_quality(video)
                
                # Step 4: Folder name format: Name (Year)
                folder_name = f"{name} ({year})"
                
                # Step 5: File name format (including source and quality): Name (Year) - Source-Quality
                if quality and source:
                    hardlink_name = f"{name} ({year}) {source}-{quality}"
                elif quality:
                    hardlink_name = f"{name} ({year}) {quality}"
                elif source:
                    hardlink_name = f"{name} ({year}) {source}"
                else:
                    hardlink_name = f"{name} ({year})"  # If neither source nor quality is found

                # If the file is already properly named, skip it and log it
                if name and year and f"{name} ({year})" in video and (source and source in video or quality and quality in video):
                    skipped_files.append(file_path)
                    continue

                file_data.append([file_path, folder_name, hardlink_name])

        else:
            # Process subfolders: Find and process the largest file only
            largest_file = None
            largest_size = 0
            for video in video_files:
                file_path = os.path.join(root, video)
                file_size = os.path.getsize(file_path)
                
                # Find the largest file in the subfolder
                if file_size > largest_size:
                    largest_size = file_size
                    largest_file = file_path

            # Only process the largest file in the subfolder
            if largest_file:
                name, year = extract_name_and_year(os.path.basename(largest_file))
                source, quality = extract_source_and_quality(os.path.basename(largest_file))
                
                print(f"Processing largest file in subfolder: {largest_file}")
                print(f"Extracted Name: {name}, Extracted Year: {year}")

                if name is None or year is None:
                    print(f"Skipping file (unable to extract name/year): {largest_file}")
                    skipped_files.append(largest_file)
                    continue
                
                # Step 4: Folder name format: Name (Year)
                folder_name = f"{name} ({year})"
                
                # Step 5: File name format (including source and quality): Name (Year) - Source-Quality
                if quality and source:
                    hardlink_name = f"{name} ({year}) {source}-{quality}"
                elif quality:
                    hardlink_name = f"{name} ({year}) {quality}"
                elif source:
                    hardlink_name = f"{name} ({year}) {source}"
                else:
                    hardlink_name = f"{name} ({year})"  # If neither source nor quality is found

                file_data.append([largest_file, folder_name, hardlink_name])

    return file_data, skipped_files

# Function to create hardlink in Folder 2 with check for existing file
def create_hardlinks_in_folder(folder2_path, file_data):
    for file_path, folder_name, hardlink_name in file_data:
        # Create folder in Folder 2 if it doesn't exist
        folder_path = os.path.join(folder2_path, folder_name)
        pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
        
        # Get the original file extension (.mkv or .mp4)
        file_extension = os.path.splitext(file_path)[1]  # Get file extension (.mkv, .mp4, etc.)

        # Hardlink path, now using the original file extension
        hardlink_path = os.path.join(folder_path, f"{hardlink_name}{file_extension}")
        
        # Check if the hardlink already exists
        if os.path.exists(hardlink_path):
            print(f"Skipping: Hardlink already exists for {hardlink_path}")
        else:
            os.link(file_path, hardlink_path)
            print(f"Created hardlink: {hardlink_path}")

# Function to process the skipped files
def process_skipped_files(skipped_files):
    skipped_file_data = []
    for file_path in skipped_files:
        filename = os.path.basename(file_path)
        name, year = extract_name_and_year(filename)
        source, quality = extract_source_and_quality(filename)

        # If the name and year were extracted properly
        if name and year:
            folder_name = f"{name} ({year})"
            if quality and source:
                hardlink_name = f"{name} ({year}) {source}-{quality}"
            elif quality:
                hardlink_name = f"{name} ({year}) {quality}"
            elif source:
                hardlink_name = f"{name} ({year}) {source}"
            else:
                hardlink_name = f"{name} ({year})"
            
            skipped_file_data.append([file_path, folder_name, hardlink_name])

    return skipped_file_data

def main():
    # Open folder dialog for Folder 1 (source)
    Tk().withdraw()  # Hide the root Tk window
    folder1_path = filedialog.askdirectory(title="Select Folder 1 (Movies Folder)")

    if not folder1_path:
        print("Folder 1 not selected.")
        return

    # Open folder dialog for Folder 2 (destination)
    folder2_path = filedialog.askdirectory(title="Select Folder 2 (Destination Folder)")

    if not folder2_path:
        print("Folder 2 not selected.")
        return

    # Process files from Folder 1
    file_data, skipped_files = process_files_in_folder(folder1_path)

    # Create hardlinks in Folder 2
    create_hardlinks_in_folder(folder2_path, file_data)

    # Process skipped files and create hardlinks for them
    skipped_file_data = process_skipped_files(skipped_files)
    create_hardlinks_in_folder(folder2_path, skipped_file_data)

    # Output skipped files for user review
    if skipped_files:
        print("\nSkipped Files (Unable to extract name/year):")
        for skipped_file in skipped_files:
            print(f"  {skipped_file}")

    print(f"\nHardlinks created in {folder2_path}")

if __name__ == "__main__":
    main()
