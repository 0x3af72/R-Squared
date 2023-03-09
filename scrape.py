import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyttsx3
import validators

import re
import os
import random
import string
import time
from copy import copy

import printswitch
from printswitch import PRINTS

# constants
EXECUTABLE_PATH = "chromedriver.exe"
BRAVE_PATH = "drivers/brave.exe"
POST_ELEMENT_CLASS = "Post "
POST_TEXT_CLASS = "SQnoC3ObvgnGjWt90zD9Z _2INHSNB8V5eaWp4P0rY_mE"
POST_DESCRIPTION_CLASS = "_3xX726aBn29LDbsDtzr_6E _1Ap4F5maDtT1E1YuCiaO0r D3IL3FD0RFy_mkKLPwL4"
COMMENT_ELEMENT_CLASS = "Comment "
COMMENT_TEXT_CLASS = "_292iotee39Lmt0MkQZ2hPV RichTextJSON-root"
DROPDOWN_BUTTON_CLASS = "_10K5i7NW6qcm-UoCtpB3aK _1pA8z73SZ1olP5KMKFN4_Z _18X7KoiaLuKbuLqg4zE8BH _22SL37yETIW414yUiZj27w"
DARKMODE_BUTTON_CLASS = "_2e2g485kpErHhJQUiyvvC2 _1asGWL2_XadHoBuUlNArOq _3kUvbpMbR21zJBboDdBH7D"

# pyttsx3 converter
converter = pyttsx3.init()
converter.setProperty("rate", 225)

# save tts to a file
def save_tts(text, file, pause=True):
    converter.save_to_file(text, file)
    converter.runAndWait()

# whether to ignore a post
def to_ignore(element, ignore):
    for text in ignore:
        if text in element.text: return True
    return False

# filter out urls in string
def filter_urls(s):
    return " ".join(word if not validators.url(word) else "(url removed)" for word in re.split(f"[{string.whitespace}]", s))

# moving around the chromedriver file for neatness
def move_chromedriver_file(out):
    os.rename(*["drivers/chromedriver.exe", "chromedriver.exe"][::-1 if not out else 1])

# setup driver
def setup_driver(subreddit):

    # driver stuff
    move_chromedriver_file(True)
    options = webdriver.ChromeOptions()
    options.binary_location = BRAVE_PATH
    options.executable_path = EXECUTABLE_PATH
    prefs = {"profile.default_content_setting_values.notifications": 2} # this disables the screen dimming thing
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.reddit.com/r/{subreddit}/top/?t=day")
    driver.maximize_window()

    # dark mode
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//button[@class='{DROPDOWN_BUTTON_CLASS}']"))).click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//button[@class='{DARKMODE_BUTTON_CLASS}']"))).click()

    return driver

# get posts and comments
def get_posts_PTC(
    subreddit,
    max_posts=5, # number of posts to scrape
    max_comments=7, # number of comments per video
    max_videos=1, # number of videos to create from one post
    WAIT_TIMEOUT=20, ignore=[], logging=True,
):
    
    # set logging switch
    printswitch.switch.print = logging
    
    # just in case, create screenshots folder
    try: os.mkdir("screenshots")
    except FileExistsError: pass

    # setup driver
    driver = setup_driver(subreddit)

    # wait until enough posts are loaded
    start_time = time.time()
    post_elems = []
    while len(post_elems) < max_posts:
        post_elems = [
            element for element in
            driver.find_elements(By.CSS_SELECTOR, f"[class*='{POST_ELEMENT_CLASS}']")
            if not to_ignore(element, ignore)
        ]
        if time.time() - start_time >= WAIT_TIMEOUT: break

    # find post: titles and links
    posts = []
    for element in post_elems:

        # exit if limit reached
        if len(posts) == max_posts: break

        # ads and anomaly skipper
        try:
            text_element = element.find_element(By.XPATH, f".//a[@class='{POST_TEXT_CLASS}']")
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
        PRINTS(f"[DEBUG] Scraping post: {post['title']} ({idx + 1} / {len(posts)})")

        # change webpage
        driver.get(post["link"])

        # wait until enough comments are loaded
        start_time = time.time()
        comment_elems = []
        while len(comment_elems) < max_videos * max_comments:
            comment_elems = [
                element for element in
                driver.find_elements(By.CSS_SELECTOR, f"[class^='{COMMENT_ELEMENT_CLASS}']")
                if "level 1" in element.text # only get main posts
            ]
            if time.time() - start_time >= WAIT_TIMEOUT: break

        # screenshot and store each comment
        cur_comments = []
        for element in comment_elems:

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
                comment_text = filter_urls(text_element.text)
                save_tts(comment_text, path + ".wav")

                # update cur comments
                cur_comments.append((
                    comment_text,
                    path
                ))

                # update post
                if len(cur_comments) == max_comments:
                    post["comments"].append(cur_comments.copy())
                    cur_comments.clear()

            except selenium.common.exceptions.WebDriverException: # deleted posts or haywire posts are skipped
                pass

    move_chromedriver_file(False)
    return posts

