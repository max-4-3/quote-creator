from requests import Session
from rich import print
import json, os
from fake_useragent import UserAgent
from render import text_to_image 

def make_session(**kwargs):
    session = Session(**kwargs)
    session.headers["UserAgent"] = UserAgent().random
    return session

def load_data(fp: str):
    try:
        with open(fp, 'r', errors='ignore', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print('Error while loading data:', e)

    return None

def save_data(data: dict | list, fp: str):
    try:
        with open(fp + (".json" if not fp.endswith(".json") else ""), "w", errors="ignore", encoding="utf-8") as file:
            json.dump(data, file)
        return True
    except Exception as e:
        print('Error While Saving:', e)

    return False

def make_request(session: Session, url: str, method="GET", **kwargs):
    req = session.request(method, url=url, **kwargs)
    req.raise_for_status()
    return req.json()

def main():
    mode = input("Do you want to load new quotes?: ")
    if mode.lower().strip() in ["no", "n"]:
        fp = "quotes.json"
        data = load_data(fp)
    else:
        url = "https://zenquotes.io/api/quotes"
        session = make_session()
        print("Making request to", url)
        data = None
        try:
            data = make_request(session, url)
        except Exception as e:
            print('Unable to make request', e)
            return

        print('Request Succesfull!')
        print(data)

        fp = "quotes.json"
        save_data(data, fp)
        print('Data Saved at', fp)
    
    if not data:
        print('Data is None')
        return
    
    save_path = "quotes"
    os.makedirs(save_path, exist_ok=True)

    for i, d in enumerate(data, start = 1):
        quote = d["q"]
        print(f'Converting {quote} to image')
        text_to_image("“" + quote.strip() + "”", output_path=os.path.join(save_path, f"{i}_quote.png"))

if __name__ == "__main__":
    main()


