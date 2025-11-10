import Link from 'next/link';
import styles from '../styles/NavBar.module.css';

export default function NavBar() {
  return (
    <nav className={styles.navbar}>
      <div className={styles.container}>
        <h1 className={styles.title}>Agent Mira 🏡</h1>
        <Link href="/saved" className={styles.link}>
          Saved Properties
        </Link>
      </div>
    </nav>
  );
}

