import './globals.css'

export const metadata = {
  title: 'Polymarket Tech Markets',
  description: 'Tech markets with top holders',
}

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  )
}
