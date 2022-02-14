import re


def decode_multipart(body):
    RE_PATTERN = r'(?<=; filename=")(.*?)"\\r\\nContent-Type: (.*?)\\r\\n(.*?)((-{2,})([a-zA-Z0-9_.-]+))'  # noqa
    RE_REPLACE_TO = r'\1"\\r\\nContent-Type: \2\\r\\n\\r\\n<file-data>\\r\\n\4'

    return (
        re.sub(
            pattern=RE_PATTERN,
            repl=RE_REPLACE_TO,
            string="%r" % body,
        )[2:-1]
        .encode()
        .decode("unicode_escape")
    )
