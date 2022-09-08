

class Binary:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class AND(Binary):
    def search(self, index):
        left_match = self.left.search(index)
        right_match = self.right.search(index)
        return left_match.intersection(right_match)

    def __repr__(self):
        return f"({self.left}) AND ({self.right})"


class ANDNOT(Binary):
    def search(self, index):
        left_match = self.left.search(index)
        right_match = self.right.search(index)
        return left_match.difference(right_match)

    def __repr__(self):
        return f"({self.left}) AND NOT ({self.right})"


class OR(Binary):
    def search(self, index):
        left_match = self.left.search(index)
        right_match = self.right.search(index)
        return left_match.union(right_match)

    def __repr__(self):
        return f"({self.left}) OR ({self.right})"
