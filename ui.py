import videomaker
import scrape

subreddits = ["AskReddit", "ExplainLikeImFive", "TodayILearned"]

while True:
    
    # get subreddit index
    print(f"Available subreddits: {', '.join(subreddits)}")
    sub_idx = int(input("Enter subreddit index (0-indexed), or -1 to quit: "))
    if sub_idx == -1: break

    # get inputs and then generate
    num_posts = int(input("Enter maximum number of posts: "))
    num_comments = int(input("Enter maximum number of comments per post (cuts off at 60s): "))
    videomaker.generate_reddit_videos(subreddit=subreddits[sub_idx], max_posts=num_posts, max_comments=num_comments)