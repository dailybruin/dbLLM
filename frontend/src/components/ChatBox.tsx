import React, { useState } from "react";
import ReactMarkdown from 'react-markdown'
import axios from "axios";

// This function is used to transform text with links in the format [text](link) to hyperlinks
// This function has been DEPRECATED, but we will keep it here for now just in case we need it
function TextWithLink({ text, link, linkText }: { text: string; link: string; linkText: string; }) {
    return (
        <p>
            {text}
            <a href={link} target="_blank" rel="noopener noreferrer">{linkText}</a>
        </p>
    );
}

// DEPRECATED function for hyperlinks
function transformTextToLinks(text: string): React.ReactNode {
  const linkRegex = /\[([^\]]+)\]\((https?:\/\/[^\s]+)\)/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match;

    while ((match = linkRegex.exec(text)) !== null) {
        parts.push(text.substring(lastIndex, match.index)); // Text before the link

        const linkText = match[1];
        const linkUrl = match[2];

        parts.push(
          <a key={match.index} href={linkUrl} target="_blank" rel="noopener noreferrer">{linkText}</a>
        );
        lastIndex = match.index + match[0].length;
      }
    parts.push(text.substring(lastIndex)); // Remaining Text

  return <React.Fragment>{parts.map((part, index) => <React.Fragment key={index}>{part}</React.Fragment>)}</React.Fragment>
}

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
