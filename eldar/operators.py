

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
