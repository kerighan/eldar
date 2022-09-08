import re
from collections import defaultdict

from unidecode import unidecode

from .entry import IndexEntry, Item
from .query import is_balanced, strip_brackets
from .regex import WORD_REGEX


class Index:
    def __init__(
        self,
        ignore_case=True,
        ignore_accent=True,
        use_trie=True
    ):
        self.ignore_case = ignore_case
        self.ignore_accent = ignore_accent
        self.use_trie = use_trie
        self._index = defaultdict(set)

    def get(self, query_term):
        if query_term == "*":
            raise ValueError(
                "Single character wildcards * are not implemented")

        if "*" not in query_term:
            res = self._index.get(query_term, set())
            if not isinstance(res, set):
                res = set(res)
            return res
        else:
            query_regex = query_term.replace("*", ".*")
            if self.use_trie:
                matches = self._trie.get(query_term)
                matches = [
                    token for token in matches
                    if re.match(query_regex, token) is not None
                ]
            else:
                matches = [
                    token for token in self._index
                    if re.match(query_regex, token) is not None
                ]
            results = set()
            for match in matches:
                res = self._index[match]
                if not isinstance(res, set):
                    res = set(res)
                results.update(res)
            return results

    def build(self, documents, verbose=False):
        self.documents = documents
        if verbose:
            from tqdm import tqdm
            iteration = tqdm(enumerate(documents), total=len(documents))
        else:
            iteration = enumerate(documents)
        for i, document in iteration:
            tokens = self.preprocess(document)
            for j, token in enumerate(tokens):
                self._index[token].add(Item(i, j))

        if self.use_trie:
            from .trie import Trie
            self._trie = Trie()
            self._trie.add_tokens(self._index.keys())

    def preprocess(self, doc):
        if self.ignore_case:
            doc = doc.lower()
        if self.ignore_accent:
            doc = unidecode(doc)
        doc = re.findall(WORD_REGEX, doc, re.UNICODE)
        return doc

    def search(self, query, return_ids=False):
        query = parse_query(query,
                            ignore_case=self.ignore_case,
                            ignore_accent=self.ignore_accent)
        ids = query.search(self)
        if return_ids:
            return ids

        return [self.documents[i] for i in ids]

    def count(self, query):
        return len(self.search(query, return_ids=True))

    def save(self, filename):
        import pickle
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename):
        import pickle
        with open(filename, "rb") as f:
            index = pickle.load(f)
        return index


def parse_query(query, ignore_case=True, ignore_accent=True):
    from .indexops import AND, ANDNOT, OR

    # remove brackets around query
    if query[0] == '(' and query[-1] == ')':
        query = strip_brackets(query)
    # if there are quotes around query, make an entry
    if query[0] == '"' and query[-1] == '"' and query.count('"') == 1:
        if ignore_case:
            query = query.lower()
        if ignore_accent:
            query = unidecode(query)
        return IndexEntry(query)

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
        return IndexEntry(query)
