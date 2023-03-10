import videomaker
import scrape

subreddits_PTC = ["AskReddit", "ExplainLikeImFive", "TodayILearned"]
subreddits_PD = ["AmItheAsshole", "entitledparents"]

while True:

    # get mode: PTC or PD
    mode = input("Enter mode (without brackets): (0) Post and comments, (1) Post and description: ")
    
    # get subreddit index
    to_show = subreddits_PTC if mode == "0" else subreddits_PD
    print(f"Available subreddits: {', '.join(to_show)}")
    sub_idx = int(input("Enter subreddit index (0-indexed), or -1 to quit: "))
    if sub_idx == -1: break

    # get background video path
    bg_path = input("Enter background video path: ")

    # get inputs and then generate
    num_posts = int(input("Enter maximum number of posts: "))
    if mode == "0":
        num_videos = int(input("Enter maximum number of videos to create per post: "))
        num_comments = int(input("Enter maximum number of comments per video (cuts off at 60s): "))
        videomaker.generate_reddit_videos_PTC(
            subreddit=subreddits_PTC[sub_idx],
            bg_path=bg_path,
            max_posts=num_posts,
            max_comments=num_comments,
            max_videos = num_videos,
        )
    else:
        videomaker.generate_reddit_videos_PD(
            subreddit=subreddits_PD[sub_idx],
            bg_path=bg_path,
            max_posts=num_posts,
        )