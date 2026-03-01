import requests

def test_faang():
    res = requests.get("https://faang.watch/api/search", params={"categories": "Software Engineering", "seniority": "Entry", "page_size": 2})
    print(res.status_code)
    try:
        print(res.json())
    except:
        print(res.text)

if __name__ == "__main__":
    test_faang()
