import os
import random

import openai
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import time


# Scopes required to access YouTube Data API
SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    
]

CLIENT_SECRETS_FILE = 'authentication/client_secret.json'

# Set your OpenAI API key securely
openai.api_key = ""


# List of User-Agent strings to rotate through
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.6 Mobile/15E148 Safari/537.36"
]

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080)

    youtube = build('youtube', 'v3', credentials=credentials)

    # Randomly select a User-Agent string for each request
    random_user_agent = random.choice(USER_AGENTS)
    youtube._http.headers = {
        "User-Agent": random_user_agent
    }

    return youtube



def post_comment(youtube, video_id, ai_comment, output_file="data/response_ids.json"):
    try:
        # Create the request to insert a comment
        request = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": ai_comment
                        }
                    }
                }
            }
        )
        # Execute the request and fetch the response
        response = request.execute()
        response_id = response.get("id")
        
        # Print the response ID
        
        
        # Save the response ID to a JSON file
        save_response_id_to_json_append(response_id, output_file)
        return response
    except HttpError as e:
        print(f"Failed to post comment: {e}")
        return None

def save_response_id_to_json_append(response_id, output_file):
    try:
        # Read existing data or start with an empty list
        try:
            with open(output_file, "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []  # Start with an empty list if file doesn't exist or is invalid

        # Append the new response ID
        data.append({"id": response_id})

        # Write the updated list back to the file
        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)

        print(f"Response ID added to {output_file}")
    except Exception as e:
        print(f"Failed to save response ID to JSON file: {e}")

# Fetch videos from the given channel ID

# Save video data and comments in a JSON file




def get_latest_videos_with_comments(youtube, channel_id, max_results=50, max_comment_length=1000):
    try:
        # Fetch latest videos from the channel
        request = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            order='date',
            maxResults=max_results
        )
        response = request.execute()
        videos = response.get('items', [])
        
        # List to store videos and their comments
        video_data = []

        for video in videos:
            video_id = video['id'].get('videoId')
            if not video_id:
                continue

            video_info = {
                'video_id': video_id,
                'title': video['snippet']['title'],
                'comments': []
            }

            try:
                # Fetch top comments for the video
                comments_request = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=4,
                    order='relevance'  # Fetch the most relevant comments
                )
                comments_response = comments_request.execute()
                
                for comment in comments_response.get('items', []):
                    top_comment = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                    
                    # Check if the comment exceeds the maximum length
                    if len(top_comment) <= max_comment_length:
                        video_info['comments'].append(top_comment)
                    else:
                        print(f"Excluded an excessively long comment for video ID {video_id}")

            except HttpError as e:
                if 'commentsDisabled' in str(e):
                    print(f"Comments are disabled for video ID {video_id}")
                else:
                    print(f"Failed to fetch comments for video ID {video_id}: {str(e)}")

            # Add the video info with comments (if any) to the list
            video_data.append(video_info)

        return video_data

    except HttpError as e:
        print(f"Failed to fetch videos: {str(e)}")
        return []



def generate_comment(video_title, video_comments):
    # Prepare comments as a single string
    comments_string = "\n".join(video_comments)

    prompt = (
        f"Write a comment for this youtube video titled '{video_title}'. Take inspiration from these comments {comments_string}. Make it kind, engaging and authentic."
    )

#f"Write a kind YouTube comment for a video titled '{video_title}'. Use inspiration from these user comments: {comments_string}. "
        #"Aim for a comment that feels authentic and could become a top comment by being relatable or insightful. Do not use links or quotation marks in the response.
    
    try:
        # Generate the initial response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are music enthusiast"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.8,
            presence_penalty=0.3,
        )

        # Access the generated content
        generated_text = response['choices'][0]['message']['content'].strip()

        # Summarize the response to make it more concise
        summarize_prompt = f"Shorten this youtube comment to 1 sentence while maintaining its message: \n{generated_text}. Remove any qutation marks and input boxes as well. Make sure it does not make any controversial statements."
        
        summary_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You summarize youtube comments"},
                {"role": "user", "content": summarize_prompt}
            ],
            max_tokens=70,
            temperature=0.7,
            top_p=0.8,
            frequency_penalty=0.4,
            presence_penalty=0.6,
        )

        return summary_response['choices'][0]['message']['content'].strip()

    except openai.error.OpenAIError as e:
        print(f"Error generating comment: {str(e)}")
        return None




