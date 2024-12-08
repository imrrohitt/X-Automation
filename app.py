import requests
import json
from requests_oauthlib import OAuth1Session
import re
import schedule
import time
from datetime import datetime

# Define your credentials here
GROQ_API_KEY = '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'  # Replace with your Groq API key
TWITTER_CONSUMER_KEY = 'oZd1HFFLyGCqrsEo70nQCatMX'
TWITTER_CONSUMER_SECRET = 'Ytbx3P6xWhAqcs7cSoDZYlbNuaiC0u9ECe2vjaMIw5tVNafo5M'
TWITTER_ACCESS_TOKEN = '1557747240776892417-3WRco08xNgdBWsYhV90eqHNhUuwXOE'
TWITTER_ACCESS_TOKEN_SECRET = '3iu8LMLjnObnaqHpLS0QzSx2MqibVrr091qp3khadDasS'

# Groq API endpoint and parameters for content generation
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_MODEL = 'llama3-8b-8192'  # Replace with the model you want to use

# Twitter's character limit for a tweet
TWITTER_CHAR_LIMIT = 280

def generate_content():
    """
    Generate content using the Groq API, ensuring the content is concise.
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GROQ_API_KEY}'
    }

    # Define the prompt for generating concise content about ReactJS
    payload = {
        'model': GROQ_MODEL,
        'messages': [
            {
                'role': 'user',
                'content': 'JS topic event loop with emojies also . Limit the response to around 200 characters.'
            }
        ]
    }

    try:
        print("Sending request to Groq API...")
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        print(f"Groq API response status: {response.status_code}")

        if response.status_code == 200:
            generated_text = response.json()['choices'][0]['message']['content']
            print("Successfully generated content from Groq API.")
            return generated_text
        else:
            print(f"Failed to generate content. Groq API response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error generating content: {e}")
        return None

def sanitize_content(content):
    """
    Sanitize the response by removing unwanted characters and cleaning up the text.
    """
    # Remove unwanted characters such as extra spaces, newlines, and special characters
    content = re.sub(r'\s+', ' ', content)  # Replace multiple spaces with a single space
    content = content.strip()  # Remove leading/trailing spaces
    content = content.replace("\n", " ")  # Replace newlines with space
    return content

def truncate_content(content):
    """
    This function truncates the content to fit Twitter's character limit.
    If the content is too long, it adds '...' at the end to indicate truncation.
    """
    if len(content) > TWITTER_CHAR_LIMIT:
        print(f"Content exceeds {TWITTER_CHAR_LIMIT} characters. Truncating...")
        content = content[:TWITTER_CHAR_LIMIT - 3] + "..."  # Truncate and add '...' to indicate cut-off
    return content

def post_to_twitter(content):
    """
    Post the sanitized and truncated content to Twitter using OAuth1 authentication.
    """
    twitter_url = 'https://api.twitter.com/2/tweets'

    # Create OAuth1Session instance for Twitter authentication
    oauth = OAuth1Session(
        TWITTER_CONSUMER_KEY,
        client_secret=TWITTER_CONSUMER_SECRET,
        resource_owner_key=TWITTER_ACCESS_TOKEN,
        resource_owner_secret=TWITTER_ACCESS_TOKEN_SECRET
    )

    # Sanitize and truncate the content to ensure it fits within Twitter's character limit
    content = sanitize_content(content)
    content = truncate_content(content)

    # Define the data payload for the tweet
    tweet_data = {
        'text': content  # 'status' changed to 'text' for Twitter API v2
    }

    try:
        print("Sending request to Twitter API...")
        response = oauth.post(twitter_url, json=tweet_data)
        print(f"Twitter API response status: {response.status_code}")

        if response.status_code == 201:
            print("Successfully posted the tweet!")
        else:
            print(f"Error posting tweet. Twitter API response: {response.status_code}, {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error posting tweet: {e}")

def generate_and_post():
    """
    Generate content from Groq and post it to Twitter.
    """
    content = generate_content()
    if content:
        print("Generated content:", content)
        post_to_twitter(content)
    else:
        print("Failed to generate content.")

# Schedule the job for 9 AM and 9 PM
# schedule.every().day.at("09:00").do(generate_and_post)

# Schedule the job to run every 2 minutes for testing
# schedule.every(2).minutes.do(generate_and_post)


schedule.every().day.at("21:00").do(generate_and_post)

# Run the schedule loop
if __name__ == "__main__":
    print(f"Scheduler started at {datetime.now()}")
    while True:
        schedule.run_pending()  # Run pending scheduled tasks
        time.sleep(60)  # Wait for one minute before checking again
