import librosa
from moviepy.video.fx.all import crop, resize
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip, TextClip

import os
import random

import scrape
import printswitch
from printswitch import PRINTS

# filter out illegal filename characters
def filter_filename(name, illegal="\\/:?\"<>|"):
    return "".join(c for c in name if not c in illegal)

# post and comments video generator
def generate_reddit_videos_PTC(
    subreddit, bg_path, max_posts=5, max_comments=7, max_videos=1,
    output_width=786, output_height=1400, clear_screenshot_folder=True, logging=True, **kwargs,
):
    
    # set logging switch
    printswitch.switch.print = logging

    # just in case, create screenshots and output folder
    try: os.mkdir("screenshots")
    except FileExistsError: pass
    try: os.mkdir("output")
    except FileExistsError: pass
    
    # clear folder
    if clear_screenshot_folder:
        for file in os.listdir("screenshots"):
            try: os.remove("screenshots/" + file)
            except PermissionError: pass
    
    # width needs to be divisible by 2
    output_width += 1 * (output_width % 2 != 0)

    # call scrape
    PRINTS(f"[DEBUG][PTC MODE] Scraping subreddit: {subreddit} for up to {max_posts} posts, up to {max_comments} comments, up to {max_videos} videos")
    posts = scrape.get_posts_PTC(subreddit, max_posts, max_comments, max_videos, logging=logging, **kwargs)

    # create a video for each post
    for post in posts:
        
        unused_comments = [] # if comments not used, can use for next video
        for vid_idx in range(len(post["comments"])): # might be slow

            # get title clip and audio
            duration = librosa.get_duration(filename=post["thumbnail"] + ".wav")
            image = ImageClip(post["thumbnail"] + ".png").set_start(0).set_position("center").set_duration(duration)
            image = resize(image, width=output_width, height=int(output_width / image.w * image.h))
            audio = AudioFileClip(post["thumbnail"] + ".wav").set_start(0)
            comment_clips = [image,]
            comment_audios = [audio,]

            # get comment videos to add to compositeclip and total duration
            PRINTS(f"[DEBUG][{vid_idx}]: Creating comment video clips for post: {post['title']}")
            total_duration = duration
            new_unused = []
            for text, comment_path in sorted(
                post["comments"][vid_idx] + unused_comments,
                key=lambda comment: len(comment[0]), reverse=True # sort comments by size descending
            ):
                
                # check if exceeds
                duration = librosa.get_duration(filename=comment_path + ".wav")
                if total_duration + duration < 59:
                    # create clips
                    image = ImageClip(comment_path + ".png").set_start(total_duration).set_position("center").set_duration(duration)
                    image = resize(image, width=output_width, height=int(output_width / image.w * image.h))
                    audio = AudioFileClip(comment_path + ".wav").set_start(total_duration)

                    # update list and total duration
                    comment_clips.append(image); comment_audios.append(audio)
                    total_duration += duration

                else: # just add the comment to unused
                    if duration < 59: # if comment is super long just skip
                        new_unused.append((text, comment_path))

            # background video
            PRINTS(f"[DEBUG][{vid_idx}]: Adding background video")
            background_video = VideoFileClip(bg_path).set_audio(None)

            # resize background video to fit
            resize_scale = max(output_width / background_video.w, output_height / background_video.h)
            if resize_scale > 1:
                background_video = background_video.resize(resize_scale)
                PRINTS(f"[DEBUG][{vid_idx}]: Resizing to scale: {resize_scale}")

            # set background video subclip, background video needs to be longer than 60s to work, else bad things will happen
            start_time = random.randint(0, int(background_video.duration) - 60)
            background_video = background_video.subclip(start_time, start_time + total_duration)
            PRINTS(f"[DEBUG][{vid_idx}]: Background video subclip start: {start_time}s")

            # final clip creation
            PRINTS(f"[DEBUG][{vid_idx}]: Generating final clip")
            final_audio = CompositeAudioClip(comment_audios)
            final_clip = CompositeVideoClip([background_video, *comment_clips]).set_audio(final_audio)

            # crop final clip
            x1 = (final_clip.w - output_width) // 2; x2 = x1 + output_width
            y1 = (final_clip.h - output_height) // 2; y2 = y1 + output_height
            final_clip = crop(final_clip, x1=x1, y1=y1, x2=x2, y2=y2)

            # write output
            try:
                final_clip.write_videofile(
                    "output/" + f"({vid_idx + 1}) " + filter_filename(post["title"]) + ".mp4",
                    temp_audiofile="output/temp-audio.mp3",
                    verbose=False, logger=None, fps=30, codec="libx264",
                    ffmpeg_params=["-vf", "format=yuv420p"],
                    threads=4,
                )
                print(f"[DEBUG][{vid_idx}]: DONE!")
            except OSError: pass # winerror 6 thrown for no reason sometimes

    return True

