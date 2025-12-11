import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Polymarket 기업 마켓 대시보드',
  description: 'Polymarket에서 기업 관련 마켓을 필터링하여 내부 정보 우위가 있을 수 있는 마켓을 찾습니다.',
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