def save_comment_log(video_id, video_title, ai_comment, video_comments, channel_id):
    try:
        # Create a new log entry
        log_entry = {
            "channel_id": channel_id,
            "video_id": video_id,
            "title": video_title,
            "comment": ai_comment,
            "inspiration_comment": video_comments,
        }

        # Read existing data from the JSON file
        try:
            with open("data/full_comment_log.json", "r") as log_file:
                existing_data = json.load(log_file)
        except FileNotFoundError:
            # If the file doesn't exist, start with an empty list
            existing_data = []

        # Ensure the data is a list
        if not isinstance(existing_data, list):
            raise ValueError("The JSON file does not contain a valid list.")

        # Append the new log entry to the existing data
        existing_data.append(log_entry)

        # Write the updated data back to the JSON file
        with open("data/full_comment_log.json", "w") as log_file:
            json.dump(existing_data, log_file, indent=4)

        print("Comment log updated.")
    except Exception as e:
        print(f"Error saving comment log: {e}")

def get_latest_comments(youtube, video_id, max_results=2):
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        order="time"
    )
    response = request.execute()
    comments = []
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        comments.append({
            'authorChannelId': comment['authorChannelId'],
            'text': comment['textDisplay']
        })
    return comments

def get_authenticated_channel_id(youtube):
    request = youtube.channels().list(
        part="id",
        mine=True
    )
    response = request.execute()
    return response['items'][0]['id']



if __name__ == "__main__":
    CHANNEL_ID = input("Enter the channel ID: ")
    channel_id = str(CHANNEL_ID)
    
    youtube = get_authenticated_service()
    
    # Fetch the authenticated user's channel ID
    your_channel_id = get_authenticated_channel_id(youtube)
    print(f"Authenticated user's channel ID: {your_channel_id}")

    # Fetch the latest videos with comments
    videos = get_latest_videos_with_comments(youtube, CHANNEL_ID)
    random.shuffle(videos)
    # Initialize posted video IDs to prevent duplicate comments
    posted_video_ids = set()

    for video in videos:
        video_id = video['video_id']
        video_title = video['title']
        video_comments = video.get('comments', [])  # Safe way to access comments
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        ai_comment = generate_comment(video_title, video_comments)

        save_comment_log(video_id, video_title, ai_comment, video_comments, channel_id)

        if ai_comment and video_id not in posted_video_ids:
            print("---------------")
            print(f"Generated comment for: {video_title}")
            print(f"Video URL: {video_url}")

            # Post the comment to YouTube
            try:
                post_comment(youtube, video_id, ai_comment)
            except HttpError as e:
                print(f"Failed to post comment for {video_id}: {str(e)}")
                continue
            
            # Mark this video ID as commented
            posted_video_ids.add(video_id)
            time.sleep(60)
            # Verify if the comment was posted
            try:
                comments = get_latest_comments(youtube, video_id, max_results=2)
                comment_found = False
                for comment in comments:
                    if comment['authorChannelId']['value'] == your_channel_id:
                        print(f"Comment successfully posted by channel: {your_channel_id}")
                        comment_found = True
                        break
                if not comment_found:
                    print(comment['authorChannelId']['value'])
                    print(f"Comment not found for video {video_id}")
                    break
            except HttpError as e:
                print(f"Failed to verify comment for {video_id}: {str(e)}")

            print("---------------")

            # Avoid API quota overload with random short delay
            time.sleep(random.randint(60, 180))

