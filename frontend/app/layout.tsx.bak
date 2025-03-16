import type { Metadata } from 'next';
import './styles/globals.css';

export const metadata: Metadata = {
  title: 'Python Learning Platform',
  description: 'Interactive platform for learning Python programming',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <script src="/heartbeat.js" defer></script>
      </head>
      <body className="min-h-screen bg-gray-50">
        {children}
      </body>
    </html>
  );
} 