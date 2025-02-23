from tweety.types.twDataTypes import Excel
from tweety.utils import iterable_to_string
import json, datetime
from collections import deque
import pandas as pd

def get_names_from_excel(file_path):
    """
    Extracts names from the first column of an Excel file.

    :param file_path: Path to the Excel file.
    :return: List of names from the first column.
    """
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)

        # Extract the first column
        names = df.iloc[:, 0].dropna().tolist()

        return names
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def which_AKP(text):
    excel_file = "docs/AKP_actors.xlsx"
    names = get_names_from_excel(excel_file)
    for name in names:
        if name in text:
            return name
    return "[]"

class MyExcel(Excel):
    def _write_tweet(self, tweet):
        # all_dict_keys(['id', 'created_on', 'date', 'author', 'is_retweet', 'retweeted_tweet', 'rich_text', 'article', 'text', 'tweet_body', 'is_quoted', 'quoted_tweet', 'is_reply', 'is_sensitive', 'reply_counts', 'quote_counts', 'replied_to', 'bookmark_count', 'vibe', 'views', 'language', 'likes', 'place', 'retweet_counts', 'source', 'audio_space_id', 'is_space', 'voice_info', 'media', 'pool', 'user_mentions', 'urls', 'has_moderated_replies', 'hashtags', 'symbols', 'community_note', 'community', 'url', 'edit_control', 'has_newer_version', 'broadcast', 'threads', 'is_liked', 'is_retweeted', 'can_reply', 'comments'])
        self.worksheet[f'A{self.max_row + 1}'] = self.max_row
        self.worksheet[f'B{self.max_row + 1}'] = tweet.date.replace(tzinfo=None)
        self.worksheet[f'C{self.max_row + 1}'] = tweet.author.name
        self.worksheet[f'D{self.max_row + 1}'] = tweet.id
        self.worksheet[f'E{self.max_row + 1}'] = tweet.text
        self.worksheet[f'F{self.max_row + 1}'] = tweet.likes
        self.worksheet[f'G{self.max_row + 1}'] = tweet.retweet_counts
        self.worksheet[f'H{self.max_row + 1}'] = tweet.views
        self.worksheet[f'I{self.max_row + 1}'] = tweet.bookmark_count
        self.worksheet[f'J{self.max_row + 1}'] = tweet.author.followers_count
        self.worksheet[f'K{self.max_row + 1}'] = len(tweet.user_mentions)
        self.worksheet[f'L{self.max_row + 1}'] = tweet.url
        self.worksheet[f'M{self.max_row + 1}'] = tweet.source
        self.worksheet[f'N{self.max_row + 1}'] = iterable_to_string(tweet.media, ",", "direct_url")
        self.worksheet[f'O{self.max_row + 1}'] = iterable_to_string(tweet.user_mentions, ",", "screen_name")
        self.worksheet[f'P{self.max_row + 1}'] = iterable_to_string(tweet.urls, ",", "expanded_url")
        self.worksheet[f'R{self.max_row + 1}'] = iterable_to_string(tweet.hashtags, ",", "text")
        self.worksheet[f'S{self.max_row + 1}'] = which_AKP(tweet.text)
        self.max_row += 1

    def _set_headers(self):
        for index, value in enumerate(['#', 'Date', 'Author Name', 'Tweet ID', 'Text', 'Likes',
                                       'Retweet Count', 'Views Count', 'Bookmark Count', 'Authors Followers Count',
                                       'Mention Count', 'Tweet URL', 'Source', 'Medias', 'User Mentions', 'URLs',
                                       'Hashtags'],
                                      start=1):
            self.worksheet.cell(row=1, column=index).value = value


def extract_user_data(user):
    return {
        "ID": user.id,
        "Username": user.username,
        "Name": user.name,
        "Bio": user.bio,
        "Location": user.location,
        "Followers Count": user.followers_count,
        "Following Count": user.friends_count,
        "Favourites Count": user.favourites_count,
        "Friends Count": user.friends_count,
        "Statuses Count": user.statuses_count,
        "Verified": user.verified,
        "Profile URL": user.profile_url,
        "Created At": user.created_at,
        "Birthdate": user.birth_date,
        "Profile Banner URL": user.profile_banner_url,
        "Profile Image URL": user.profile_image_url_https,
        "Fast Followers Count": user.fast_followers_count,
        "Listed Count": user.listed_count,
        "Media Count": user.media_count,
        "AKP_list": user.is_akp_list,
    }


def datetime_converter(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def save_user_to_json(json_path, user):
    file_path = json_path
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(extract_user_data(user), json_file, ensure_ascii=False, indent=4, default=datetime_converter)
    print("Veriler başarıyla dosyasına kaydedildi.")

# JSON loader function for accounts
def load_accounts_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if not isinstance(data, list) or not all(
                    isinstance(account, list) and len(account) == 2 for account in data):
                raise ValueError("JSON data must be a list of [username, password] pairs.")
            return deque(data)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return deque()
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{file_path}'. Ensure the file is properly formatted.")
        return deque()
    except Exception as e:
        print(f"Error: {e}")
        return deque()
