# Input
query_string = "?osmclassname a lgdo:Hotel . OPTIONAL { ?osmentity rdfs:label ?hotelname .}FILTER(?buildingHeight > 30) ."
keywords = "Hotels over 30m high"
import re

# Extract numbers from keywords and add them to the list

# Preprocessing keywords
keywords_list = keywords.lower().split()
print(keywords_list)
keywords_list = [word[:-1] if word.endswith('s') else word for word in keywords_list]
numbers = re.findall(r'\d+', keywords)
keywords_list.extend(numbers)
print(keywords_list)
# Check and encapsulate words in query_string
tokens = re.findall(r'\d+|\S+', query_string)

# Check and encapsulate words in tokens
output_string = ""
for token in tokens:
    if any(keyword in token.lower() for keyword in keywords_list):
        output_string += "{= " + token + " =}"
    else:
        output_string += token
    output_string += " "

print(output_string)