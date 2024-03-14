import re

def find_links(text: str):
    # Regular expression to find all URLs in the text
    url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+(?=\b)'

    links = re.findall(url_regex, text)
    return links
