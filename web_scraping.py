import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re
import pandas as pd

import tweepy
import http.client
import re
import json
import os

df = pd.DataFrame()
visited_urls = set()

active =[]
links = []
paragraphs = []
times = []
bases = []
images = []


def is_active_url(url):
    """
    Check if the URL is active by sending a HEAD request.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def find_all_links(url, soup):
    """
    Find all the hyperlinks in the current page.
    """
    links = set()
    for link in soup.find_all('a', href=True):
        full_url = urljoin(url, link['href'])
        if url in full_url:  # Only consider URLs in the same domain
            links.add(full_url)
    return links

def crawl_website(base_url, max_pages=100):
    """
    Crawl a website to count active pages.
    
    Parameters:
        base_url (str): The starting URL of the website to crawl.
        max_pages (int): The maximum number of pages to crawl.
    
    Returns:
        int: The count of active pages.
    """
    visited_urls = set()
    urls_to_visit = {base_url}
    active_pages_count = 0

    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop()
        
        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)

        try:
            response = requests.get(current_url, timeout=5)
            if response.status_code == 200:
                print(f"Active URL: {current_url}")
                active_pages_count += 1
                soup = BeautifulSoup(response.content, 'html.parser')
                links = find_all_links(current_url, soup)
                urls_to_visit.update(links - visited_urls)
            else:
                print(f"Inactive URL: {current_url} - Status Code: {response.status_code}")
        
        except requests.RequestException as e:
            print(f"Failed to fetch {current_url}: {e}")

        # Be polite to the server, avoid hammering it
        time.sleep(1)
    
    print(f"Total active pages: {active_pages_count}")
    return active_pages_count

def getPageTime(url):
    response = requests.get(url)
    html_content = response.text
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check for meta tags related to modification date
    last_modified = soup.find('meta', {'http-equiv': 'last-modified'})
    date_meta = soup.find('meta', {'name': 'date'})
    
    if last_modified:
        return last_modified.get('content')
    elif date_meta:
        return date_meta.get('content')
    else:
        return None

def extract_base_url(url):
    # Regular expression pattern for extracting base URL
    pattern = re.compile(r'^(https?:\/\/[^\/]+)')
    
    # Search for the pattern in the provided URL
    match = pattern.search(url)
    
    # Return the base URL if a match is found, otherwise None
    return match.group(1) if match else None

def getPageText(url):    
    response = requests.get(url)
    html_content = response.text
    
    # Step 2: Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Step 3: Remove Unwanted Tags
    # Find and remove <header>, <footer>, and <nav> tags
    for tag_name in ['header', 'footer', 'nav']:
        for element in soup.find_all(tag_name):
            element.decompose()  # Removes the tag and its content
    
    # Step 4: Extract <p> Tags
    # Find all <p> tags
    paragraphs = soup.find_all('p')
    
    return "\n".join([i.get_text(strip=True) for i in paragraphs])


def getImages(url):
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
    
        # Find all <img> tags on the page
        img_tags = soup.find_all('img')
    
        # Extract the URLs of the images
        img_urls = []
        for img in img_tags:
            img_url = img.get('src')
            # Handle relative URLs by converting them to absolute URLs
            img_url = urljoin(url, img_url)
            img_urls.append(img_url)
    
        # Print the collected image URLs
        print(f"Found {len(img_urls)} images:")
        return img_urls
    else:
        print(f"Failed to retrieve webpage. Status code: {response.status_code}")
        return []

def crawl_website(base_url, max_pages=100):
    
    global visited_urls

    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print(f"Active URL: {base_url}")
            soup = BeautifulSoup(response.content, 'html.parser')
            current_links = find_all_links(base_url, soup)
            visited_urls.add(base_url)
        else:
            print(f"Inactive URL: {base_url} - Status Code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to fetch {base_url}: {e}")

    for i in [ j for j in current_links if j not in visited_urls]:
        if(is_active_url(i)):
            paragraphs.append(getPageText(i))
            links.append(i)
            crawl_website(i)
            times.append(getPageTime(i))
            bases.append(extract_base_url(i))
            images.append(getImages(i))
            
def getTwitterTrends(woeid=23424863):
    consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_KEY")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN")

    trending_topics = api.get_place_trends(woeid)
    
def getPostComments(post_id=1552735248026411010):
    def extract_full_text(input_string):
        pattern = r'"full_text":\s*"([^"]+)"\s*,?'
        matches = re.findall(pattern, input_string)
        if matches:
            return matches
        else:
            return None
    conn = http.client.HTTPSConnection("twitter241.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "cb50110465msh7ab905f9be94fa7p1c6954jsn63ec422eb069",
        'x-rapidapi-host': "twitter241.p.rapidapi.com"
    }

    conn.request("GET", f"/comments?pid={post_id}&count=40&rankingMode=Relevance", headers=headers)

    res = conn.getresponse()
    data = str(res.read().decode("utf-8"))
    result = extract_full_text(data)
    return [i for i in result]
def getPostComments(post_id=1552735248026411010):
    def extract_full_text(input_string):
        pattern = r'"full_text":\s*"([^"]+)"\s*,?'
        matches = re.findall(pattern, input_string)
        if matches:
            return matches
        else:
            return None
    conn = http.client.HTTPSConnection("twitter241.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "cb50110465msh7ab905f9be94fa7p1c6954jsn63ec422eb069",
        'x-rapidapi-host': "twitter241.p.rapidapi.com"
    }

    conn.request("GET", f"/comments?pid={post_id}&count=400&rankingMode=Relevance", headers=headers)

    res = conn.getresponse()
    data = str(res.read().decode("utf-8"))
    result = extract_full_text(data)
    return [i for i in result]

    
def searchTopic(topic="Kenya"):
    def extract_full_text(input_string):
        pattern = r'"full_text":\s*"([^"]+)"\s*,?'
        matches = re.findall(pattern, input_string)
        if matches:
            return matches
        else:
            return None
    conn = http.client.HTTPSConnection("twitter241.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': "cb50110465msh7ab905f9be94fa7p1c6954jsn63ec422eb069",
        'x-rapidapi-host': "twitter241.p.rapidapi.com"
    }
    
    conn.request("GET", f"/search-v2?type=Top&count=50&query={topic}", headers=headers)
    
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    result = extract_full_text(data)
    return [i for i in result]

def getUserDetails(username=None):
    conn = http.client.HTTPSConnection("twitter241.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "cb50110465msh7ab905f9be94fa7p1c6954jsn63ec422eb069",
        'x-rapidapi-host': "twitter241.p.rapidapi.com"
    }
    
    conn.request("GET", "/user?username=MrBeast", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return json.loads(data.decode("utf-8"))['result']['data']['user']['result']

def getUserPosts(rest_id="2455740283"):
    def extract_full_text(input_string):
        pattern = r'"full_text":\s*"([^"]+)"\s*,?'
        pattern_id = r'"rest_id":\s*"([^"]+)"\s*,?'
        matches = re.findall(pattern, input_string)
        matchesId = re.findall(pattern_id, input_string)
        if matches or matchesId:
            return matches, matchesId
        else:
            return None
    conn = http.client.HTTPSConnection("twitter241.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': "cb50110465msh7ab905f9be94fa7p1c6954jsn63ec422eb069",
        'x-rapidapi-host': "twitter241.p.rapidapi.com"
    }
    
    conn.request("GET", f"/user-tweets?user={rest_id}&count=40", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    
    posts, ids = extract_full_text((data.decode("utf-8")))
    return posts, ids

def getLocationTwitter():
    conn = http.client.HTTPSConnection("twitter135.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "cb50110465msh7ab905f9be94fa7p1c6954jsn63ec422eb069",
        'x-rapidapi-host': "twitter135.p.rapidapi.com"
    }
    
    conn.request("GET", "/v1.1/Locations/", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return json.loads(data.decode("utf-8"))

def getLocationTrends(location_id="1706136829559624331"):
    conn = http.client.HTTPSConnection("twitter135.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "cb50110465msh7ab905f9be94fa7p1c6954jsn63ec422eb069",
        'x-rapidapi-host': "twitter135.p.rapidapi.com"
    }
    conn.request("GET", "/v1.1/Trends/?location_id=1706136829559624331&count=20", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return json.loads(data.decode("utf-8"))

def searchTwitter(topic="@KimaniKuria"):
    topic = topic.replace(" ","")
    def extract_full_text(input_string):
        pattern = r'"full_text":\s*"([^"]+)"\s*,?'
        matches = re.findall(pattern, input_string)
        if matches:
            return matches
        else:
            return None
    conn = http.client.HTTPSConnection("x-com2.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': "cb50110465msh7ab905f9be94fa7p1c6954jsn63ec422eb069",
        'x-rapidapi-host': "x-com2.p.rapidapi.com"
    }
    
    conn.request("GET", f"/Search/?q={topic}&count=20&tweet_search_mode=live&result_filter=user", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return extract_full_text(data.decode("utf-8"))

def getUser(username="tomitsuma"):
    conn = http.client.HTTPSConnection("x-com2.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': "cb50110465msh7ab905f9be94fa7p1c6954jsn63ec422eb069",
        'x-rapidapi-host': "x-com2.p.rapidapi.com"
    }
    
    conn.request("GET", f"/UserByScreenName/?username={username}", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return json.loads(data.decode("utf-8"))
    
def getUserTweetsReplies(user_id="44196397"):
    def extract_full_text(input_string):
        pattern = r'"full_text":\s*"([^"]+)"\s*,?'
        matches = re.findall(pattern, input_string)
        if matches:
            return matches
        else:
            return None
    conn = http.client.HTTPSConnection("x-com2.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': "cb50110465msh7ab905f9be94fa7p1c6954jsn63ec422eb069",
        'x-rapidapi-host': "x-com2.p.rapidapi.com"
    }
    
    conn.request("GET", f"/v2/UserTweetsAndReplies/?id={user_id}&count=40", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return extract_full_text(data.decode("utf-8"))


    
# Authenticate with Tweepy
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth)
    
    
start = time.time()
end = time.time()

