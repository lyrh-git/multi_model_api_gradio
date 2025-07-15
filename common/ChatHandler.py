
class ChatHandler:
    def handle_query_texts(self, texts):
        query_list = list()
        if isinstance(texts, str):
            query_list = [{"role": "user", "content": texts}]
        elif isinstance(texts, list):
            if all(isinstance(text, str) for text in texts):
                query_list = [{"role": "user" if i % 2 == 0 else "assistant", "content": text} for i, text in
                              enumerate(texts)]
            elif all(isinstance(text, dict) and "role" in text for text in texts):
                query_list = texts
        return query_list