from unidecode import unidecode
import re
from .regex import WORD_REGEX
from .entry import Entry
from .operators import AND, ANDNOT, OR


class Query:
    def __init__(
        self,
        query,
        ignore_case=True,
        ignore_accent=True,
        match_word=True
    ):
        self.ignore_case = ignore_case
        self.ignore_accent = ignore_accent
        self.match_word = match_word
        self.query = parse_query(query, ignore_case, ignore_accent)

    def preprocess(self, doc):
        if self.ignore_case:
            doc = doc.lower()
        if self.ignore_accent:
            doc = unidecode(doc)
        if self.match_word:
            doc = set(re.findall(WORD_REGEX, doc, re.UNICODE))
        return doc

    def evaluate(self, doc):
        doc = self.preprocess(doc)
        return self.query.evaluate(doc)

    def filter(self, documents):
        docs = []
        for doc in documents:
            if not self.evaluate(doc):
                continue
            docs.append(doc)
        return docs

    def __call__(self, doc):
        return self.evaluate(doc)

    def __repr__(self):
        return self.query.__repr__()


def parse_query(query, ignore_case=True, ignore_accent=True):
    # remove brackets around query
    if query[0] == '(' and query[-1] == ')':
        query = strip_brackets(query)
    # if there are quotes around query, make an entry
    if query[0] == '"' and query[-1] == '"' and query.count('"') == 1:
        if ignore_case:
            query = query.lower()
        if ignore_accent:
            query = unidecode(query)
        return Entry(query)

    # find all operators
    match = []
    match_iter = re.finditer(r" (AND NOT|AND|OR) ", query, re.IGNORECASE)
    for m in match_iter:
        start = m.start(0)
        end = m.end(0)
        operator = query[start+1:end-1].lower()
        match_item = (start, end)
        match.append((operator, match_item))
    match_len = len(match)

    if match_len != 0:
        # stop at first balanced operation
        for i, (operator, (start, end)) in enumerate(match):
            left_part = query[:start]
            if not is_balanced(left_part):
                continue

            right_part = query[end:]
            if not is_balanced(right_part):
                raise ValueError("Query malformed")
            break

        if operator == "or":
            return OR(
                parse_query(left_part, ignore_case, ignore_accent),
                parse_query(right_part, ignore_case, ignore_accent)
            )
        elif operator == "and":
            return AND(
                parse_query(left_part, ignore_case, ignore_accent),
                parse_query(right_part, ignore_case, ignore_accent)
            )
        elif operator == "and not":
            return ANDNOT(
                parse_query(left_part, ignore_case, ignore_accent),
                parse_query(right_part, ignore_case, ignore_accent)
            )
    else:
        if ignore_case:
            query = query.lower()
        if ignore_accent:
            query = unidecode(query)
        return Entry(query)


def strip_brackets(query):
    count_left = 0
    for i in range(len(query) - 1):
        letter = query[i]
        if letter == "(":
            count_left += 1
        elif letter == ")":
            count_left -= 1
        if i > 0 and count_left == 0:
            return query

    if query[0] == "(" and query[-1] == ")":
        return query[1:-1]
    return query


def is_balanced(query):
    # are brackets balanced
    brackets_b = query.count("(") == query.count(")")
    quotes_b = query.count('"') % 2 == 0
    return brackets_b and quotes_b
