
def embedArticle(genai, embeddings, embedding_model, article):
    """
        Embed an article using a google gemini embedding model and append it to the embeddings array

        @param genai: The google gemini variable
        @param embeddings: The array of embeddings that we will append to
        @param embedding_model: As a string, what embedding model to use
        @param article: The article, including its id, link, date, etc (not just the page content)
        @return: None
    """
    content = article['content']['rendered']
    article_id = str(article['id'])

    # Generate embedding using Google Gemini
    embedding_response = genai.embed_content(
        model=embedding_model,
        content=content)
    embedding_vector = embedding_response['embedding']

    # The new embedding that will be added to the embeddings array
    new_embedding = {
        "id": article_id,
        "values": embedding_vector,
        "metadata": {
            "date": article['date'],
            "date_gmt": article['date_gmt'],
            "link": article['link']
        }
    }

    # Append the new embedding
    embeddings.append(new_embedding)

def embedChunksAsArticle(genai, embeddings, embedding_model, article, split_texts):
    """
        Embed chunks using a google gemini embedding model and append it to the embeddings array

        @param genai: The google gemini variable
        @param embeddings: The array of embeddings that we will append to
        @param embedding_model: As a string, what embedding model to use
        @param article: The article, including its id, link, date, etc (not just the page content)
        @param split_texts: An array holding the split version of article (only the rendered page texts, not info like date or link)
        @return: A bool -  False if there was an error embedding, True if successful
    """
    new_embeddings = []

    # Try embedding each text
    for i, split_text in enumerate(split_texts):
        try:
            # Generate embedding using Google Gemini
            embedding_response = genai.embed_content(
                model=embedding_model,
                content=split_text)
            embedding_vector = embedding_response['embedding']
        
            # Append to embeddings list
            # The id for this is a bit different, with a chunk number added to the end (to preserve unique ids)
            new_embeddings.append({
                "id": f"{str(article['id'])}_chunk{i}",
                "values": embedding_vector,
                "metadata": {
                    "date": article['date'],
                    "date_gmt": article['date_gmt'],
                    "link": article['link'],
                    "chunk_total": len(split_texts)
                }
            })
        # If there was an error embedding
        except Exception as e:
            print(f"Error generating embedding for article {article['id']}: {e}. Could not split into chunks.")
            # Return false indicating error (embeddings remains unchanged)
            return False
    
    # If everything was successful, append to the embeddings array
    embeddings.extend(new_embeddings)
    # Return True indicating success
    return True