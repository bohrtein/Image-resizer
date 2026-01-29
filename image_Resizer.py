import os
from PIL import Image

# Disable the decompression bomb protection
Image.MAX_IMAGE_PIXELS = None 

path = r"D:\Trivelo\tirivelo-web\public\images"

def get_initial_inputs():
    tag = input("Enter the filename prefix (tag): ").strip()
    return path, tag

def process_single_image(file_path, save_path, scale_factor):
    """Handles image manipulation and replaces transparency with white."""
    try:
        with Image.open(file_path) as img:
            # 1. Calculate new size
            new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
            
            # 2. Resize original
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 3. Handle Transparency (The "Black Frame" Fix)
            if img.mode in ("RGBA", "P"):
                # Create a solid white background the same size as the resized image
                background = Image.new("RGB", new_size, (255, 255, 255))
                # Paste the image onto the white background using its own alpha as a mask
                background.paste(img, (0, 0), img.convert("RGBA"))
                final_img = background
            else:
                final_img = img.convert("RGB")
            
            # 4. Save
            final_img.save(save_path, "JPEG", optimize=True, quality=85)
            return True, new_size
    except Exception as e:
        return False, str(e)

def run_loop(directory, prefix):
    directory = os.path.normpath(directory)
    output_dir = os.path.join(directory, "optimized_output")
    os.makedirs(output_dir, exist_ok=True)

    files = [f for f in os.listdir(directory) if f.lower().startswith(prefix.lower()) 
             and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if not files:
        print(f"No files found starting with '{prefix}'")
        return

    for filename in files:
        source = os.path.join(directory, filename)
        destination = os.path.join(output_dir, filename)

        # Get original dimensions
        with Image.open(source) as img:
            orig_w, orig_h = img.size
        
        print(f"\n" + "="*40)
        print(f"FILE: {filename}")
        print(f"ORIGINAL SIZE: {orig_w} x {orig_h}")

        chosen_scale = 1.0
        
        # Inner loop to "preview" resolution changes
        while True:
            user_in = input(f"Enter % to resize (Empty for 100%, 's' to skip, 'y' to confirm current): ").strip().lower()

            if user_in == "":
                chosen_scale = 1.0
                break   
            if user_in == 's':
                chosen_scale = None
                break
            if user_in == 'y':
                break
            
            try:
                temp_scale = float(user_in.replace('%', '')) / 100
                new_w = int(orig_w * temp_scale)
                new_h = int(orig_h * temp_scale)
                print(f"--> NEW PREVIEW: {new_w} x {new_h} pixels")
                chosen_scale = temp_scale
                # It loops again so you can enter a different number or 'y' to confirm
            except ValueError:
                print("Invalid input. Enter a number, 'y' to confirm, or 's' to skip.")

        if chosen_scale:
            print(f"Processing...")
            success, result = process_single_image(source, destination, chosen_scale)
            if success:
                print(f"[SUCCESS] Saved as {result[0]}x{result[1]}")
            else:
                print(f"[ERROR] {result}")

    print("\nAll tasks finished.")

if __name__ == "__main__":
    folder, tag = get_initial_inputs()
    run_loop(folder, tag)