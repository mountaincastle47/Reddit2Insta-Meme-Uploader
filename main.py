# If you are reading this. I am so so so sorry that you have to read this piece of shit, buggy, not orginized code.

import os
import json
from datetime import datetime
import time
from instabot import bot
import praw
from dotenv import load_dotenv
# from sidspackage import ColorPrint
import wget
from datetime import datetime
import shutil

load_dotenv()

# cp = ColorPrint() # Prints text with colors - Theres better libraries


def log(message:str) -> None:
    """
    This function takes a string and logs it to a file

    Args:
        `message (str)`: This is the string that will be logged to the file

    Returns:
        `None`: This function returns nothing

    """
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")

    with open('log.txt', 'a') as f:
        f.write('\n')
        f.write(f"{current_time} | {message}")


def deletecookies():
    """
    This function is used to delete the autogenerated config and log files that are made by the instabot module

    Returns:
        `None`: This function doesn't return anything
    """
    try:
        shutil.rmtree("config") # Delete Config Folder
        # cp.print("Cookies Eaten Successfuly.", color="yellow")
        log("Cookies Eaten Successfuly.")
    except Exception as e:
        # cp.print("Cookies Deletion Failed.", color="red")
        log(f"Cookies Deletion Failed. {e}")


def reddit_client():
    """
    This function creates an instance of `praw.Reddit` which will be used to get the memes

    Returns:
        `praw.Reddit`: This returns a client object which will be used to download the memes
    """
    client = praw.Reddit( # Client ID and Client Secret are bot in the .env file
        client_id=os.environ['CLIENT_ID'], 
        client_secret=os.environ['CLIENT_SECRET'],
        user_agent="memes-fastapi"
    )
    return client


def is_image(post):
    """
    This function checks weather a post is an image or not because you cant upload links to insta, It must be a image.

    Args:
        `post (praw.models.Submission)`: This will be checks if it has a post hint of true or not

    Returns:
        `Boolean`: If post is image it retirns True 
            else it will return False
    """
    try:
        return post.post_hint == "image"
    except AttributeError:
        return False


def get_img_url(client: praw.Reddit, subreddits: list, limit: int):
    """
    This function looks through the top memes of reddit and returns info about them in a dictionary

    Args:
        `client (praw.Reddit)`: This is the client, It will be used to authenticate you and to look thoough reddit
        `subreddits (List[str])`: This is a list of subreddits the bot will get memes from
        `limit (int)`: This is the limit on how memes the bot will look for

    Returns:
        `List[ Dict[str : str] ]`: This will return a list of dictionaries with post information. This will be used to download the image and caption the post properly
    """
    memes = []
    for subreddit in subreddits:
        hot_memes = client.subreddit(subreddit).hot(limit=limit) # Returns list of hot memes

        for post in hot_memes:
            if is_image(post): # Checks if post is image
                data = {
                    "url": post.url,
                    "author": post.author.name,
                    "title": post.title
                }
                memes.append(data)

    return memes 


log("----------START----------")
# cp.print("----------START----------", color="blue")

start_time = datetime.now() # Records when this bot starts

# Notification for mac, If youre not on mac delete this line
os.system("""osascript -e 'display notification "Starting Meme Uploads" with title "Reddit 2 Insta"'""")
deletecookies()

# Create reddit client
client = reddit_client()

# get 100 image urls from each of these subreddits
rpsnlist = ['memes', 'dankmemes']
memes = get_img_url(client=client, subreddits=rpsnlist, limit=100)

log("Downloaded urls")
# cp.print("Downloaded urls", color="purple")

# Make insta bot
bot = bot.Bot()

# Login
bot.login( # Both values are put in the .env file
    username=os.environ['insta_user'],
    password=os.environ['insta_pass']
)

log("Logged In Successfully!")
# cp.print("Logged In Successfully!", color="green")

hashtags = "#memes #funny #reddit #dankmemes #lol #memesdaily #humor #dank #meme #followorgetrickrolled #image #random #images"

old_count, new_count, gif_count = 0, 0, 0 # These variables count the old, new and gifs in the list returned by get_img_url()

for meme in memes:
    with open('urls.json', 'r') as f:
        data = json.load(f)

    post_url = meme["url"]
    post_author = meme["author"]
    post_title = meme["title"]

    fileext = post_url[-4] + post_url[-3] + post_url[-2] + post_url[-1] # gets the file extension of the image, eg: .png
    if fileext == '.gif':
        gif_count += 1
        continue

    if post_url in data:
        old_count += 1
        continue

    else:
        data.append(post_url)
        new_count += 1
        with open("urls.json", 'w') as f:
            json.dump(data, f, indent=4)

    filename = wget.download(url=str(post_url), out="upload") # Download Meme
    time.sleep(2)
    try:
        bot.upload_photo(filename, caption=f"{post_title}\n\n[Via Reddit] - (Author: u/{post_author})\n\n[Hashtags]\n{hashtags}")
        time.sleep(2)
    except Exception as e:
        log(f"Error: {e}")
    os.remove(filename)


# Stats:

log(f"{new_count}/{len(rpsnlist)*100} new urls")
log(f"{old_count}/{len(rpsnlist)*100} old urls")
log(f"{gif_count}/{len(rpsnlist)*100} gifs")

# cp.print(f"{new_count}/{len(rpsnlist)*100} new urls", color="cyan")
# cp.print(f"{old_count}/{len(rpsnlist)*100} old urls", color="cyan")
# cp.print(f"{gif_count}/{len(rpsnlist)*100} gifs", color="cyan")

deletecookies()

end_time = datetime.now() # Records the time when the bot finished
total_time = int((end_time - start_time).total_seconds()) # The total time the bot took

# Notification for mac, If youre not on mac delete this line
os.system(f"""osascript -e 'display notification "Finished in {total_time/60}" with title "Reddit 2 Insta"'""")

# cp.print(f"Finished in {total_time}s", color="green")
# cp.print("-----------END-----------", color="red")

log(f"Finished in {total_time}s")
log("-----------END-----------")
