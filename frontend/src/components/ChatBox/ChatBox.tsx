import React, { useState } from "react";
import ReactMarkdown from 'react-markdown'
import axios from "axios";

import styles from "./ChatBox.module.css";

const ChatBox: React.FC = () => {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");

  const handleSubmit = async () => {
    try {
      const res = await axios.get(
        `http://localhost:5001/query?index=main&query=${encodeURIComponent(message)}`
      );

      setResponse(res.data.response);
    } catch (error) {
      console.error("Error communicating with backend:", error);
    }
  };

  return (
    <div className={styles.textContainer}>
      <div className={styles.chatBox}>
      <textarea
        className = {styles.textarea}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message here"
      />
      <button className={styles.submitButton} onClick={handleSubmit}>Ask Oliver!</button>
    </div>
    
      {/* <div>{response && <p>Response: {response}</p>}</div> */}
      {/* <div>{response && <p>{transformTextToLinks(response)}</p>}</div> */}
      <div>{response && <ReactMarkdown className={styles.responseText}>{response}</ReactMarkdown>}</div>
    </div>
  );
};

export default ChatBox;
