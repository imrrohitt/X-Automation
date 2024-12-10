import requests
import json
import re
import schedule
import time
from datetime import datetime

# Define your credentials here
GROQ_API_KEY = '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'  # Replace with your Groq API key
LINKEDIN_ACCESS_TOKEN = 'AQWGuKDWRDOFILzNfL8IPwg8qMEPjTMfuDfs_vDRPJwm7mJDfI1q5FtP-TK75PQOqj0zcUo-Yq8-aXHZCOssEPKwFCLCdfAcqP3yoD1NyPWoD7eg6vuFaMRgZmPdW7FxrJej53mpUKQFkZMIcXvQybkP_SmLg-ndg94iJkXR108fDDpBui8PKogqc2gHDryQ5R9zx9gQzRXrU9RPjhp3P4a944fnxlhSx-jecEUoISdmCE9BiWy8WUCC1iXyrDCAG4cmUNr1froBm6kNHmS3rqPGVE2QwzoWRG_tRZX1Be_Vpuw1rK1xH200Wo-w_d-l9_QtXlD4GiFT-7AyBYXMZvLvW9MwrQ'
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_MODEL = 'llama3-8b-8192'  # Replace with the model you want to use

def generate_content():
    """
    Generate dynamic content using the Groq API with a focus on coding logic explanations.
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GROQ_API_KEY}'
    }

    # Define a dynamic prompt for generating diverse content
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Pick one coding topic, explain it simply, and add lots of emojis!"
            }
        ],
        "temperature": 1.0
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
    Sanitize the response by removing unwanted characters, markdown syntax, excessive spaces,
    and ensuring the content is professionally formatted for LinkedIn posts.
    Handles emojis, links, punctuation, and coding-related symbols properly.
    """
    # 1. Handle heading separators (lines with multiple '=' or '-')
    content = re.sub(r'^[=]{2,}$', '\n\n', content, flags=re.MULTILINE)
    content = re.sub(r'^[-]{2,}$', '\n\n', content, flags=re.MULTILINE)
    
    # 2. Remove Markdown Syntax (e.g., **, *, __, etc.)
    content = re.sub(r'(\*\*|\*|__|_|\`|\~\~)', '', content)
    
    # 3. Replace multiple newlines with double newline to indicate paragraph breaks
    content = re.sub(r'\n+', '\n\n', content)
    
    # 4. Replace multiple spaces with a single space
    content = re.sub(r'[ \t]+', ' ', content)
    
    # 5. Trim leading and trailing spaces
    content = content.strip()
    
    # 6. Allow coding symbols like braces {}, square brackets [], parentheses (), arrows =>, etc.
    content = re.sub(r'([{}()\[\]=;.,])', r' \1 ', content)  # Add space around these symbols for better readability
    
    # 7. Preserve emojis and remove any other unwanted characters
    # Allow non-ASCII characters (to keep emojis), and only remove unwanted special characters
    content = re.sub(r'[^\w\s\.,!?;:()&%$#@=+\-_*“”‘’📚💻🔥✨👩‍💻👨‍💻📝📈📊🚀🎉{}()\[\]=;]', '', content)
    
    # 8. Normalize excessive punctuation
    content = re.sub(r'[!]{2,}', '!', content)
    content = re.sub(r'[?]{2,}', '?', content)
    
    # 9. Ensure emojis and punctuation are properly spaced
    # Add space after punctuation if not followed by space or newline
    content = re.sub(r'([.,!?;:()&%$#@=+\-_*“”‘’📚💻🔥✨👩‍💻👨‍💻📝📈📊🚀🎉])(?!\s|\n)', r'\1 ', content)
    
    # 10. Final cleanup: Remove any leading/trailing spaces introduced during processing
    content = content.strip()

    return content

def post_to_linkedin(content):
    """
    Post the sanitized content to LinkedIn using the LinkedIn API.
    """
    linkedin_url = 'https://api.linkedin.com/v2/ugcPosts'

    # LinkedIn authentication
    headers = {
        'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
    }

    # Sanitize the content
    content = sanitize_content(content)

    # Define the payload for the LinkedIn post
    payload = {
        "author": "urn:li:person:zO8XdF8KuI",  # Replace with your actual LinkedIn user ID
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    try:
        print("Sending request to LinkedIn API...")
        response = requests.post(linkedin_url, headers=headers, json=payload)
        print(f"LinkedIn API response status: {response.status_code}")
        if response.status_code == 201:  # 201 indicates success
            print("Successfully posted to LinkedIn!")
        else:
            print(f"Error posting to LinkedIn. Response: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error posting to LinkedIn: {e}")

def generate_and_post():
    """
    Generate content from Groq and post it to LinkedIn.
    """
    content = generate_content()
    if content:
        print("Generated content:", content)
        post_to_linkedin(content)
    else:
        print("Failed to generate content.")

# Schedule the job for 9 AM and 9 PM
schedule.every().day.at("09:00").do(generate_and_post)
schedule.every().day.at("21:00").do(generate_and_post)

schedule.every(20).minutes.do(generate_and_post)

# Run the schedule loop
if __name__ == "__main__":
    print(f"Scheduler started at {datetime.now()}")
    while True:
        schedule.run_pending()  # Run pending scheduled tasks
        time.sleep(60)  # Wait for one minute before checking again
