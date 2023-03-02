import videomaker
import scrape

subreddits_PTC = ["AskReddit", "ExplainLikeImFive", "TodayILearned"]
subreddits_PD = ["AmItheAsshole", "entitledparents"]

while True:
    
    # get subreddit index
    print(f"Available subreddits: {', '.join(subreddits_PTC)}")
    sub_idx = int(input("Enter subreddit index (0-indexed), or -1 to quit: "))
    if sub_idx == -1: break

    # get background video path
    bg_path = input("Enter background video path: ")

    # get inputs and then generate
    num_posts = int(input("Enter maximum number of posts: "))
    num_comments = int(input("Enter maximum number of comments per post (cuts off at 60s): "))
    videomaker.generate_reddit_videos_PTC(subreddit=subreddits_PTC[sub_idx], bg_path=bg_path, max_posts=num_posts, max_comments=num_comments)