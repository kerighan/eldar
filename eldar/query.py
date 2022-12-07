from unidecode import unidecode
import re
from typing import Dict
from .entry import Entry
from .operators import AND, ANDNOT, OR


class Query:
    def __init__(
        self,
        query,
        ignore_case=True,
        ignore_accent=True,
    ):
        self.ignore_case = ignore_case
        self.ignore_accent = ignore_accent
        self.query_text = query
        self.query = parse_query(query, ignore_case, ignore_accent)

    def preprocess(self, doc):
        if self.ignore_case:
            doc = doc.lower()
        if self.ignore_accent:
            doc = unidecode(doc)
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

    def validate_query(self) -> Dict:
        """
        Checks that the query provided is valid and does not cause an error.

        We perform the following checks:
            - Check we actually have a query
            - Check parentheses are even
            - Check quotation marks are even
            - Check correct spacing after AND/OR condition
            - If it's still working run it through and test for any unknown error
        First we run some basic checks such as making sure we have the correct number of parentheses and quotation marks

        Then we actually try evaluate the query and ensure there are no error
        :return:
        """
        query = str(self.query)
        sample_text = "Hello world!"
        query_issues = []
        is_valid = True
        # Check we actually have a query
        if self.query is not None and len(self.query_text.strip()) == 0:
            query_issues.append("No query provided")
            is_valid = False

        # Check parentheses are even
        open_brackets = re.findall(r'\(', query)
        close_brackets = re.findall(r'\)', query)

        if len(open_brackets) != len(close_brackets):
            is_valid = False
            query_issues.append("Number of opening and closing parentheses do not match")

        # Check quotation marks are even
        quotation_marks = re.findall(r'"', query)
        if len(quotation_marks) % 2 != 0:
            is_valid = False
            query_issues.append("Number of opening and closing quotation marks do not match")

        # Check correct spacing after AND/OR condition
        for match in re.finditer(r"(\bAND NOT\b|\bAND\b|\bOR\b)", query):
            start = match.start()
            end = match.end()
            if (
                    start == 0 or
                    query[start - 1] != " " or
                    end == len(query) or
                    query[end] != " "
            ):
                is_valid = False
                query_issues.append(
                    "Incorrect spacing following AND/OR/AND NOT condition. Please ensure you have a whitespace "
                    "character after each of these conditions"
                )
        if is_valid is True:
            # Handle if an unknown error occurs
            try:
                self.evaluate(sample_text)
            except Exception:
                is_valid = False
                if len(re.findall(r'(\band not\b|\band\b|\bor\b)', query)) > 0:
                    query_issues.append(
                        'If you are including an "AND" or "OR" or "AND NOT" condition, please ensure they are in '
                        'upper case'
                    )
                else:
                    query_issues.append(f"Unable to validate query due to an unknown error")

        return {"is_valid": is_valid, "query_issues": query_issues}

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
    match_iter = re.finditer(r"(\bAND NOT\b|\bAND\b|\bOR\b)", query,)
    for m in match_iter:
        start = m.start(0)
        end = m.end(0)
        operator = query[start:end].lower()
        match_item = (start, end)
        match.append((operator, match_item))
    match_len = len(match)

    if match_len != 0:
        left_part = None
        right_part = None
        # stop at first balanced operation
        for i, (operator, (start, end)) in enumerate(match):
            left_part = query[:start].strip()
            right_part = query[end:].strip()

        if left_part is not None and right_part is not None:
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
