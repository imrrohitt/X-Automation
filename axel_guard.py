import requests
import json
from requests_oauthlib import OAuth1Session
import re
import schedule
import time
import random
from datetime import datetime

# ----------------------------
# Configuration & Credentials
# ----------------------------

# Groq API configuration
GROQ_API_KEY = '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'  # Replace with your Groq API key
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_MODEL = 'llama3-8b-8192'  # Replace with the model you want to use

# AxelGuard Twitter account credentials (example keys)
TWITTER_CONSUMER_KEY = 'UMSTp3EdXhPdZrWecjzFTiIKf'
TWITTER_CONSUMER_SECRET = 'ibWj6aNGJ4RqDqtkTqWa3dBcgMeZSOvWoGEEisM9M442rJ30kT'
TWITTER_ACCESS_TOKEN = '1838908598740779008-TP0G3C0OjzV9iJwqSn77cvLNW2Op9w'
TWITTER_ACCESS_TOKEN_SECRET = '034OGg9ZMKVtTfP1fW5r4XiVtuco5MwPWx5BFoxv68JCh'

# Twitter character limit
TWITTER_CHAR_LIMIT = 280

# -----------------------------------------
# Utility Functions: Sanitization & Truncation
# -----------------------------------------
def sanitize_content(content):
    """Remove extra spaces and newlines."""
    content = re.sub(r'\s+', ' ', content)
    return content.strip()

def truncate_content(content):
    """Truncate text to fit Twitter's 280-character limit."""
    if len(content) > TWITTER_CHAR_LIMIT:
        content = content[:TWITTER_CHAR_LIMIT - 3] + "..."
    return content

# --------------------------------------------------------
# Helper: Append a Relevant URL if Tweet is Product-Related
# --------------------------------------------------------
def maybe_append_url(content):
    """
    If the tweet text is related to a product (contains one of the keywords),
    append a corresponding AxelGuard URL. This function ensures the final tweet
    remains under Twitter's character limit.
    """
    if "http" in content:
        return content

    keyword_url_mapping = {
        "MDVR": [
            "http://axel-guard.com/product.html?product_type=basic_mdvr",
            "http://axel-guard.com/product.html?name=MDVR"
        ],
        "Dashcam": [
            "http://axel-guard.com/product.html?product_type=Dashcam",
            "http://axel-guard.com/product.html?name=DashCam"
        ],
        "RFID": [
            "http://axel-guard.com/product.html?product_type=rfid_reader",
            "http://axel-guard.com/product.html?name=RFID"
        ],
        "Camera": [
            "http://axel-guard.com/product.html?product_type=AI_camera",
            "http://axel-guard.com/product.html?name=Camera"
        ]
    }

    for keyword, urls in keyword_url_mapping.items():
        if keyword.lower() in content.lower():
            chosen_url = random.choice(urls)
            suffix = " " + chosen_url
            max_text_length = TWITTER_CHAR_LIMIT - len(suffix)
            if len(content) > max_text_length:
                content = content[:max_text_length].rstrip()
            content = content + suffix
            return content

    return content

# --------------------------------------------------------
# Simulated function: New Product Update Event
# --------------------------------------------------------

