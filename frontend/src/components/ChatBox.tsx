import React, { useState } from "react";
import ReactMarkdown from 'react-markdown'
import axios from "axios";

const ChatBox: React.FC = () => {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");

  const formatArticle = (article: string) => {
    return article
  };

  const handleSubmit = async () => {
    try {
      const res = await axios.get(
        `http://localhost:5001/query?index=main&query=${encodeURIComponent(message)}`
      );

      const formattedArticle = formatArticle(res.data.response);
      setResponse(formattedArticle);
    } catch (error) {
      console.error("Error communicating with backend:", error);
    }
  };

  return (
    <div>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message here"
      />
      <button onClick={handleSubmit}>Submit</button>
      {/* <div>{response && <p>Response: {response}</p>}</div> */}
      <div><h3>Oliver:</h3></div>
      {/* <div>{response && <p>{transformTextToLinks(response)}</p>}</div> */}
      <div>{response && <ReactMarkdown>{response}</ReactMarkdown>}</div>
    </div>
  );
};

export default ChatBox;
