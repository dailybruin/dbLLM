import React, { useState } from "react";
import ReactMarkdown from 'react-markdown'
import axios from "axios";

import styles from "./ChatBox.module.css";

//const BACKEND_DOMAIN = import.meta.env.BACKEND_DOMAIN;

const ChatBox: React.FC = () => {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");

  const handleSubmit = async () => {
    setResponse("Oliver is thinking...");
    try {
      const token = localStorage.getItem("token") || "";
      const res = await axios.get(
        `https://oliver.dailybruin.com/api/query/?index=main&query=${encodeURIComponent(message)}&token=${encodeURIComponent(token)}`
      );

      setResponse(res.data.response);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          setResponse("Unauthorized. Please login to ask Oliver!");
        } else {
          setResponse("An error occurred. Please try again later.");
        }
      } else {
        setResponse("An unexpected error occurred.");
      }
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
