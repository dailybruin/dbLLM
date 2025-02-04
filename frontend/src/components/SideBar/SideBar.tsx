import styles from "./SideBar.module.css"; // Import your custom CSS
import { useState, useEffect } from 'react';

//const BACKEND_DOMAIN = import.meta.env.BACKEND_DOMAIN;

interface SidebarProps {
  queryTime: number;
  responseTime: number;
}

const Sidebar = ({ queryTime, responseTime }: SidebarProps) => {  
  const [message, setMessage] = useState<string | null>('Loading...');

  useEffect(() => {
    const fetchMessage = async () => {
      try {
        const response = await fetch(`http://localhost:5001/api/get_message/`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();
        setMessage("API Status: " + data.message + "\nModel: " + data.model);
      } catch (error) {
        console.error('Error fetching message:', error);
        setMessage('Error fetching data: ' + error + ". Make sure the backend is running");
      }
    };
    fetchMessage();
  }, []);

  const formatTime = (seconds: number) => {
    return seconds.toFixed(2);
  };

  return (
    <div className={styles.sidebarStyle}>
      <div>
        <h1>Oliver Beta</h1>
        <hr className={styles.sidebarDivider} />
        <h3>{message}</h3>
        <hr className={styles.sidebarDivider} />
        <h3 style={{ color: "rgb(70, 175, 237)" }}>
          Model Query Time: {formatTime(queryTime)}
        </h3>
        <h3 style={{ color: "rgb(70, 175, 237)" }}>
          Model Response Time: {formatTime(responseTime)}
        </h3>
      </div>

      <div>
        <h3>Any feedback is appreciated. </h3>
        <br />
        <p><i>The information above is purely for beta testing.</i></p>
      </div>
    </div>
  );
};
  
export default Sidebar;