import os
import subprocess
import shutil
from fractions import Fraction

def get_script_dir():
    """Get the directory where the script is located."""
    return os.path.dirname(os.path.realpath(__file__))

def calculate_aspect_ratio(width, height):
    """Calculate the aspect ratio from resolution."""
    aspect_ratio = Fraction(width, height).limit_denominator()
    return f"{aspect_ratio.numerator}:{aspect_ratio.denominator}"

def get_video_info(video_path, ffprobe_path):
    """Get the resolution and display aspect ratio of the video."""
    cmd = [ffprobe_path, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,display_aspect_ratio", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    width, height, dar = result.stdout.decode().strip().split('\n')
    return int(width), int(height), dar

def correct_dar(dest_path, ffmpeg_path, correct_aspect_ratio):
    """Correct the DAR to the calculated aspect ratio, maintaining the original file format."""
    print(f"Correcting DAR for: {dest_path} to {correct_aspect_ratio}")

    # Extract the file extension and create a temporary file name with the same extension
    file_extension = os.path.splitext(dest_path)[1]
    temp_path = dest_path + "_temp" + file_extension

    # Run FFmpeg with reduced log level
    subprocess.run([ffmpeg_path, "-loglevel", "error", "-i", dest_path, "-c", "copy", "-aspect", correct_aspect_ratio, temp_path])
    
    # Replace the temp file with the corrected file name
    corrected_path = dest_path.replace("_temp", "_corrected")
    shutil.move(temp_path, corrected_path)
    print(f"Finished processing: {corrected_path}")

def process_directory(directory, ffprobe_path, ffmpeg_path):
    """Process all MP4 and AVI files in the directory and correct in place if necessary."""
    print(f"Starting to process directory: {directory}")
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ["fixed", "marquee"]]  # Skip 'fixed' and 'marquee' directories
        for file in files:
            if file.lower().endswith((".mp4", ".avi")):  # Check for both .mp4 and .avi files
                full_path = os.path.join(root, file)
                width, height, dar = get_video_info(full_path, ffprobe_path)
                correct_aspect_ratio = calculate_aspect_ratio(width, height)
                if dar != correct_aspect_ratio:
                    corrected_dir = os.path.join(directory, "fixed")
                    os.makedirs(corrected_dir, exist_ok=True)
                    corrected_path = os.path.join(corrected_dir, os.path.relpath(full_path, start=directory))

                    # Ensure the target directory for the corrected file exists
                    os.makedirs(os.path.dirname(corrected_path), exist_ok=True)

                    print("Copying to:", corrected_path)
                    shutil.copy(full_path, corrected_path)
                    correct_dar(corrected_path, ffmpeg_path, correct_aspect_ratio)
    print("Processing complete.")


script_dir = get_script_dir()
ffprobe_executable = os.path.join(script_dir, "ffprobe.exe")
ffmpeg_executable = os.path.join(script_dir, "ffmpeg.exe")

print("Script started.")
print(f"Using ffprobe at: {ffprobe_executable}")
print(f"Using ffmpeg at: {ffmpeg_executable}")

# Use the script's current directory as the search directory
search_directory = script_dir
print(f"Searching in directory: {search_directory}")
process_directory(search_directory, ffprobe_executable, ffmpeg_executable)
print("Script finished.")
