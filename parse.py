import re
import requests
from bs4 import BeautifulSoup
import functools


BASE_URL = "https://wooordhunt.ru/"


def _parse(word: str):
    URL = BASE_URL + "word/" + word
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    return soup


@functools.lru_cache(maxsize=500)
def translate_word(word: str):
    """
    Возвращает 3 варианта перевода, или None если не удалось найти перевод
    """
    soup = _parse(word)

    if soup.find(class_="t_inline_en"):
        return ", ".join(soup.find(class_="t_inline_en").text.split(", ")[:3])


@functools.lru_cache(maxsize=500)
def full_translate(word: str):
    soup = _parse(word)
    request_dict = {}

    if soup.find(class_="t_inline_en"):
        request_dict["main translate"] = soup.find(class_="t_inline_en").text
    elif soup.find(class_='possible_variant'):
        return full_translate(
            soup.find(class_='possible_variant')['href'].split('/')[-1]
        )
    elif soup.find(id='word_forms'):
        return full_translate(
            soup.find(id='word_forms').a['href'].split('/')[-1]
        )

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

    return word, request_dict
я