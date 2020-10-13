from unidecode import unidecode
import re


__version__ = "0.0.5"


word_regex = r'([\w]+|[,?;.:\/!()\[\]\'"’\\><+-=])'


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
            doc = set(re.findall(word_regex, doc, re.UNICODE))
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


class Binary:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class AND(Binary):
    def evaluate(self, doc):
        left_match = self.left.evaluate(doc)
        if not left_match:
            return False
        right_match = self.right.evaluate(doc)
        if not right_match:
            return False
        return True

    def __repr__(self):
        return f"({self.left}) AND ({self.right})"


class ANDNOT(Binary):
    def evaluate(self, doc):
        left_match = self.left.evaluate(doc)
        if not left_match:
            return False
        right_match = self.right.evaluate(doc)
        return not right_match

    def __repr__(self):
        return f"({self.left}) AND NOT ({self.right})"


class OR(Binary):
    def evaluate(self, doc):
        if self.left.evaluate(doc):
            return True
        if self.right.evaluate(doc):
            return True
        return False

    def __repr__(self):
        return f"({self.left}) OR ({self.right})"


class Entry:
    def __init__(self, query):
        self.query = strip_quotes(query)

    def evaluate(self, doc):
        return self.query in doc

    def __repr__(self):
        return self.query


def parse_query(query, ignore_case=True, ignore_accent=True):
    # remove brackets around query
    if query[0] == '(' and query[-1] == ')' and query.count('(') == 1:
        query = strip_brackets(query)
    # if there are quotes around query, make an entry
    if query[0] == '"' and query[-1] == '"' and query.count('"') == 2:
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
    if query[0] == "(" and query[-1] == ")":
        return query[1:-1]
    return query


def strip_quotes(query):
    if query[0] == '"' and query[-1] == '"':
        return query[1:-1]
    return query


def is_balanced(query):
    # are brackets balanced
    brackets_b = query.count("(") == query.count(")")
    quotes_b = query.count('"') % 2 == 0
    return brackets_b and quotes_b