# get posts and description from subreddit
def get_posts_PD(
    subreddit,
    max_posts=5, # number of posts to scrape
    CHUNKSIZE=75, # chunk up long descriptions by chunks of n words
    WAIT_TIMEOUT=20, ignore=[], logging=True,
):
    
    # set logging switch
    printswitch.switch.print = logging
    
    # just in case, create screenshots folder
    try: os.mkdir("screenshots")
    except FileExistsError: pass

    # setup driver
    driver = setup_driver(subreddit)

    # wait until enough posts are loaded
    start_time = time.time()
    post_elems = []
    while len(post_elems) < max_posts:
        post_elems = [
            element for element in
            driver.find_elements(By.CSS_SELECTOR, f"[class*='{POST_ELEMENT_CLASS}']")
            if not to_ignore(element, ignore)
        ]
        if time.time() - start_time >= WAIT_TIMEOUT: break

    # find post: titles and descriptions
    posts_to_visit = []
    for element in post_elems:

        # exit if limit reached
        if len(posts_to_visit) == max_posts: break

        # ads and anomaly skipper
        try:
            text_element = element.find_element(By.XPATH, f".//a[@class='{POST_TEXT_CLASS}']")
        except selenium.common.exceptions.WebDriverException: # this should skip ads
            continue

        # save screenshot and tts
        path = "screenshots/" + "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))
        driver.execute_script('arguments[0].scrollIntoView({block: "center"});', element) # prevent cutting off
        element.screenshot(path + ".png")
        save_tts(text_element.text, path + ".wav")

        posts_to_visit.append((text_element.text, text_element.get_attribute("href"), path))

    posts = []
    for title, link, thumbnail in posts_to_visit:

        # visit link
        driver.get(link)

        # get chunk text
        PRINTS(f"[DEBUG]: Getting post description: {title}")
        try:
            description_text = driver.find_element(By.XPATH, f"//div[@class='{POST_DESCRIPTION_CLASS}']").text
            if not description_text:
                PRINTS(f"[DEBUG]: POST NO DESCRIPTION, ABORTING.")
                return False # invalid post, subreddit might not work at all
            description_text = description_text.split(" ")
        except selenium.common.exceptions.NoSuchElementException:
            PRINTS(f"[DEBUG]: POST NO DESCRIPTION, ABORTING.")
            return False # same as above
        
        # chunking up + tts
        description_chunks = []
        while description_text:
            chunk = filter_urls(" ".join(description_text[:CHUNKSIZE]))
            path = "screenshots/" + "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))
            save_tts(chunk, path + ".wav", False)
            description_chunks.append((chunk, path))
            description_text = description_text[CHUNKSIZE:]

        # add the new element to posts
        new_element = {
            "title": title[:92],
            "description_chunks": description_chunks,
            "thumbnail": thumbnail,
        }
        posts.append(new_element)

    move_chromedriver_file(False)
    return posts

if __name__ == "__main__":
    # posts = get_posts_PTC("AskReddit", max_posts=2, max_videos=5)
    # for post in posts:
    #     PRINTS(post["title"], len(post["comments"]))
    #     for comment in post["comments"]:
    #         PRINTS(len(comment))
    #         PRINTS("> " + comment[0][0])
    posts = get_posts_PD("AmItheAsshole", max_posts=2)
    for post in posts:
        print(post["title"])
        print(post["description_chunks"])