import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  // Get environment variables that should be exposed to the client
  const env = {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  };

  return (
    <Html lang="en">
      <Head />
      <body>
        {/* Inject environment variables into window.ENV */}
        <script
          dangerouslySetInnerHTML={{
            __html: `window.ENV = ${JSON.stringify(env)};`,
          }}
        />
        <Main />
        <NextScript />
      </body>
    </Html>
  );
} 