from eldar import build_query
from pprint import pprint


# build list
documents = [
    "Gandalf is a fictional character in Tolkien's The Lord of the Rings",
    "Frodo is the main character in The Lord of the Rings",
    "Ian McKellen interpreted Gandalf in Peter Jackson's movies",
    "Elijah Wood was cast as Frodo Baggins in Jackson's adaptation",
    "The Lord of the Rings is an epic fantasy novel by J. R. R. Tolkien"]

eldar = build_query('("gandalf" OR "frodo") AND NOT ("movie" OR "adaptation")')

# use `filter` to get a list of matches:
pprint(eldar.filter(documents))
# >>> ["Gandalf is a fictional character in Tolkien's The Lord of the Rings",
#     'Frodo is the main character in The Lord of the Rings']

# call to see if the text matches the query:
print(eldar(documents[0]))
# >>> True
print(eldar(documents[2]))
# >>> False
