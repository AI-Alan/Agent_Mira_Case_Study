import type { AppProps } from 'next/app';
import Head from 'next/head';
import NavBar from '../components/NavBar';
import '../styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>Agent Mira - AI Real Estate Chatbot</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <NavBar />
      <main>
        <Component {...pageProps} />
      </main>
    </>
  );
}

