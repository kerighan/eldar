from eldar import build_query
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
eldar = build_query('("gandalf" OR "frodo") AND NOT ("movie" OR "adaptation")')

# eldar's call returns True if the text matches the query.
# You can filter a dataframe using pandas mask syntax:
df = df[df.content.apply(eldar)]
print(df)
