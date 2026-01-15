import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Todo Chatbot',
  description: 'AI-powered todo management chatbot',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
