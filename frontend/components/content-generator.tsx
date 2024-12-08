'use client'

import { useState } from 'react'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card'
import { Loader2, RefreshCw } from 'lucide-react'
import axios from 'axios'

export default function ContentGenerator() {
  const [prompt, setPrompt] = useState('')
  const [tone, setTone] = useState('humorous')
  const [platform, setPlatform] = useState('twitter')
  const [isLoading, setIsLoading] = useState(false)
  const [generatedContent, setGeneratedContent] = useState<{
    text: string
    image: string
    video: string
    meme: string
    sources: string[]
  } | null>(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    try {
      const response = await axios.post('http://localhost:8000/generate', {
        prompt,
        tone,
        platform,
      })
      setGeneratedContent(response.data)
    } catch (err) {
      console.error('Error generating content:', err)
      setError('Failed to generate content. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-2xl bg-white/90 backdrop-blur-sm">
      <CardHeader>
        <CardTitle>Generate Content</CardTitle>
        <CardDescription>Enter your prompt and preferences to generate content</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="prompt">Prompt</Label>
            <Input
              id="prompt"
              placeholder="E.g., Create a humorous post about AI trends today"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="tone">Tone</Label>
              <Select value={tone} onValueChange={setTone}>
                <SelectTrigger id="tone">
                  <SelectValue placeholder="Select tone" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="humorous">Humorous</SelectItem>
                  <SelectItem value="formal">Formal</SelectItem>
                  <SelectItem value="casual">Casual</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="platform">Platform</Label>
              <Select value={platform} onValueChange={setPlatform}>
                <SelectTrigger id="platform">
                  <SelectValue placeholder="Select platform" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="twitter">Twitter</SelectItem>
                  <SelectItem value="instagram">Instagram</SelectItem>
                  <SelectItem value="linkedin">LinkedIn</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Generate Content
              </>
            )}
          </Button>
        </form>
      </CardContent>
      {error && (
        <CardContent>
          <p className="text-red-500">{error}</p>
        </CardContent>
      )}
      {generatedContent && (
        <CardFooter className="flex flex-col">
          <Tabs defaultValue="text" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="text">Text</TabsTrigger>
              <TabsTrigger value="image">Image</TabsTrigger>
              <TabsTrigger value="video">Video</TabsTrigger>
              <TabsTrigger value="meme">Meme</TabsTrigger>
            </TabsList>
            <TabsContent value="text" className="mt-4">
              <p className="text-sm">{generatedContent.text || 'No text generated.'}</p>
            </TabsContent>
            <TabsContent value="image" className="mt-4">
              {generatedContent.image ? (
                <img src={generatedContent.image} alt="Generated content" className="w-full h-auto rounded-lg" />
              ) : (
                <p className="text-sm">No image generated.</p>
              )}
            </TabsContent>
            <TabsContent value="video" className="mt-4">
              {generatedContent.video ? (
                <video src={generatedContent.video} controls className="w-full h-auto rounded-lg">
                  Your browser does not support the video tag.
                </video>
              ) : (
                <p className="text-sm">No video generated.</p>
              )}
            </TabsContent>
            <TabsContent value="meme" className="mt-4">
              {generatedContent.meme ? (
                <img src={generatedContent.meme} alt="Generated meme" className="w-full h-auto rounded-lg" />
              ) : (
                <p className="text-sm">No meme generated.</p>
              )}
            </TabsContent>
          </Tabs>
          {generatedContent.sources.length > 0 && (
            <div className="mt-4 w-full">
              <h4 className="font-semibold mb-2">Sources:</h4>
              <ul className="list-disc list-inside">
                {generatedContent.sources.map((source, index) => (
                  <li key={index} className="text-sm">
                    <a href={source} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                      {source}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardFooter>
      )}
    </Card>
  )
}