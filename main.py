import asyncio, time, os
from helper import MyExcel, load_accounts_from_json
import pandas as pd
from tweety import TwitterAsync
app = TwitterAsync("session")

# Load accounts dynamically from JSON file
accounts_file = "accounts.json"
accounts = load_accounts_from_json(accounts_file)
max_attempts = len(accounts)

def date_range_pandas(start_date, end_date):
    dates = pd.date_range(start=start_date, end=end_date).tolist()
    return dates

def list_exported_xlsx_files(date_start):
    # Belirtilen dizindeki tüm dosyaları ve uzantısını kontrol et
    xlsx_files = [f for f in os.listdir("docs") if f.endswith('.xlsx')]
    try:
        last = xlsx_files.pop().split(".")[0].split("_")[1]
        last = pd.to_datetime(last)
        if last == pd.to_datetime(date_start):
            last = last + pd.DateOffset(days=1)
    except:
        last = date_start
    return last

# API çağrısını gerçekleştiren fonksiyon
async def call_api(account, query):
    # API isteği gerçekleştirme kodu burada
    app = TwitterAsync("session")
    await app.sign_in(account[0], account[1])
    partial_tweets = await app.search(query, pages=100)
    return app, partial_tweets

async def main():
    global app
    date_start = list_exported_xlsx_files("2018-01-01")
    date_end = "2018-04-01"
    dates = date_range_pandas(date_start, date_end)
    i = 1
    for date_left, date_right in zip(dates[:-1], dates[1:]):
        result = None
        attempt = 0
        # Başlangıç zamanı
        start_time = time.perf_counter()
        while attempt < max_attempts:
            current_account = accounts[0]  # Listenin ilk elemanını seç
            query = ("from:dikencomtr include:nativeretweets -filter:replies since:" +
                     pd.to_datetime(date_left).strftime("%Y-%m-%d") + " until:" +
                     pd.to_datetime(date_right).strftime("%Y-%m-%d"))
            print(query)
            try:
                app, partial_tweets = await call_api(current_account, query)

                # Eğer API çağrısı faydasız bir sonuç döndürürse kontrol edin
                if not app or not partial_tweets:
                    raise Exception("API çağrısı başarısız oldu")

                print(f"Success with account: {current_account}")
                partial_tweets.tweets = [tweet for tweet in partial_tweets if not getattr(tweet, 'is_retweet', False)]
                tweets_excel_path = "docs/tweets_" + pd.to_datetime(date_left).strftime("%Y-%m-%d") + ".xlsx"
                MyExcel(partial_tweets, tweets_excel_path)
                break  # Başarılı olursa döngüden çık
            except Exception as e:
                print(f"Error with account {current_account}: {e}")
                if app.cookies:
                    # Eğer app None değilse hata sonrası temizle
                    app.cookies.clear()
                accounts.rotate(-1)  # Hesapları sağa kaydırır; sıradaki hesap başa gelir.
                attempt += 1

        elapsed_time = time.perf_counter() - start_time
        print(f"Scraped in {elapsed_time:.4f} saniye")
        i+=1

asyncio.run(main())