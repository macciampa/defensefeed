import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Pryzm · Intelligence Platform',
  description: 'Personalized government opportunity feed for defense contractors',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
