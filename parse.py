import re
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://wooordhunt.ru/"


def parse_word(word: str):
    URL = BASE_URL + "word/" + word
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    try:
        request_dict = {"main translate": soup.find(class_="t_inline_en").text}
    except:
        if soup.title.text == "Упссс...":
            return parse_word(soup.find(id='word_not_found').a['href'].split('/')[1])
        else:
            return parse_word(soup.find(id='word_forms').a['href'].split('/')[1])

    p = re.compile(r'<i>.*?</i>')

    for part_of_speech, tr in zip(soup.find_all(class_="pos_item"), soup.find_all(class_="tr")):
        part_of_speech = re.sub('[^a-zа-яё-]', '', part_of_speech.text, flags=re.IGNORECASE).strip()

        out_tr = []
        tr = p.sub('', str(tr))

        for i in tr.split("<br/>"):
            i = re.sub('[^а-яё ,]', '', i, flags=re.IGNORECASE).strip()
            for j in i.split(','):
                j = j.strip()
                if j:
                    out_tr.append(i)

        request_dict[part_of_speech] = ", ".join(out_tr)
    return request_dict
