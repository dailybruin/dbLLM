import styles from "./Banner.module.css";
import { useAuth } from "../../Context/useAuth";

function Banner() {
  const { logoutUser } = useAuth();
  
  return (
    <div className={styles.gridContainer}>
      <h2 className={styles.bannerTitle}> UCLA Daily Bruin — Project Oliver </h2>
      <button className={styles.logoutButton} onClick={logoutUser}>Logout</button>
    </div>
  );
}

export default Banner;