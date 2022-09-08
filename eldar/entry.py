import re
from collections import defaultdict
from dataclasses import dataclass

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


class IndexEntry:
    def __init__(self, query_term):
        self.not_ = False

        if query_term == "*":
            raise ValueError(
                "Single character wildcards * are not implemented")

        if " " in query_term:  # multiword query
            self.query_term = strip_quotes(query_term).split()
            self.search = self.search_multiword
        else:
            self.query_term = query_term
            self.search = self.search_simple

    def search_simple(self, index):
        res = index.get(self.query_term)
        return {match.id for match in res}

    def search_multiword(self, index):
        docs = defaultdict(list)
        for token in self.query_term:
            items = index.get(token)
            for item in items:
                docs[item.id].append((item.position, token))

        # utils variable
        first_token = self.query_term[0]
        query_len = len(self.query_term)
        query_rest = self.query_term[1:]
        iter_rest = range(1, query_len)

        results = set()
        for doc_id, tokens in docs.items():
            tokens = sorted(tokens)
            if len(tokens) < query_len:
                continue
            for i in range(len(tokens) - query_len + 1):
                pos, tok = tokens[i]
                if tok != first_token:
                    continue
                is_a_match = True
                for j, correct_token in zip(iter_rest, query_rest):
                    next_pos, next_tok = tokens[i + j]
                    if correct_token != next_tok or next_pos != pos + j:
                        is_a_match = False
                        break
                if is_a_match:
                    results.add(doc_id)
                    break
        return results

    def __repr__(self):
        if self.not_:
            return f'NOT "{self.query_term}"'
        return f'"{self.query_term}"'


def strip_quotes(query):
    if query[0] == '"' and query[-1] == '"':
        return query[1:-1]
    return query


@dataclass(unsafe_hash=True, order=True)
class Item:
    id: int
    position: int
