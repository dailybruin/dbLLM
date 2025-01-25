import styles from "./SideBar.module.css"; // Import your custom CSS
import { useState, useEffect } from 'react';

const Sidebar = () => {  

  const [message, setMessage] = useState<string | null>('Loading...'); // Set default state to loading

  useEffect(() => {
    const fetchMessage = async () => {
      try {
        const response = await fetch('http://localhost:5001/get_message'); // Adjust the backend URL if needed
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        setMessage("API Status: " + data.message + "\nModel: " + data.model);
      } catch (error) {
        console.error('Error fetching message:', error + ". Make sure the backend is running");
        setMessage('Error fetching data: ' + error + ". Make sure the backend is running");
      }
    };

    fetchMessage();
    }, []);

  // ===========================================
  // QUERY TIMER
  // ===========================================
  const [timeElapsed, setTimeElapsed] = useState<number>(0);
  const [timerStatus, setTimerStatus] = useState<string>("Waiting");
  const [startTime, setStartTime] = useState<number | null>(null);

  useEffect(() => {
    
    const fetchTimer = async () => {
      try {
        const response = await fetch('http://localhost:5001/get_timer');
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        
        if (data.status === "running") {
          const duration = parseFloat(data.duration) * 1000; // Convert to milliseconds
          setTimeElapsed(duration);
          setTimerStatus("Running");
          if (!startTime) {
            setStartTime(Date.now() - duration);
          }
        } else if (data.status === "stopped") {
          const duration = parseFloat(data.duration) * 1000;
          setTimeElapsed(duration);
          setTimerStatus("Stopped");
          setStartTime(null);
        } else {
          setTimeElapsed(0);
          setTimerStatus("Waiting");
          setStartTime(null);
        }
      } catch (error) {
        console.error('Error fetching timer data:', error);
        setTimerStatus("Error");
      }
    };

    // Update timer display every 10ms if running
    const updateTimer = () => {
      if (startTime && timerStatus === "Running") {
        const currentTime = Date.now();
        setTimeElapsed(currentTime - startTime);
      }
    };

    // Fetch timer status every second
    const statusIntervalId = setInterval(fetchTimer, 10);
    // Update display every 10ms
    const displayIntervalId = setInterval(updateTimer, 10);

    return () => {
      clearInterval(statusIntervalId);
      clearInterval(displayIntervalId);
    };
  }, [startTime, timerStatus]);

  // ===========================================
  // Response TIMER
  // ===========================================
  const [timeElapsedR, setTimeElapsedR] = useState<number>(0);
  const [timerStatusR, setTimerStatusR] = useState<string>("Waiting");
  const [startTimeR, setStartTimeR] = useState<number | null>(null);

  useEffect(() => {
    
    const fetchTimer = async () => {
      try {
        const response = await fetch('http://localhost:5001/get_timerR');
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        
        if (data.status === "running") {
          const duration = parseFloat(data.duration) * 1000; // Convert to milliseconds
          setTimeElapsedR(duration);
          setTimerStatusR("Running");
          if (!startTime) {
            setStartTimeR(Date.now() - duration);
          }
        } else if (data.status === "stopped") {
          const duration = parseFloat(data.duration) * 1000;
          setTimeElapsedR(duration);
          setTimerStatusR("Stopped");
          setStartTimeR(null);
        } else {
          setTimeElapsedR(0);
          setTimerStatusR("Waiting");
          setStartTimeR(null);
        }
      } catch (error) {
        console.error('Error fetching timer data:', error);
        setTimerStatusR("Error");
      }
    };

    // Update timer display every 10ms if running
    const updateTimer = () => {
      if (startTimeR && timerStatusR === "Running") {
        const currentTime = Date.now();
        setTimeElapsedR(currentTime - startTimeR);
      }
    };

    // Fetch timer status every second
    const statusIntervalId = setInterval(fetchTimer, 10);
    // Update display every 10ms
    const displayIntervalId = setInterval(updateTimer, 10);

    return () => {
      clearInterval(statusIntervalId);
      clearInterval(displayIntervalId);
    };
  }, [startTime, timerStatus]);

  // ===========================================
  // Timer Formatting
  // ===========================================
  const formatTime = (milliseconds: number) => {
    const seconds = milliseconds / 1000;
    return seconds.toFixed(2);
  };

    return (
      <div className={styles.sidebarStyle}>
        <h1>Oliver Beta</h1>
        <hr className={styles.sidebarDivider} />
        <h3>{message}</h3>
        <hr className={styles.sidebarDivider} />
        <h3 style={{ color: 'rgb(70, 175, 237)' }}>Model Query Time: {formatTime(timeElapsed)}</h3>
        <h3 style={{ color: 'rgb(70, 175, 237)' }}>Model Response Time: {formatTime(timeElapsedR)}</h3>

      </div>
    );
  };
  
    export default Sidebar;