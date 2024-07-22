from operator import itemgetter

from langchain.chains import LLMChain

from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_openai import AzureChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate

import yaml

with open('/Users/kdh/Desktop/project/langchain-prac/key.yaml') as f:
    config = yaml.safe_load(f)

api_version = config["config"]["api_version"]
azure_endpoint = config["config"]["azure_endpoint"]
api_key = config["config"]["api_key"]
model = config["config"]["model"]

def read_prompt_template(file_path: str) -> str:
    with open(file_path, "r") as f:
        prompt_template = f.read()

    return prompt_template


writer_llm = AzureChatOpenAI(
    azure_deployment = model,
    api_version = api_version,
    azure_endpoint = azure_endpoint,
    api_key = api_key
)

writer_prompt_template = ChatPromptTemplate.from_template(
    template=read_prompt_template("/Users/kdh/Desktop/project/langchain-prac/novel_chain_prac/langchain/prompt_template_v1.txt")
)

writer_chain = LLMChain(
    llm=writer_llm, prompt = writer_prompt_template, output_key = "output"
)

messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]

result = writer_chain(messages)
ai_msg = llm.invoke(messages)
print(ai_msg.content)

#############################
model = AzureChatOpenAI(
    azure_deployment = model,
    api_version = api_version,
    azure_endpoint = azure_endpoint,
    api_key = api_key
)

prompt1 = ChatPromptTemplate.from_template("what is the city {person} is from")
prompt2 = ChatPromptTemplate.from_template(
    "what country is the city {city} in? respond in {language}"
)

chain1 = prompt1 | model | StrOutputParser()
#chain1_answer = chain1.invoke({"person" : "obama"})
#print(chain1_answer)

chain2 = (
    {"city" : chain1, "language" : itemgetter("language")}
    | prompt2 | model | StrOutputParser()
)

chain2.invoke({"person" : "obama", "language": "korean"})