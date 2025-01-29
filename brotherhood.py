import os
import random
import openai
import ffmpeg
from PIL import Image, ImageDraw, ImageFont
import textwrap
import subprocess
import base64
import requests
from typing import List, Optional

def init_openai_client(api_key: Optional[str] = None) -> openai.Client:
    """Initialize OpenAI client with API key."""
    if api_key is None:
        api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key is required")
    return openai.Client(api_key=api_key)

def generate_and_save_images(
    prompt: str,
    save_directory: str = "AiImages/Brotherhood",  # Relative path
    model: str = "dall-e-3",
    n: int = 1,
    quality: str = "standard",
    size: str = "1024x1024",
    style: str = "vivid",
    response_format: str = "url",
    api_key: Optional[str] = None
) -> List[str]:
    """Generate and save DALL-E images"""
    try:
        client = init_openai_client(api_key)
        
        # Create directory in current working directory
        os.makedirs(save_directory, exist_ok=True)
        
        # Generate image
        response = client.images.generate(
            prompt=prompt,
            model=model,
            n=n,
            quality=quality,
            size=size,
            style=style,
            response_format=response_format
        )

        # Save image
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        file_path = os.path.join(save_directory, "brotherhood_image.png")
        with open(file_path, "wb") as file:
            file.write(img_data)
        
        return [file_path]

    except Exception as e:
        print(f"Error: {str(e)}")
        return []





def get_unique_output_path(output_path):
    """
    Check if the output file already exists. If it does, add a suffix to make it unique.
    """
    base, ext = os.path.splitext(output_path)
    counter = 1
    while os.path.exists(output_path):
        output_path = f"{base}_{counter}{ext}"
        counter += 1
    return output_path


api_key = ''
client = openai.Client(api_key=api_key)

os.environ['OPENAI_API_KEY'] = ""


# Input video folder
input_folder = 'backgrounds/brotherhood'
output_folder = 'Brotherhood'
used_quotes_file = 'usedquotes/brotherhood.txt'
music_folder = 'music'
os.makedirs(output_folder, exist_ok=True)

# Load used quotes
if os.path.exists(used_quotes_file):
    with open(used_quotes_file, 'r') as f:
        used_quotes = set(f.read().splitlines())
else:
    used_quotes = set()

# Number of videos to produce
num_videos_to_produce = int(input("How many videos do you want to produce? "))

# Filter out non-video files
video_files = [f for f in os.listdir(input_folder) if f.endswith(('.mp4', '.mov', '.avi', '.mkv'))]

# Filter out non-audio files
audio_files = [f for f in os.listdir(music_folder) if f.endswith(('.mp3', '.wav', '.aac'))]

# Ensure we don't try to produce more videos than available
if len(video_files) == 0:
    print("No video files found in the input folder.")
    exit()

if len(audio_files) == 0:
    print("No audio files found in the music folder.")
    exit()

# Define potential songs for each type of video
deep_songs = [song for song in audio_files if any(keyword in song for keyword in ['FinalHour', 'MountingPressure', '2025za', 'zamental', 'TaiShanEcho', 'HuaShanSpirit', 'CallofMountain','QuinDynasty','YunnanSoul', 'mars'])]
catchy_songs = [song for song in audio_files if any(keyword in song for keyword in ['QuinDynasty','JinDynasty','CheeryBlossoms','YunnanSoul', '2025za', 'zamental', 'TaiShanEcho', 'HuaShanSpirit', 'CallofMountain','QuinDynasty','YunnanSoul', 'mars'])]
warrior_songs = [song for song in audio_files if any(keyword in song for keyword in [ 'TaiShanEcho', 'HuaShanSpirit', 'CallofMountain','QuinDynasty','YunnanSoul', '2025za', 'zamental', 'mars'])]


# Define possible file names for each type of video
ice_file_names = ['forest']
forest_file_names = ['flower']
squad_file_names = ['ship']

