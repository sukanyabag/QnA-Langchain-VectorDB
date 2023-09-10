import os
from langchain import PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.deeplake import DeepLake
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyMuPDFLoader
from langchain.chat_models.openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferWindowMemory

from .utils import save

import config as cfg


class Retriever:
    def __init__(self):
        self.text_retriever = None
        self.text_deeplake_schema = None
        self.embeddings = None
        self.memory = ConversationBufferWindowMemory(k=2, return_messages=True)

    def create_and_add_embeddings(self, file):
        os.makedirs("data", exist_ok=True)

        self.embeddings = OpenAIEmbeddings(
            openai_api_key=cfg.OPENAI_API_KEY,
            chunk_size=cfg.OPENAI_EMBEDDINGS_CHUNK_SIZE,
        )

        loader = PyMuPDFLoader(file)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(
            chunk_size=cfg.CHARACTER_SPLITTER_CHUNK_SIZE,
            chunk_overlap=0,
        )
        docs = text_splitter.split_documents(documents)

        self.text_deeplake_schema = DeepLake(
            dataset_path=cfg.TEXT_VECTORSTORE_PATH,
            embedding_function=self.embeddings,
            overwrite=True,
        )

        self.text_deeplake_schema.add_documents(docs)

        self.text_retriever = self.text_deeplake_schema.as_retriever(
            search_type="similarity"
        )
        self.text_retriever.search_kwargs["distance_metric"] = "cos"
        self.text_retriever.search_kwargs["fetch_k"] = 15
        self.text_retriever.search_kwargs["maximal_marginal_relevance"] = True
        self.text_retriever.search_kwargs["k"] = 3

    def retrieve_text(self, query):
        self.text_deeplake_schema = DeepLake(
            dataset_path=cfg.TEXT_VECTORSTORE_PATH,
            read_only=True,
            embedding_function=self.embeddings,
        )

        prompt_template = """You are an intelligent AI which analyses text from documents and 
        answers the user's questions. Please answer in as much detail as possible, so that the user does not have to 
        revisit the document. If you don't know the answer, say that you don't know, and avoid making up things.
        {context}
        Question: {question} 
        Answer:
        """

        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        chain_type_kwargs = {"prompt": PROMPT}

        model = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            openai_api_key=cfg.OPENAI_API_KEY,
        )

        qa = RetrievalQA.from_chain_type(
            llm=model,
            chain_type="stuff",
            retriever=self.text_retriever,
            return_source_documents=False,
            verbose=False,
            chain_type_kwargs=chain_type_kwargs,
            memory=self.memory,
        )

        response = qa({"query": query})
        return response["result"]