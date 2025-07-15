import praw
import openai
import os
from dotenv import load_dotenv
import re
import sys

# --- SETUP: Load Environment Variables ---
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# --- Helper Functions ---
def extract_username(profile_url):
    """
    Extracts the Reddit username from a given profile URL.
    """
    match = re.search(r'reddit\.com\/user\/([^\/]+)', profile_url)
    return match.group(1) if match else None

def get_user_data(username, limit=50):
    """
    Fetches a specified limit of posts and comments for a given Reddit username.
    Includes permalinks for better citation.
    """
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
        print("Error: Reddit API credentials not found in environment variables. Please set them in your .env file.")
        sys.exit(1)

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    redditor = reddit.redditor(username)

    posts, comments = [], []

    print(f"Attempting to fetch data for u/{username}...")
    try:
        # Fetch submissions (posts)
        for submission in redditor.submissions.new(limit=limit):
            posts.append({
                "id": submission.id,
                "url": f"https://www.reddit.com{submission.permalink}", # Full permalink
                "title": submission.title,
                "selftext": submission.selftext if submission.is_self else "[Link Post]"
            })
        print(f"Fetched {len(posts)} posts.")

        # Fetch comments
        for comment in redditor.comments.new(limit=limit):
            comments.append({
                "id": comment.id,
                "url": f"https://www.reddit.com{comment.permalink}", # Full permalink
                "body": comment.body
            })
        print(f"Fetched {len(comments)} comments.")

    except Exception as e:
        print(f"An error occurred while fetching Reddit data: {e}")
        print("This might be due to an invalid username, API rate limits, or incorrect credentials.")
        return [], [] # Return empty lists on error

    return posts, comments

def generate_persona(posts, comments):
    """
    Generates a user persona using OpenAI's GPT-3.5-turbo, citing sources.
    """
    if not OPENAI_API_KEY:
        print("Error: OpenAI API key not found in environment variables. Please set it in your .env file.")
        sys.exit(1)

    # Construct the prompt with specific instructions for citation
    prompt = """Based on the following Reddit posts and comments, generate a detailed user persona.
    The persona should include categories such as:
    - **Interests**: What are their hobbies, passions, and topics they engage with?
    - **Values**: What principles or beliefs seem important to them?
    - **Tone/Communication Style**: How do they typically express themselves (e.g., formal, casual, humorous, sarcastic, critical)?
    - **Personality Traits**: What adjectives describe their general demeanor (e.g., empathetic, analytical, cynical, enthusiastic)?
    - **Potential Political Views**: Are there any indications of political leanings or social stances?

    For EACH characteristic identified, you MUST cite the exact Reddit post or comment content that directly supports your inference.
    Cite by including the full text of the supporting content, clearly marked with its type ([POST] or [COMMENT]) and its unique URL.

    Example of desired output format:
    **Interests:**
    - Enjoys video games, especially RPGs. [Cite: [POST] URL: https://www.reddit.com/r/gaming/comments/... Title: My favorite RPGs Body: I spend hours playing The Witcher 3 and Elden Ring...]
    - Has a strong interest in technology and AI. [Cite: [COMMENT] URL: https://www.reddit.com/r/technology/comments/... Body: AI advancements are truly fascinating, especially in natural language processing.]

    **Values:**
    - Values intellectual honesty and critical thinking. [Cite: [COMMENT] URL: https://www.reddit.com/r/science/comments/... Body: It's important to base opinions on scientific evidence, not just anecdotal experiences.]

    --- Reddit User Data for Analysis ---
    """

    content_for_llm = ""
    for p in posts:
        # Include URL for precise citation
        content_for_llm += (
            f"[POST] URL: {p['url']}\n"
            f"Title: {p['title']}\n"
            f"Body: {p['selftext']}\n\n"
        )
    for c in comments:
        # Include URL for precise citation
        content_for_llm += (
            f"[COMMENT] URL: {c['url']}\n"
            f"Body: {c['body']}\n\n"
        )

    # Truncate content if it's too long, but be mindful of losing context.
    # A more advanced solution might involve summarization or chunking.
    # 15000 characters is a rough estimate for GPT-3.5-turbo's context window.
    # Always keep in mind the token limit which is around 16k tokens for gpt-3.5-turbo-16k.
    # Character count doesn't directly map to tokens, but 15000 chars is a safe upper bound for illustrative purposes.
    max_input_length = 15000
    if len(content_for_llm) > max_input_length:
        print(f"Warning: Reddit data truncated from {len(content_for_llm)} to {max_input_length} characters to fit LLM context.")
        content_for_llm = content_for_llm[:max_input_length]

    full_prompt = prompt + content_for_llm

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # You can try "gpt-4" if you have access for better results
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7, # Controls creativity (0.0-1.0)
            max_tokens=1500, # Max tokens for the persona output
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response['choices'][0]['message']['content']
    except openai.error.OpenAIError as e:
        print(f"An error occurred with the OpenAI API: {e}")
        print("Please check your API key, subscription status, and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during persona generation: {e}")
        sys.exit(1)


def save_persona(username, persona_text):
    """
    Saves the generated persona to a text file.
    """
    filename = f"{username}_persona.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(persona_text)
        print(f"Persona successfully saved to {filename}")
    except IOError as e:
        print(f"Error saving persona to file {filename}: {e}")
        sys.exit(1)

# --- Main Execution Flow ---
def main():
    """
    Main function to run the Reddit User Persona Generator.
    """
    print("--- Reddit User Persona Generator ---")
    url = input("Enter Reddit profile URL (e.g., https://www.reddit.com/user/kojied/): ").strip()
    username = extract_username(url)

    if not username:
        print("Invalid Reddit URL. Please ensure it's in the format https://www.reddit.com/user/username/")
        sys.exit(1)

    print(f"\n--- Processing u/{username} ---")
    posts, comments = get_user_data(username)

    if not posts and not comments:
        print(f"No posts or comments found for u/{username} or an error occurred during fetching. Cannot generate persona.")
        sys.exit(0) # Exit gracefully if no data

    print("\n--- Generating User Persona (This may take a moment) ---")
    persona = generate_persona(posts, comments)

    if persona:
        save_persona(username, persona)
    else:
        print("Failed to generate persona.")

if __name__ == "__main__":
    main()