from unidecode import unidecode
import cython
import re


__version__ = "0.0.3"
operators = {"OR", "AND", "AND NOT"}


class ExpressionError(Exception):
    pass


cdef is_balanced(str query):
    # are brackets balanced
    brackets_b = query.count("(") == query.count(")")
    quotes_b = query.count('"') % 2 == 0
    return brackets_b and quotes_b


cdef is_valid(list ops):
    # check if a query part is valid
    if len(ops) == 2:
        return True
    else:
        first_one = ops[0]
        for item in ops[1:-1]:
            if item != first_one:
                raise ExpressionError("Cannot mix OR, AND or AND NOT "
                                      "in the same level without "
                                      "brackets.")
        return True


@cython.boundscheck(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef build_query(str query, int ignore_case=True, int ignore_accent=True):
    cpdef match_iter
    cpdef part
    cpdef key
    cpdef list match = []
    cpdef (Py_ssize_t, Py_ssize_t) match_item
    cpdef list splitted
    cpdef value
    cpdef Py_ssize_t i
    cpdef int start
    cpdef int end
    cpdef int match_len
    cpdef Py_ssize_t last_index = 0
    cpdef list tmp = []
    cpdef list res = []
    cpdef list ops = []
    cpdef Node node = None

    if not is_balanced(query):
        raise ExpressionError("Unbalanced brackets or quotes")

    query = query.strip() + " OR "
    match_iter = re.finditer(r" (AND NOT|AND|OR) ", query)
    for m in match_iter:
        match_item = (m.start(0), m.end(0))
        match.append(match_item)
    match_len = len(match)

    if match_len <= 1:
        key = None
        query = query[:match[0][0]]
        if query[0] == '"' and query[-1] == '"':
            value = query[1:-1]
        else:
            splitted = query.split(":", 1)
            if len(splitted) == 1:
                value = splitted[0]
            else:
                key = splitted[0]
                value = splitted[1]

        return Node(value=value,
                    key=key,
                    ignore_case=ignore_case,
                    ignore_accent=ignore_accent)
    else:
        last_index = 0
        for i in range(match_len):
            start, end = match[i]
            part = query[last_index:start]
            if is_balanced(part):
                res.append(part)
                ops.append(query[start + 1:end - 1])
                last_index = end

        is_valid(ops)
        node = Node(ops[0])
        for subquery in res:
            if subquery[0] == "(" and subquery[-1] == ")":
                subquery = subquery[1:-1]
            node += build_query(subquery)
        return node


cdef class Node():
    cpdef list children
    cpdef operator
    cpdef value
    cpdef key
    cpdef int ignore_case
    cpdef int ignore_accent

    def __init__(self, operator="AND", str value=None, str key=None, int ignore_case=True, int ignore_accent=True):
        self.children = []
        self.operator = operator
        self.ignore_case = ignore_case
        self.ignore_accent = ignore_accent
        if value is not None:
            value = value.strip()
            if value == "TRUE":
                pass
            elif value == "FALSE":
                pass
            else:
                if value[0] == '"' and value[-1] == '"':
                    value = value[1:-1]
                if ignore_case:
                    value = value.lower()
                if ignore_accent:
                    value = unidecode(value)
        self.value = value
        self.key = key

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    def __call__(self, text):
        return self.query(text)

    def __iadd__(self, Node node):
        self.children.append(node)
        return self
    
    cpdef filter(self, list texts):
        cpdef results = []
        for text in texts:
            if self.query(text):
                results.append(text)
        return results
    
    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef evaluate(self, text):
        cpdef value = self.value
        cpdef key = self.key
        cpdef int ignore_case = self.ignore_case
        cpdef int ignore_accent = self.ignore_accent

        if key is None:
            if value == u"TRUE":
                return True
            elif value == u"FALSE":
                return False

            if ignore_case:
                text = text.lower()
            if ignore_accent:
                text = unidecode(text)
            return value in text
        else:
            if value == u"TRUE":
                return True
            elif value == u"FALSE":
                return False

            text_ = text[key]
            if ignore_case:
                text_ = text_.lower()
            if ignore_accent:
                text_ = unidecode(text_)
            return value in text_

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cpdef query(self, text):
        cpdef operator
        cpdef value = self.value
        cpdef list children = self.children
        cpdef int children_num = len(children)
        cpdef Node child = None
        cpdef Py_ssize_t i
        cpdef int res

        operator = self.operator.lower()

        if value is not None:
            return self.evaluate(text)

        if operator == "and":
            # for child in children:
            for i in range(children_num):
                child = children[i]
                q = child.query(text)
                if not q:
                    return False
            return True
        
        if operator == "or":
            res = False
            for i in range(children_num):
                child = children[i]
                q = child.query(text)
                if q:
                    return True
            return False

        if operator == "and not":
            if len(children) != 2:
                raise ExpressionError("AND NOT needs correct parentheses")
            
            left = children[0].query(text)
            if not left:
                return False

            right = children[1].query(text)
            return not right
