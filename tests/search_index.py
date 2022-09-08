from eldar import Index
from eldar.trie import Trie

documents = [
    "Gandalf is a fictional character in Tolkien's The Lord of the Rings",
    "Frodo is the main character in The Lord of the Rings",
    "Ian McKellen interpreted Gandalf in Peter Jackson's movies",
    "Elijah Wood was cast as Frodo Baggins in Jackson's adaptation",
    "The Lord of the Rings is an epic fantasy novel by J. R. R. Tolkien",
    "Frodo Baggins is a hobbit"
]

index = Index()
index.build(documents)  # no copy is made

# index.save("index.p")  # but documents are copied to disk
# index = Index.load("index.p")

# support for wildcard
print(index.search('"frodo b*" AND NOT hobbit'))
