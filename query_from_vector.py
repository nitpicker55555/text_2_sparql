import os
import getpass
from dotenv import load_dotenv
import os
# from streamlit_chat import message
import io
import asyncio
from SPARQLWrapper import SPARQLWrapper, JSON
import json
"""
Find 4 buildings that have the maximum number of roof surfaces
CityGML buildings affected by heavy snow
 Map roof surfaces of buildings over 35m
  Get buildings with height over 40m
"""
endpoint_url =  "http://localhost:8082/sparql"
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
def run_query(endpoint_url, query):
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    response = sparql.query().convert()

    # 检查响应是否为字节对象，并在必要时解码为字符串
    if isinstance(response, bytes):
        response = response.decode('utf-8')
        response = json.loads(response)
    result_length=0
    for result in response["results"]["bindings"]:
        if len(result)>result_length:
            result_length=len(result)
        print(result)

    if result_length==0:
        return False
    else:
        return True

def change_statement(prompt,user_content,mode='run'):
    import openai

    openai.api_key = ''
    if mode=="run":
        content_str="given the sparql input, please rewrite it to a compete sparql query (just change the key part of the sparql input )to achieve the search goal of "+prompt
    else:
        content_str='given the sparql input, Please translate it to natural language declarative sentences'
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
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


    if mode=="run":
        check_result = check_brackets(final_query)
        while check_result != "False":
            final_query = change_statement(check_result + final_query, extract_result(result))
            check_result = check_brackets(final_query)
        print('----------')
        print("Grammar correct!")
        print('----------')
        print('----------')
        print("final_query:")
        print(final_query)
        print('----------')
    return (final_query)
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
def extract_result(result):
    return result.split('query="""')[1].split('"""')[0]
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
db3 = Chroma(persist_directory="./chroma_db", embedding_function=OpenAIEmbeddings())
template_str="I want to find a complete query, "
while True:
    first_query=input('input:')
    query=template_str+first_query

    docs = db3.as_retriever(search_type="mmr").get_relevant_documents(query)
    result=docs[0].page_content
    print("original result:")
    print('----------')
    print(result)
    print('----------')
    print("processed result:")
    print('----------')
    print(extract_result(result))
    print('----------')
    print("rewrite result:")
    print('----------')
    final_query=change_statement(first_query,extract_result(result))
    print('=========================')
    print("Do you mean: ",change_statement('',final_query,'explain'),"?")
    client_judge=input('yes or no?')
    print('=========================')
    judge_list=['yes','no','y','n']
    while client_judge not in judge_list:
        client_judge = input('Please input yes or no')
    if client_judge in "yes":
        print('----------')
        print("query result:")
        print('----------')

        result_length=run_query(endpoint_url, final_query)
        while not result_length:
            client_feedback=input('query result is 0, do you want to reproduce the query?')
            if client_feedback in "yes":
                final_query = change_statement(first_query, extract_result(result))
                result_length = run_query(endpoint_url, final_query)
            else:
                break

    elif client_judge in 'no':
        print("Please rewrite your query demand")
        break