# A list of over 100 AxelGuard products
PRODUCTS = [
    "Mobile DVR (MDVR)", "Dashcams", "Outdoor Bullet Camera", "Indoor Dome Cameras",
    "Dashcam Cameras", "AI Camera", "Active RFID Reader", "Active RFID Tags",
    "MDVR Monitor", "15-meter Cable", "Other MDVR Accessories", "360° Vehicle Camera",
    "Advanced GPS Tracker", "Fleet Management System", "Night Vision Dashcam",
    "4G LTE DVR System", "Backup Camera System", "Collision Warning System",
    "Driver Fatigue Monitoring", "AI-Powered Traffic Sign Recognition", "High-Resolution CCTV",
    "Wireless Vehicle Camera", "Smart Parking Assist", "Ultra-HD Dashcam",
    "5G-Enabled Fleet Monitoring", "Live Streaming Dashcam", "Solar-Powered Camera",
    "License Plate Recognition Camera", "Multi-Angle Security Camera", "Advanced Video Analytics",
    "Blind Spot Monitoring System", "Speed Violation Detection", "Thermal Imaging Camera",
    "Dual-Lens Dashcam", "HD MDVR with SSD Storage", "Remote Vehicle Tracking",
    "Driver Behavior Analysis", "Emergency SOS Button", "AI-Based Vehicle Surveillance",
    "Smart Auto-Locking System", "Vehicle Proximity Sensor", "High-End Motion Detection DVR",
    "Heavy-Duty Truck Camera", "Temperature Sensor-Enabled DVR", "Wide-Angle Car DVR",
    "Cloud-Connected Dashcam", "AI-Based Gesture Control Camera", "Weatherproof Car DVR",
    "3D Surround View System", "Smart Engine Immobilizer", "AI-Based Lane Departure Warning",
    "Intelligent Transport Management System", "Edge AI Security Camera", "Waterproof RFID Reader",
    "Emergency Braking Alert System", "Intelligent Object Detection Camera",
    "Onboard AI Security Analytics", "Ultra-Wide Dashcam", "Speed Limit Warning System",
    "Car DVR with AI Night Vision", "Multi-Mode AI Dashcam", "Heavy Machinery Safety Camera",
    "Facial Recognition Security System", "AI-Powered Road Hazard Detection",
    "Multi-Vehicle Fleet Safety Monitor", "Collision Avoidance AI System",
    "Smart Helmet Detection System", "Real-Time AI Traffic Analytics", "Personalized Fleet Alerts",
    "Pedestrian Detection AI", "AI-Powered Voice Command Dashcam", "AI-Based Distance Monitoring",
    "Data Encryption & Security Module", "Cloud-Based Incident Reporting System",
    "Full HD Night Vision Car DVR", "Smart Auto Brake Camera", "Gesture-Controlled Security Camera",
    "Intelligent AI Fleet Optimization", "Bluetooth-Enabled Vehicle Surveillance",
    "Real-Time AI Voice Alerts", "Car DVR with Radar Sensor", "Ultra-Compact AI Security Camera",
    "AI-Powered Number Plate Reader", "Truck Blind Spot Detection Camera",
    "AI-Powered Over Speed Detection", "Vehicle Footage Backup System", "Autonomous Drone Surveillance",
    "Smart Dashcam with AI Auto-Recording", "Emergency Alert GPS System",
    "AI-Based Seatbelt Compliance Checker", "Speed Limit Detection AI",
    "AI-Driven Pedestrian Avoidance System", "Driver Monitoring with Emotion Detection",
    "Multi-Channel Car DVR System", "AI-Powered Trailer Security System",
    "AI-Powered Tire Pressure Monitoring", "High-Resolution AI Parking Camera",
    "Dashcam with Automatic Roadside Assistance Alert", "AI-Based Vehicle Exit Warning System"
]

# A set of dynamic announcement templates
TEMPLATES = [
    "🔥 Exciting news! Our latest {product} is here! 🚀 Enhance safety & efficiency today!",
    "🚗 Introducing {product}! Designed for smarter, safer driving! 😎",
    "📢 The wait is over! The revolutionary {product} is now available. Get yours today! 🔥",
    "🚦 Safety first! Upgrade to our cutting-edge {product} for maximum protection! 🔒",
    "🌟 Experience next-gen vehicle security with {product}. Stay ahead with AxelGuard! 🚗",
    "🚀 Elevate your fleet’s safety with the all-new {product}. Smarter, safer roads await! 🌍",
    "💡 Your car deserves the best! Our new {product} is here to redefine vehicle security! 🚙",
    "⚡ Boost your vehicle’s intelligence with {product}. Future-proof your journey today! 🚗",
    "🛠️ Upgraded tech alert! {product} just got even better. Drive with confidence! 💪",
    "🚛 Fleet owners rejoice! Our advanced {product} is your best co-pilot on the road! 🏆"
]

def get_new_product_update():
    """
    Randomly selects a product from a list of 100+ options and returns a dynamic announcement.
    This function triggers about 1/3 of the time to simulate periodic product updates.
    """
    if random.choice([True, False, False]):  # ~33% chance to trigger an update
        selected_product = random.choice(PRODUCTS)
        announcement = random.choice(TEMPLATES).format(product=selected_product)
        return announcement
    else:
        return None

