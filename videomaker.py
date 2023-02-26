import librosa
from moviepy.video.fx.all import crop, resize
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip

import os
import scrape
import random

# filter out illegal filename characters
def filter_filename(name, illegal="\\/:?\"<>|"):
    return "".join(c for c in name if not c in illegal)

def generate_reddit_videos(
    subreddit="AskReddit", max_posts=5, max_comments=7, max_videos=1, bg_path="background/minecraft.mp4",
    output_width=786, output_height=1400, clear_folder=True, **kwargs
):
    # just in case, create screenshots and output folder
    try:
        os.mkdir("screenshots")
        os.mkdir("output")
    except FileExistsError: pass
    
    # clear folder
    if clear_folder:
        for file in os.listdir("screenshots"):
            try: os.remove("screenshots/" + file)
            except PermissionError: pass
    
    # width needs to be divisible by 2
    output_width += 1 * (output_width % 2 != 0)

    # call scrape
    print(f"[DEBUG] Scraping subreddit: {subreddit} for up to {max_posts} posts, up to {max_comments} comments, up to {max_videos} videos")
    posts = scrape.get_posts(subreddit, max_posts, max_comments, max_videos, **kwargs)

    # create a video for each post
    for post in posts:

        for vid_idx in range(len(post["comments"])): # might be slow

            # get title clip and audio
            duration = librosa.get_duration(filename=post["thumbnail"] + ".wav")
            image = ImageClip(post["thumbnail"] + ".png").set_start(0).set_position("center").set_duration(duration)
            image = resize(image, width=output_width, height=int(output_width / image.w * image.h))
            audio = AudioFileClip(post["thumbnail"] + ".wav").set_start(0)
            comment_clips = [image,]
            comment_audios = [audio,]

            # get comment videos to add to compositeclip and total duration
            print(f"[DEBUG][{vid_idx}]: Creating comment video clips for post: {post['title']}")
            total_duration = duration
            for text, comment_path in post["comments"][vid_idx]:
                # create clips
                duration = librosa.get_duration(filename=comment_path + ".wav")
                image = ImageClip(comment_path + ".png").set_start(total_duration).set_position("center").set_duration(duration)
                image = resize(image, width=output_width, height=int(output_width / image.w * image.h))
                audio = AudioFileClip(comment_path + ".wav").set_start(total_duration)

                # update list and total duration
                comment_clips.append(image); comment_audios.append(audio)
                total_duration += duration

            # background video
            print(f"[DEBUG][{vid_idx}]: Adding background video")
            start_time = random.randint(0, 4200) # start time: 0s - 1h10min
            background_video = VideoFileClip(bg_path).subclip(start_time, start_time + total_duration).set_audio(None).resize(2)

            # final clip creation
            print(f"[DEBUG][{vid_idx}]: Generating final clip")
            final_audio = CompositeAudioClip(comment_audios)
            final_clip = CompositeVideoClip([background_video, *comment_clips]).set_audio(final_audio).subclip(0, 58)

            # crop final clip
            x1 = (final_clip.w - output_width) // 2; x2 = x1 + output_width
            y1 = (final_clip.h - output_height) // 2; y2 = y1 + output_height
            final_clip = crop(final_clip, x1=x1, y1=y1, x2=x2, y2=y2)

            # write output
            final_clip.write_videofile(
                "output/" + f"({vid_idx + 1}) " + filter_filename(post["title"]) + ".mp4",
                temp_audiofile="output/temp-audio.mp3",
                verbose=False, logger=None, fps=30, codec="libx264",
                ffmpeg_params=["-vf", "format=yuv420p"]
            )

if __name__ == "__main__":
    # need to put more comments or else will have black screen if comments are too short
    generate_reddit_videos(max_posts=2, max_comments=10, max_videos=3)