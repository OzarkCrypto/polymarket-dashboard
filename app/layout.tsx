import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Polymarket Tech 마켓 & 홀더 대시보드',
  description: 'Tech 카테고리의 액티브 마켓과 각 마켓의 Yes/No 탑10 홀더를 확인하세요.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  )
}

