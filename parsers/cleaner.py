def normalize(text):

    if text is None:
        return ""

    text = str(text)

    text = text.strip()

    text = text.replace("\n", " ")

    text = " ".join(text.split())

    return text