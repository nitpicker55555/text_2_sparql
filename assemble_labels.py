import os
import getpass
from dotenv import load_dotenv
import os
# from streamlit_chat import message
import io
import asyncio
from SPARQLWrapper import SPARQLWrapper, JSON
import json,re
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
def check_brackets(sparql_query):
    brackets_counter = {
        '(': 0,
        ')': 0,
        '{': 0,
        '}': 0,
        '[': 0,
        ']': 0,
    }
    last_occurrence = {
        '(': -1,
        ')': -1,
        '{': -1,
        '}': -1,
        '[': -1,
        ']': -1,
    }
    lines = sparql_query.split('\n')

    for line_number, line in enumerate(lines, start=1):
        for char_index, char in enumerate(line):
            if char in brackets_counter:
                brackets_counter[char] += 1
                last_occurrence[char] = line_number


    error_found = "False"
    if brackets_counter['('] != brackets_counter[')']:
        print(f"Error: Unmatched parentheses, last occurrence at line {last_occurrence['('] or last_occurrence[')']}")
        error_found = f"Error: Unmatched parentheses, last occurrence at line {last_occurrence['('] or last_occurrence[')']}"
    if brackets_counter['{'] != brackets_counter['}']:
        print(f"Error: Unmatched curly braces, last occurrence at line {last_occurrence['{'] or last_occurrence['}']}")
        error_found = f"Error: Unmatched curly braces, last occurrence at line {last_occurrence['{'] or last_occurrence['}']}"
    if brackets_counter['['] != brackets_counter[']']:
        print(
            f"Error: Unmatched square brackets, last occurrence at line {last_occurrence['['] or last_occurrence[']']}")
        error_found = f"Error: Unmatched square brackets, last occurrence at line {last_occurrence['['] or last_occurrence[']']}"


    return error_found
def get_numbers_from_string(s):
    return re.findall(r'\d+', s)
def contains_numbers(s):
    return bool(re.search(r'\d', s))
def search_label(ques,label):
    with open("label_part.txt", "r", encoding="utf-8") as file:
        content = file.read()
    import re

    # Search for the pattern "OSM---------" followed by any characters and then "---------"
    pattern = r"%s---------([\s\S]*?)---------"%label
    match = re.search(pattern, content)

    # Extract the content between the two patterns
    result = match.group(1).strip() if match else " "
    pre_prompt=""
    if result.split("\n")[0].startswith("#"):
        pre_prompt=result.split("\n")[0][1:]
        print("pre_prompt:")
        print(pre_prompt)
        print("-----")
    if "numerical_value_height" in label:
        print("original code:")
        print(result)
        print("========")
        # ques = get_numbers_from_string(ques)[0]
        result=change_statement([pre_prompt,ques],result)
    if   label=="OSM_building" :
        print("original:")
        print(result)
        print("========")
        print("changed:")
        result=change_statement([pre_prompt,ques],result)
        print(result)
        print("========")
    return result

def change_statement(prompts,user_content,mode='run'):
    import openai

    openai.api_key = api_key
    if prompts[0]!="":
        prompt=prompts[1]
        pre_prompt=prompts[0]
        if contains_numbers(pre_prompt):

            content_str="given the input sentence with number of %s, please rewrite it to  %s,please do not change other words and pay attention to the sign <,>,="%(pre_prompt,prompt)
        else:
            content_str="given the input of %s, please rewrite it to the building item in the sentence below %s, please Pay attention to capitalization"%(pre_prompt,prompt)

    else:
        prompt=prompts
        content_str="given the input, please rewrite it to %s, please Pay attention to capitalization"%prompt
    print(content_str)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": content_str
            },
            {
                "role": "user",
                "content": user_content
            }
        ],
        temperature=0,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # print(response["choices"][0]["message"]["content"])
    final_query=response["choices"][0]["message"]["content"]


    # if mode=="run":
    #     check_result = check_brackets(final_query)
    #     while check_result != "False":
    #         final_query = change_statement(check_result + final_query, check_result)
    #         check_result = check_brackets(final_query)
    #     print('----------')
    #     print("Grammar correct!")
    #     print('----------')
    #     print('----------')
    #     print("final_query:")
    #     print(final_query)
    #     print('----------')
    return (final_query)

def classification(text):
    import openai

    type_of_buildings = """
    OSM: specific kind of building mentioned like hotel, Briefkasten,Bridge.
    General_buildings: no specific building mentioned.
    residential_buildings: residential building mentioned.
    
    """



    content = "###type_of_buildings###\n{%s}\n\n###Instructions###\nCategorise the following text to one or more type.\n{%s}\n"%(type_of_buildings,text)

    function = {
        "name": "classify_type_of_building",
        "description": "Predict the type of buildings for a given text",
        "parameters": {
            "type": "object",
            "properties": {
                "prediction": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "OSM",
                            "General_buildings",
                            "residential_buildings",
                        ]
                    },
                    "description": "The classified type of building."
                }
            },
            "required": [
                "prediction"
            ]
        }
    }

    r = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.0,
        messages=[{"role": "user", "content": content}],
        functions=[function],
        function_call={"name": "classify_type_of_building"},
    )

    classification_result=json.loads(r["choices"][0]["message"]["function_call"]["arguments"])["prediction"][0]



    print("Building classification_result:")
    print(classification_result)
    print("----------")
    return (classification_result)


# print(change_statement())
def assemble(ques):
    prefix_part=search_label(ques,'PREFIX')+'\n'
    building_type=classification(ques)
    main_part="SELECT *\n{\n"+search_label(ques,building_type)+"\n"+search_label(ques,building_type+"_building")+'\n'+search_label(ques,building_type+"_numerical_value_height")+"\n}"
    final_query=prefix_part+main_part
    return (final_query)
while True:
    final_query=(assemble(input("input:")))

    check_result = check_brackets(final_query)
    while check_result != "False":
        final_query = change_statement(check_result + final_query, check_result)
        check_result = check_brackets(final_query)
    print('----------')
    print("Grammar correct!")
    print('----------')
    print('----------')
    print("final_query:")
    print(final_query)
    print('----------')
