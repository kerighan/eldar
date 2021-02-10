import re
from .regex import WILD_CARD_REGEX


class Entry:
    def __init__(self, query):
        self.not_ = False

        if query[:4] == "not ":
            self.not_ = True
            query = query[4:]

        self.query = strip_quotes(query)

        if "*" in self.query:
            self.pattern = self.query.replace("*", WILD_CARD_REGEX)
            self.rgx = re.compile(self.pattern)
        else:
            self.rgx = None

    def evaluate(self, doc):
        if self.rgx:

            if isinstance(doc, str):
                doc = [doc]

            for item in doc:
                if self.rgx.match(item):
                    res = True
                    break
            else:
                res = False
        else:
            res = self.query in doc

        if self.not_:
            return not res

        return res

    def __repr__(self):
        if self.not_:
            return f'NOT "{self.query}"'
        return f'"{self.query}"'


def strip_quotes(query):
    if query[0] == '"' and query[-1] == '"':
        return query[1:-1]
    return query
