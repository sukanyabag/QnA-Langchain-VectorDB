from langchain.callbacks import get_openai_callback


def save(query, qa):
    with get_openai_callback() as cb:
        response = qa({"query": query}, return_only_outputs=True)
        return response["result"]