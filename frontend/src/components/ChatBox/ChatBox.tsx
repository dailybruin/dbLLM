import React, { useState, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import axios from "axios";
import { useNavigate } from "react-router-dom";

import styles from "./ChatBox.module.css";

//const BACKEND_DOMAIN = import.meta.env.BACKEND_DOMAIN;

interface ChatBoxProps {
  onTimingUpdate: (queryTime: number, responseTime: number) => void;
}


const ChatBox: React.FC<ChatBoxProps> = ({ onTimingUpdate }) => {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");
  const navigate = useNavigate(); // Initialize useNavigate
  const BACKEND_DOMAIN = import.meta.env.VITE_BACKEND_DOMAIN

  const handleSubmit = useCallback(async () => {
    if (!message.trim()) return; // Prevent empty message submission

    setResponse("Oliver is thinking...");
    try {
      const token = localStorage.getItem("token") || "";
      const res = await axios.get(
        `${BACKEND_DOMAIN}/api/query/?index=main&query=${encodeURIComponent(message)}&token=${encodeURIComponent(token)}`
      );

      // Add these lines to handle timing data
      if (res.data.query_time && res.data.response_time) {
        onTimingUpdate(res.data.query_time, res.data.response_time);
      }

      setResponse(res.data.response);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          setResponse("Unauthorized. Please login to ask Oliver!");
          
          // Remove any local storage, and redirect to login page
          localStorage.clear();
          navigate("/");

        } else {
          setResponse("An error occurred. Please try again later.");
        }
      } else {
        setResponse("An unexpected error occurred.");
      }
    }
  }, [message, onTimingUpdate]);

  useEffect(() => {
    const keyDownHandler = (e: KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    };

    document.addEventListener("keydown", keyDownHandler);
    return () => {
      document.removeEventListener("keydown", keyDownHandler);
    };
  }, [handleSubmit]);

  return (
    <div className={styles.textContainer}>
      <div className={styles.chatBox}>
        <textarea
          className={styles.textarea}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message here"
        />
        <button
          className={styles.submitButton}
          onClick={handleSubmit}
          disabled={!message.trim()}
        >
          Ask Oliver!
        </button>
      </div>

      <div>
        {response && (
          <ReactMarkdown className={styles.responseText}>
            {response}
          </ReactMarkdown>
        )}
      </div>
    </div>
  );
};

export default ChatBox;
