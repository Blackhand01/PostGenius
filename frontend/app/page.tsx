import { Metadata } from 'next'
import ContentGenerator from '../components/content-generator'

export const metadata: Metadata = {
  title: 'AI News Content Generator',
  description: 'Generate engaging social media content from daily news',
}

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-purple-400 to-indigo-600">
      <h1 className="text-4xl font-bold text-white mb-8">AI News Content Generator</h1>
      <ContentGenerator />
    </main>
  )
}

