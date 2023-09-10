from retriever.retrieval import Retriever


class Controller:
    def __init__(self):
        self.retriever = None
        self.query = ""

    def embed_document(self, file):
        if file is not None:
            self.retriever = Retriever()
            self.retriever.create_and_add_embeddings(file.name)

    def retrieve(self, query):
        texts = self.retriever.retrieve_text(query)
        return texts