# -----------------------------------------------------------
# Content Generation: Generate tweet content via Groq API
# -----------------------------------------------------------
def generate_content(product_update=None):
    """
    Generate a dynamic, emoji-rich tweet for AxelGuard that highlights our
    innovative vehicle safety systems, product specifications, news, or other interesting details.
    The tweet MUST be under 280 characters, contain ONLY the tweet text, and be unique.
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GROQ_API_KEY}'
    }
    
    # Define a list of tweet prompt templates for variety
    PROMPTS = [
        "Write a unique, engaging tweet for AxelGuard in under 280 characters that highlights our innovative vehicle safety systems and products (Mobile DVRs, Dashcams, cameras, RFID, accessories, etc.). Use lots of emojis 😎🔥🚀. Only output the tweet text.",
        "Write a unique, engaging tweet for AxelGuard in under 280 characters that focuses on detailed product specifications and technical features. Emphasize innovative design and performance. Use lots of emojis 😎🔥🚀. Only output the tweet text.",
        "Write a unique, engaging tweet for AxelGuard in under 280 characters that shares recent news or an interesting fact about vehicle safety technology, product upgrades, or industry trends. Use lots of emojis 😎🔥🚀. Only output the tweet text.",
        "Write a unique, engaging tweet for AxelGuard in under 280 characters that is creative and random—mentioning product details, new innovations, or exciting news in the vehicle safety space. Use lots of emojis 😎🔥🚀. Only output the tweet text."
    ]
    
    chosen_prompt = random.choice(PROMPTS)
    
    # If there's a product update, prepend it to the prompt.
    if product_update:
        product_prompt = f"{product_update} "
    else:
        product_prompt = ""
    
    final_prompt = product_prompt + chosen_prompt
    
    payload = {
        'model': GROQ_MODEL,
        'messages': [
            {
                'role': 'user',
                'content': final_prompt
            }
        ]
    }
    
    try:
        print("Sending request to Groq API for tweet generation...")
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        print(f"Groq API response status: {response.status_code}")
        
        if response.status_code == 200:
            generated_text = response.json()['choices'][0]['message']['content']
            print("Generated tweet content from Groq API.")
            return generated_text
        else:
            print("Groq API error:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print("Exception during Groq API request:", e)
        return None

# -----------------------------------------
# Posting to Twitter using OAuth1 authentication
# -----------------------------------------
def post_to_twitter(content):
    """
    Post the sanitized tweet content to Twitter.
    """
    twitter_url = 'https://api.twitter.com/2/tweets'
    
    oauth = OAuth1Session(
        TWITTER_CONSUMER_KEY,
        client_secret=TWITTER_CONSUMER_SECRET,
        resource_owner_key=TWITTER_ACCESS_TOKEN,
        resource_owner_secret=TWITTER_ACCESS_TOKEN_SECRET
    )
    
    content = sanitize_content(content)
    content = truncate_content(content)
    
    tweet_data = {'text': content}
    
    try:
        print("Sending tweet to Twitter...")
        response = oauth.post(twitter_url, json=tweet_data)
        print(f"Twitter API response status: {response.status_code}")
        if response.status_code == 201:
            print("Tweet posted successfully!")
        else:
            print("Error posting tweet:", response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        print("Exception during Twitter post:", e)

# --------------------------------------------------
# Main function: Check for updates, generate and post tweet
# --------------------------------------------------
def generate_and_post():
    """
    Check for new product updates, generate a unique tweet using Groq,
    optionally append a relevant URL, and post the tweet to Twitter.
    """
    product_update = get_new_product_update()  # Check for a new product update event
    content = generate_content(product_update=product_update)
    if content:
        # Append a relevant URL if the tweet content mentions product keywords
        content = maybe_append_url(content)
        print("Final generated tweet content:")
        print(content)
        # Uncomment the next line to post the tweet to Twitter.
        post_to_twitter(content)
    else:
        print("No tweet generated.")

# -------------------------
# Scheduler: Run the job periodically
# -------------------------
schedule.every(180).minutes.do(generate_and_post)

if __name__ == "__main__":
    print(f"Scheduler started at {datetime.now()}")
    while True:
        schedule.run_pending()
        time.sleep(60)
