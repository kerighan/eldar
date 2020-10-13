from eldar import Query
import pandas as pd


# build dataframe
df = pd.DataFrame([
    "Gandalf is a fictional character in Tolkien's The Lord of the Rings",
    "Frodo is the main character in The Lord of the Rings",
    "Ian McKellen interpreted Gandalf in Peter Jackson's movies",
    "Elijah Wood was cast as Frodo Baggins in Jackson's adaptation",
    "The Lord of the Rings is an epic fantasy novel by J. R. R. Tolkien"],
    columns=['content'])

# build query object
query = Query(
    '("gandalf" OR "frodo") AND NOT ("movies" OR "adaptation")',
    ignore_case=True,
    ignore_accent=True,
    match_word=True)

# calling the object returns True if the text matches the query.
# You can filter a dataframe using pandas mask syntax:
df = df[df.content.apply(query)]
print(df)
