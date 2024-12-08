import { Metadata } from 'next'
import ContentGenerator from '../components/content-generator'

export const metadata: Metadata = {
  title: 'AI News Content Generator',
  description: 'Generate engaging social media content from daily news',
}

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4 sm:p-8 bg-gradient-to-br from-gray-50 to-gray-100">
      <h1 className="text-3xl sm:text-4xl font-bold text-gray-800 mb-8 text-center">AI News Content Generator</h1>
      <ContentGenerator />
    </main>
  )
}