for i in range(num_videos_to_produce):
    selected_video = video_files[i % len(video_files)]  # Loop through the available files
    input_path = os.path.join(input_folder, selected_video)
    
    # Determine the next available number for the output video
    if 'forest' in selected_video:
        base_title = random.choice(ice_file_names)
    elif 'flower' in selected_video:
        base_title = random.choice(forest_file_names)
    elif 'ship' in selected_video:
        base_title = random.choice(squad_file_names)
    else:
        base_title = "video"

    

    # Select a random audio file based on the selected video
    if 'forest' in selected_video:
        selected_audio = random.choice(deep_songs)
    elif 'flower' in selected_video:
        selected_audio = random.choice(catchy_songs)
    elif 'ship' in selected_video:
        selected_audio = random.choice(warrior_songs)
    else:
        selected_audio = random.choice(audio_files)  # Fallback to any audio file if no specific type matches

    audio_path = os.path.join(music_folder, selected_audio)

     
    # Define the prompt based on the selected video
    if 'flower' in selected_video:
        prompt = f"Write a deep meme caption about me and bro"
    elif 'forest' in selected_video:
        prompt = f"Write a meme caption about me and bro, or the bros, hanging out"
    elif 'ship' in selected_video:
        prompt = f"Write a deep meme caption about that one bro"
    else:
        prompt = f"You are a bro content creator"

    print(prompt)
    # Get the response from ChatGPT using the new API
    while True:
        response = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-0125:personal::ApicTOku",
            messages=[
                {"role": "system", "content": "You are a meme creator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60,
            temperature=0.9,
            top_p=0.9,
            frequency_penalty=0.9,
            presence_penalty=0.9,
        )

        # Extract the response text
        caption = response.choices[0].message.content.strip()

        # Check if the quote is already used
        if caption not in used_quotes:
            used_quotes.add(caption)
            with open(used_quotes_file, 'a') as f:
                f.write(caption + '\n')
            break

    print(f"Generated Quote: {caption}")



    ### IF NEEDED: Define the prompt to shorten the quote ###
    # shorten_prompt = f"Rewrite this more concise while mainting the irony and funny tone: {quote}"

    # response_shortened = client.chat.completions.create(
    #     model="ft:gpt-3.5-turbo-0125:personal::AnCMDLT6",
    #     messages=[
    #         {"role": "system", "content": "You rewrite memes like a pro."},
    #         {"role": "user", "content": shorten_prompt}
    #     ],
    #     max_tokens=50,
    #     temperature=0.5,
    #     top_p=0.5,
    #     frequency_penalty=0.5,
    #     presence_penalty=0.5,
    # )
    # caption = response_shortened.choices[0].message.content.strip()
    # print(f"Shortened Quote: {caption}")



    ### IMAGE GENERATION ###
    try:
        image_prompt = f"Make a funny pixel art image for a meme with this caption that visualizes what has been said: {caption}. Do not use any text in the image."
        image_paths = generate_and_save_images(
            prompt=image_prompt,
            save_directory="AiImages/Brotherhood",  # Use relative path
        )
        
        if image_paths:
            print(f"Image saved successfully at: {image_paths[0]}")
        else:
            print("Failed to generate and save image")
    except Exception as e:
        print(f"Error generating image: {str(e)}")

  
 #### CAPTION OVERLAY ####

    overlay_path_heading = 'heading_overlay.png'
    overlay_path_text = 'text_overlay.png'
    video_width, video_height = 1920, 1080  # Set video resolution

    # Font settings
    font_size = 70  # Adjusted font size
    font_size_header = 20
    font_color = (255, 255, 255)
    outline_color = (0, 0, 0)
    underline_color = font_color  # Use the same color as the text for the underline
    font_paths = ['fonts/Roboto-Regular.ttf', 'fonts/Roboto-Medium.ttf']
    font_path = random.choice(font_paths)
    font_path_headers = ['fonts/Roboto-BlackItalic.ttf', 'fonts/Roboto-Black.ttf']
    font_path_header = random.choice(font_paths)

    # Set the heading based on the selected video
    
    heading = "@mythical_brotherhood"

    # Wrap heading into lines
    wrapped_heading = textwrap.fill(heading, width=40)
    heading_lines = wrapped_heading.split('\n')

    # Calculate the total height of the heading text
    total_heading_height = len(heading_lines) * font_size_header

    # Set the overlay height to be slightly larger than the total heading height
    #overlay_height = total_heading_height + 20  # Adding some padding

    # Create the heading overlay image with the calculated height
    heading_img = Image.new('RGBA', (video_width, video_height), (0, 0, 0, 0))  # Fully transparent background
    heading_draw = ImageDraw.Draw(heading_img)
    heading_font = ImageFont.truetype(font_path, font_size_header)

    # Calculate vertical centering for heading
    starting_y_heading = 10  # Adding some padding at the top

    # Draw heading line-by-line with outline
    for i, line in enumerate(heading_lines):
        bbox = heading_draw.textbbox((0, 0), line, font=heading_font)
        text_width = bbox[2] - bbox[0]
        x = (video_width - text_width) // 2
        y = starting_y_heading + i * font_size_header
        
        # Draw thicker outline
        heading_draw.text((x-3, y-3), line, font=heading_font, fill=outline_color)
        heading_draw.text((x+3, y-3), line, font=heading_font, fill=outline_color)
        heading_draw.text((x-3, y+3), line, font=heading_font, fill=outline_color)
        heading_draw.text((x+3, y+3), line, font=heading_font, fill=outline_color)
        heading_draw.text((x-3, y), line, font=heading_font, fill=outline_color)
        heading_draw.text((x+3, y), line, font=heading_font, fill=outline_color)
        heading_draw.text((x, y-3), line, font=heading_font, fill=outline_color)
        heading_draw.text((x, y+3), line, font=heading_font, fill=outline_color)
        
        # Draw main text
        heading_draw.text((x, y), line, font=heading_font, fill=font_color)
    
    # Draw underline
    underline_y = y + font_size_header + 5
    heading_draw.line((x, underline_y, x + text_width, underline_y), fill=underline_color, width=2)
    # Save heading overlay image
    heading_img.save(overlay_path_heading)
    print(f"Heading overlay image saved to {overlay_path_heading}")

    # Create the text overlay image
    text_img = Image.new('RGBA', (video_width, video_height), (0, 0, 0, 0))  # Fully transparent background
    text_draw = ImageDraw.Draw(text_img)

    # Load font
    try:
        text_font = ImageFont.truetype(font_path_header, font_size)
    except OSError:
        print("Font file not found. Check the font path.")
        exit()

    # Wrap text into lines
    wrapped_caption = textwrap.fill(caption, width=34)
    text_lines = wrapped_caption.split('\n')

    # Calculate vertical centering for text
    total_text_height = len(text_lines) * font_size
    starting_y_text = (video_height - total_text_height) // 2

    # Draw text line-by-line with outline
    for i, line in enumerate(text_lines):
        bbox = text_draw.textbbox((0, 0), line, font=text_font)
        text_width = bbox[2] - bbox[0]
        x = (video_width - text_width) // 2
        y = starting_y_text + i * font_size
        
        # Draw thicker outline
        text_draw.text((x-3, y-3), line, font=text_font, fill=outline_color)
        text_draw.text((x+3, y-3), line, font=text_font, fill=outline_color)
        text_draw.text((x-3, y+3), line, font=text_font, fill=outline_color)
        text_draw.text((x+3, y+3), line, font=text_font, fill=outline_color)
        text_draw.text((x-3, y), line, font=text_font, fill=outline_color)
        text_draw.text((x+3, y), line, font=text_font, fill=outline_color)
        text_draw.text((x, y-3), line, font=text_font, fill=outline_color)
        text_draw.text((x, y+3), line, font=text_font, fill=outline_color)
        
        # Draw main text
        text_draw.text((x, y), line, fill=font_color, font=text_font)

    # Save text overlay image
    text_img.save(overlay_path_text)
    print(f"Text overlay image saved to {overlay_path_text}")

        # Define the path to the generated image
    if image_paths:
        overlay_image_path = image_paths[0]
    else:
        raise Exception("No image generated for overlay.")

    try:
        # Input and output paths
        input_video = ffmpeg.input(input_path)
        input_audio = ffmpeg.input(audio_path)
        output_path = "Brotherhood/final.mp4"
        output_path = get_unique_output_path(output_path)

        # FFmpeg filter chain for 9:16 format
        (
ffmpeg
.concat(input_video, input_audio, v=1, a=1)
.output(
    output_path,
    filter_complex=(
        # Base video with heading at top
        f"movie='{overlay_path_heading}',scale=1080:-2[wm1];"
        f"[0:v][wm1]overlay=(main_w-overlay_w)/2:900:enable=gte(t\\,0.1)[v1];"
        
        # Center text overlay
        f"movie='{overlay_path_text}',scale=1080:-2[wm2];"
        f"[v1][wm2]overlay=(main_w-overlay_w)/2:((main_h-overlay_h)/2)-340:enable=gte(t\\,0.4)[v2];"
        
        # Main image below text
        f"movie='{overlay_image_path}',scale=810:-2[image];"
        f"[v2][image]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2+200:enable=gte(t\\,0.4)"
    ),
    vcodec="libx264",
    acodec="aac",
    shortest=None
)
.run()
)
        print(f"Video with image overlay saved at {output_path}")

        # Remove duplicate streams
        cleaned_output_path = get_unique_output_path("Brotherhood/cleaned_final.mp4")
        
        command = [
            "ffmpeg", "-i", output_path, 
            "-map", "0:v:0",  # First video stream
            "-map", "0:a:0?", # First audio stream if available
            "-c:v", "copy",   # Copy video codec
            "-c:a", "copy",   # Copy audio codec
            cleaned_output_path
        ]
        
        print(f"Removing duplicate streams from {output_path}...")
        subprocess.run(command, check=True)
        print(f"Cleaned video saved as: {cleaned_output_path}")
        
        # Clean up files
        if os.path.exists(output_path):
            os.remove(output_path)
            print(f"Original output video removed: {output_path}")
        if os.path.exists(overlay_path_heading):
            os.remove(overlay_path_heading)
            print("Temporary heading overlay image removed.")
        if os.path.exists(overlay_path_text):
            os.remove(overlay_path_text)
            print("Temporary text overlay image removed.")

    except ffmpeg.Error as e:
        print("FFmpeg Error:", e)
    except subprocess.CalledProcessError as e:
        print(f"Error in subprocess: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")