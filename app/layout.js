import './globals.css'

export const metadata = {
  title: 'Polymarket Tech Insider',
  description: 'Tech prediction markets dashboard for insider trading capture',
}

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body>{children}</body>
    </html>
  )
}
