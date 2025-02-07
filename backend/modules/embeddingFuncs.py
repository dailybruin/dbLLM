def embedArticle(genai, embeddings: list, embedding_model: str, article):
    """
    Embed an article using Google Gemini and append to embeddings array.
    @param genai: Google Gemini instance.
    @param embeddings: List of embeddings to append to.
    @param embedding_model: Embedding model string.
    @param article: Article data (id, link, date, content).
    """
    try:
        # Extract content and generate embedding using Google Gemini
        content = article['content']['rendered']
        embedding_vector = genai.embed_content(model=embedding_model, content=content)['embedding']

        # Construct embedding object
        new_embedding = {
            "id": str(article['id']),
            "values": embedding_vector,
            "metadata": {
                "date": article['date'],
                "date_gmt": article['date_gmt'],
                "link": article['link']
            }
        }

        # Append new embedding to the list
        embeddings.append(new_embedding)
    except Exception as e:
        print(f"Error embedding article {article['id']}: {e}")

def embedChunksAsArticle(genai, embeddings: list, embedding_model: str, article, split_texts: list):
    """
    Embed chunks of an article and append to embeddings array.
    @param genai: Google Gemini instance.
    @param embeddings: List of embeddings to append to.
    @param embedding_model: Embedding model string.
    @param article: Article data (id, link, date, etc).
    @param split_texts: List of text chunks to embed.
    @return: True if successful, False if any error occurs.
    """
    try:
        # Iterate through text chunks and embed
        for i, split_text in enumerate(split_texts):
            embedding_vector = genai.embed_content(model=embedding_model, content=split_text)['embedding']

            # Construct embedding for each chunk
            chunk_embedding = {
                "id": f"{article['id']}_chunk{i}",
                "values": embedding_vector,
                "metadata": {
                    "date": article['date'],
                    "date_gmt": article['date_gmt'],
                    "link": article['link'],
                    "chunk_total": len(split_texts)
                }
            }

            # Append chunk embedding to list
            embeddings.append(chunk_embedding)
        return True
    except Exception as e:
        print(f"Error embedding chunks for article {article['id']}: {e}")
        return False

def generateQueryEmbedding(genai, embedding_model: str, query: str):
    """
    Convert a query string into an embedding.
    @param genai: Google Gemini instance.
    @param embedding_model: Embedding model string.
    @param query: Query string.
    @return: Query embedding if successful, None otherwise.
    """
    try:
        # Generate query embedding using Google Gemini
        return genai.embed_content(model=embedding_model, content=query)["embedding"]
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        return None
