import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import pyttsx3

import os
import random
import string
import time

# constants
EXECUTABLE_PATH = "chromedriver.exe"
BRAVE_PATH = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
QUESTION_ELEMENT_CLASS = "Post "
QUESTION_TEXT_CLASS = "SQnoC3ObvgnGjWt90zD9Z _2INHSNB8V5eaWp4P0rY_mE"
COMMENT_ELEMENT_CLASS = "Comment "
COMMENT_TEXT_CLASS = "_292iotee39Lmt0MkQZ2hPV RichTextJSON-root"

# pyttsx3 converter
converter = pyttsx3.init()
converter.setProperty("rate", 225)

# save tts to a file
def save_tts(text, file):
    converter.save_to_file(text, file)
    converter.runAndWait()

# get posts from subreddit
def get_posts(
    subreddit,
    max_posts=5, # number of posts to scrape
    max_comments=7, # number of comments per video
    max_videos=1, # number of videos to create from one post
    WAIT_TIMEOUT=20 # number of seconds to wait for enough posts and comments to load
):
    
    # just in case, create screenshots folder
    try: os.mkdir("screenshots")
    except FileExistsError: pass

    # setup driver
    options = webdriver.ChromeOptions()
    options.binary_location = BRAVE_PATH
    options.executable_path = EXECUTABLE_PATH
    prefs = {"profile.default_content_setting_values.notifications": 2} # this disables the screen dimming thing
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--log-level=3")
    # options.add_argument("--headless")
    options.add_argument("--disable-logging")
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.reddit.com/r/{subreddit}/top/?t=day")
    driver.maximize_window()

    # wait until enough posts are loaded
    start_time = time.time()
    while len(driver.find_elements(By.CSS_SELECTOR, f"[class*='{QUESTION_ELEMENT_CLASS}']")) < max_posts:
        if time.time() - start_time >= WAIT_TIMEOUT: break

    # find post: titles and links
    posts = []
    for element in driver.find_elements(By.CSS_SELECTOR, f"[class*='{QUESTION_ELEMENT_CLASS}']"):

        # exit if limit reached
        if len(posts) == max_posts: break

        # ads and anomaly skipper
        try:
            text_element = element.find_element(By.XPATH, f".//a[@class='{QUESTION_TEXT_CLASS}']")
        except selenium.common.exceptions.WebDriverException: # this should skip ads
            continue

        # save screenshot and tts
        path = "screenshots/" + "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))
        driver.execute_script('arguments[0].scrollIntoView({block: "center"});', element) # prevent cutting off
        element.screenshot(path + ".png")
        save_tts(text_element.text, path + ".wav")

        # add the new element to posts
        new_element = {
            "title": text_element.text[:92],
            "link": text_element.get_attribute("href"),
            "comments": [],
            "thumbnail": path,
        }
        posts.append(new_element)
    
    # get top comments from posts
    for idx, post in enumerate(posts):

        # debug message
        print(f"[DEBUG] Scraping post: {post['title']} ({idx + 1} / {len(posts)})")

        # change webpage
        driver.get(post["link"])

        # wait until enough posts are loaded
        start_time = time.time()
        while len(driver.find_elements(By.CSS_SELECTOR, f"[class^='{COMMENT_ELEMENT_CLASS}']")) < max_videos * max_comments:
            if time.time() - start_time >= WAIT_TIMEOUT: break

        # screenshot and store each comment
        cur_comments = []
        for element in driver.find_elements(By.CSS_SELECTOR, f"[class^='{COMMENT_ELEMENT_CLASS}']"):

            # exit if limit reached
            if len(post["comments"]) == max_videos: break

            try:
                # get comment as text
                text_element = element.find_element(By.XPATH, f".//div[@class='{COMMENT_TEXT_CLASS}']")
                if not text_element.text:
                    continue

                # save screenshot and tts
                path = "screenshots/" + "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))
                driver.execute_script('arguments[0].scrollIntoView({block: "center"});', element) # prevent cutting off
                element.screenshot(path + ".png")
                save_tts(text_element.text, path + ".wav")

                # update cur comments
                cur_comments.append((
                    text_element.text,
                    path
                ))

                # update post
                if len(cur_comments) == max_comments:
                    post["comments"].append(cur_comments.copy())
                    cur_comments.clear()

            except selenium.common.exceptions.WebDriverException: # deleted posts or haywire posts are skipped
                pass

    return posts

if __name__ == "__main__":
    posts = get_posts("AskReddit", max_posts=2, max_videos=5)
    for post in posts:
        print(post["title"], len(post["comments"]))
        for comment in post["comments"]:
            print(len(comment))
            print("> " + comment[0][0])