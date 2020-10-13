from eldar import Query
from pprint import pprint


# create list of documents to match:
documents = [
    "Gandalf is a fictional character in Tolkien's The Lord of the Rings",
    "Frodo is the main character in The Lord of the Rings",
    "Ian McKellen interpreted Gandalf in Peter Jackson's movies",
    "Elijah Wood was cast as Frodo Baggins in Jackson's adaptation",
    "The Lord of the Rings is an epic fantasy novel by J. R. R. Tolkien"]

# build query:
query = Query('("gandalf" OR "frodo") AND NOT ("movie" OR "adaptation")')

# print query:
print(query)
# >>> ((gandalf) OR (frodo)) AND NOT ((movie) OR (adaptation))

# use `filter` method to get a list of matches:
pprint(query.filter(documents))
# >>> ["Gandalf is a fictional character in Tolkien's The Lord of the Rings",
#      'Frodo is the main character in The Lord of the Rings',
#      "Ian McKellen interpreted Gandalf in Peter Jackson's movies"]

# /!\ The last document of the result is a match, because "movies" != "movie".
# To match subwords, use match_word=False in the Query:
query = Query(
    '("gandalf" OR "frodo") AND NOT ("movie" OR "adaptation")',
    match_word=False)  # this will also exclude "movies"

# call to see if the text matches the query:
print(query(documents[0]))
# >>> True
print(query(documents[2]))
# >>> False
