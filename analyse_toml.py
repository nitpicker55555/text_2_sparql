import re
def analyse(query_string,keywords):


    keywords_list = keywords.lower().split()
    print(keywords)
    print(keywords_list)
    keywords_list_ori = [word[:-1] if word.endswith('s') else word for word in keywords_list]
    numbers = re.findall(r'\d+', keywords)
    keywords_list_ori.extend(numbers)
    keywords_list=[]
    # print(query_string)
    for item in keywords_list_ori:
        if '/' in item:
            keywords_list.extend(item.split('/'))
        else:
            keywords_list.append(item)
    # print(keywords_list)
    # Check and encapsulate words in query_string
    tokens = re.findall(r'\d+|\S+', query_string)
    stop_words = ["a", "the", "is", "of", "and", "in", "on", "with", "for", "as", "by", "at", "to",'osm']
    stop_words_query=['PREFIX','?linkage','?building']
    # Filter out the stop words from keywords_list
    filtered_keywords_list = [keyword for keyword in keywords_list if keyword not in stop_words]
    selected_words=[]
    lines = query_string.split('\n')
    processed_lines = []

    for line in lines:
        # Skip lines that start with '#'
        if line.strip().startswith("#"):
            continue
        tokens = re.findall(r'\d+|\S+', line)
        output_line = ""
        for token in tokens:

            if any(keyword in token.lower() for keyword in filtered_keywords_list):
                if token not in stop_words_query and "http" not in token:
                    selected_words.append(token)
                    output_line += "{= " + token + " =}"
                else:
                    output_line += token
            else:
                output_line += token
            output_line += " "
        processed_lines.append(output_line)

    # Join the processed lines to get the final multi-line output
    output_multiline_string = '\n'.join(processed_lines)
    print(selected_words)
    print(output_multiline_string)
    return output_multiline_string
with open("query_template.txt", "r", encoding="utf-8") as file:
        toml_content = file.read()
query_pattern = re.compile(r'query="""(.*?)"""', re.DOTALL)
queries = query_pattern.findall(toml_content)

name_pattern = re.compile(r'name="([^"]+)"')
names = name_pattern.findall(toml_content)

for num,i in enumerate(queries):
    print("_______________",num)
    analyse(i,names[num])
for num,i in enumerate(names):
    print(num,i)