# post and description video generator
def generate_reddit_videos_PD(
    subreddit, bg_path, max_posts=5,
    output_width=786, output_height=1400, clear_screenshot_folder=True, logging=True, **kwargs,
):
    
    # set logging switch
    printswitch.switch.print = logging

    # just in case, create screenshots and output folder
    try: os.mkdir("screenshots")
    except FileExistsError: pass
    try: os.mkdir("output")
    except FileExistsError: pass
    
    # clear folder
    if clear_screenshot_folder:
        for file in os.listdir("screenshots"):
            try: os.remove("screenshots/" + file)
            except PermissionError: pass
    
    # width needs to be divisible by 2
    output_width += 1 * (output_width % 2 != 0)

    # call scrape
    PRINTS(f"[DEBUG][PD MODE]: Scraping subreddit: {subreddit} for up to {max_posts} posts")
    posts = scrape.get_posts_PD(subreddit, max_posts, logging=logging, **kwargs)
    if not posts:
        PRINTS("[DEBUG]: No posts found.")
        return False
    
    for post in posts:

        # get title clip and audio
        duration = librosa.get_duration(filename=post["thumbnail"] + ".wav")
        image = ImageClip(post["thumbnail"] + ".png").set_start(0).set_position("center").set_duration(duration)
        image = resize(image, width=output_width, height=int(output_width / image.w * image.h))
        audio = AudioFileClip(post["thumbnail"] + ".wav").set_start(0)
        post_clips = [image,]
        post_audios = [audio,]

        # create clips for description
        print(f"[DEBUG]: Creating description video clips for post: {post['title']}")
        total_duration = duration
        for chunk, chunk_path in post["description_chunks"]:

            # stop when length exceeds already, this might cut off some part of the final video
            if total_duration > 59: break

            # create textclip and get audio
            duration = librosa.get_duration(filename=chunk_path + ".wav")
            audio = AudioFileClip(chunk_path + ".wav").set_start(total_duration)
            text = TextClip(chunk, fontsize=10, color="black").set_start(total_duration).set_pos("center").set_duration(duration)

            # update list and total duration
            post_clips.append(text); post_audios.append(audio)
            total_duration += duration

        # background video
        PRINTS(f"[DEBUG]: Adding background video")
        background_video = VideoFileClip(bg_path).set_audio(None)

        # resize background video to fit
        resize_scale = max(output_width / background_video.w, output_height / background_video.h)
        if resize_scale > 1:
            background_video = background_video.resize(resize_scale)
            PRINTS(f"[DEBUG]: Resizing to scale: {resize_scale}")

        # set background video subclip, background video needs to be longer than 60s to work, else bad things will happen
        start_time = random.randint(0, int(background_video.duration) - 60)
        background_video = background_video.subclip(start_time, start_time + total_duration)
        PRINTS(f"[DEBUG]: Background video subclip start: {start_time}s")

        # final clip creation
        PRINTS(f"[DEBUG]: Generating final clip")
        final_audio = CompositeAudioClip(post_audios)
        final_clip = CompositeVideoClip([background_video, *post_clips]).set_audio(final_audio)

        # crop final clip
        x1 = (final_clip.w - output_width) // 2; x2 = x1 + output_width
        y1 = (final_clip.h - output_height) // 2; y2 = y1 + output_height
        final_clip = crop(final_clip, x1=x1, y1=y1, x2=x2, y2=y2)

        # write output
        try:
            final_clip.write_videofile(
                "output/" + filter_filename(post["title"]) + ".mp4",
                temp_audiofile="output/temp-audio.mp3",
                verbose=False, logger=None, fps=30, codec="libx264",
                ffmpeg_params=["-vf", "format=yuv420p"],
                threads=4,
            )
            print(f"[DEBUG]: DONE!")
        except OSError: pass # winerror 6 thrown for no reason sometimes

    return True

if __name__ == "__main__":
    # generate_reddit_videos_PTC(
    #     subreddit="AskReddit",
    #     max_posts=5, max_comments=10, max_videos=3, bg_path="background/cake.mp4",
    #     logging=True
    # )
    generate_reddit_videos_PD(
        subreddit="AmItheAsshole",
        bg_path="background/minecraft.mp4",
        max_posts=1,
        logging=True
    )