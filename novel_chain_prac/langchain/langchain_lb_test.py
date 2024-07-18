from langchain.chains import LLMChain
from langchain.chains import llm
from langchain.prompts.chat import ChatPromptTemplate
# from langchain.chat_models import AzureChatOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAI
# from langchain_openai import AsyncAzureOpenAI
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