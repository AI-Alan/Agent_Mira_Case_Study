import Link from 'next/link';
import Head from 'next/head';
import styles from '../styles/SavedPage.module.css';

export default function SavedPage() {
  return (
    <>
      <Head>
        <title>Saved Properties - Agent Mira</title>
      </Head>
      <div className={styles.container}>
        <div className={styles.content}>
          <h1 className={styles.title}>Saved Properties</h1>
          <p className={styles.description}>
            Your saved properties will appear here.
          </p>
          <Link href="/" className={styles.link}>
            ← Back to Chat
          </Link>
        </div>
      </div>
    </>
  );
}

