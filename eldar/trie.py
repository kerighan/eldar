

class Trie:
    def __init__(self):
        self.trie = {}

    def add_tokens(self, tokens):
        for token in tokens:
            self.add_token(token)

    def add_token(self, token):
        leaf = self.trie
        for char in token:
            if char in leaf:
                leaf = leaf[char]
            else:
                leaf[char] = {}
                leaf = leaf[char]
        if 1 in leaf:
            return
        leaf[1] = 1  # the word exist

    def get(self, token):
        leaf = self.trie
        current_str = ""
        for char in token:
            if char != "*":
                if char not in leaf:
                    return []
                leaf = leaf[char]
                current_str += char
            else:
                return self.dfs(current_str, leaf)
        if 1 in leaf:
            return [token]
        return []

    def dfs(self, current_str, leaf):
        res = []
        for key in leaf:
            if key == 1:
                res.append(current_str)
            else:
                res.extend(self.dfs(current_str+key, leaf[key]))
        return res
