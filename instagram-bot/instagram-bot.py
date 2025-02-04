from instabot import Bot
from qa_bot import get_answer
import re
import time
import argparse
import os
from tqdm import tqdm

# Function to check if a comment is a question
def is_question(comment_text):
    return re.search(r"\?$", comment_text.strip()) is not None

# Function to process comments for a given post
def process_comments(bot, shortcode):
    post_link = f"https://www.instagram.com/p/{shortcode}/"
    media_id = bot.get_media_id_from_link(post_link)
    comments = bot.get_media_comments(media_id)
    
    print(f"Processing comments for {post_link}")
    
    commented_users = []
    for comment in tqdm(comments[:5]):  # Process only the first 10 comments per post
        replied = False
        parent_comment_id = comment["pk"]
        user_id = comment["user"]["pk"]
        commenter = comment["user"]["username"]
        text = comment["text"]
        bot.logger.info(f"Checking comment from `{commenter}`")
        try:
            bot.logger.info(f"Comment text: `{text}`")
        except Exception as e:
            bot.logger.error(f"{e}")
        
        # To save time, because you can't reply to yourself
        if str(user_id) == bot.user_id:
            bot.logger.error("You can't reply to yourself")
            continue
        if user_id in commented_users:
            bot.logger.info("You already replied to this user")
            continue
        for _comment in comments:
            if _comment["type"] == 2 and str(_comment["user"]["pk"]) == bot.user_id and _comment["text"].split(" ")[0][1:] == commenter:
                bot.logger.info("You already replied to this user.")
                replied = True
                break
        if replied:
            continue
        answer = get_answer()
        comment_txt = f"@{commenter} {answer}"
        bot.logger.info(f"Going to reply to `{commenter}`")
        if bot.reply_to_comment(media_id, comment_txt, parent_comment_id):
            bot.logger.info("Replied to comment.")
            commented_users.append(user_id)

# Function to run the bot in a loop
def run_bot(bot, shortcodes):
    try:
        for _ in range(10):
            for shortcode in shortcodes:
                process_comments(bot, shortcode)
            
            print("Waiting for 60 seconds before next iteration...")
            time.sleep(60)  # Sleep to avoid hitting rate limits
    except KeyboardInterrupt:
        print("\n[!] Keyboard Interrupt detected. Logging out...")
    finally:
        bot.logout()
        print("Bot logged out. Exiting.")

# Command-line argument parser
def parse_arguments():
    parser = argparse.ArgumentParser(description="Instagram Comment Bot")
    parser.add_argument("-u", type=str, required=True, help="Username")
    parser.add_argument("-p", type=str, required=True, help="Password")
    parser.add_argument("-proxy", type=str, help="Proxy")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Initialize bot
    bot = Bot()
    try:
        bot.login(username=args.u, password=args.p, proxy=args.proxy)
        if not bot.api.is_logged_in:
            print("Login failed. Exiting...")
            bot.logout()
            exit()
        print("Login Success.")
    except Exception as e:
        print(f"Login Failed: {e}")
        exit()
    
    # Load shortcodes from file
    if not os.path.exists(args.comments_file):
        print(f"Can't find file: {args.comments_file}")
        exit()
    
    with open(args.comments_file, "r") as f:
        shortcodes = [line.strip() for line in f.readlines()]
    
    print(f"Posts: {shortcodes}")
    
    run_bot(bot, shortcodes)
