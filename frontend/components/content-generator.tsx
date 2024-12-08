'use client';

import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
} from '@mui/material';
import axios from 'axios';

export default function ContentGenerator() {
  const [prompt, setPrompt] = useState('');
  const [tone, setTone] = useState('humorous');
  const [platform, setPlatform] = useState('twitter');
  const [tabIndex, setTabIndex] = useState(0);
  const [generatedContent, setGeneratedContent] = useState({
    text: '',
    image: '',
    video: '',
    meme: '',
    sources: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await axios.post('http://localhost:8000/generate', {
        prompt,
        tone,
        platform,
      });
      setGeneratedContent(response.data);
    } catch (err) {
      console.error('Error generating content:', err);
      setError('Failed to generate content. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box maxWidth="600px" mx="auto" mt="4" p="4" boxShadow={3}>
      <form onSubmit={handleSubmit}>
        <FormControl fullWidth margin="normal">
          <TextField
            label="Prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your prompt"
          />
        </FormControl>

        <FormControl fullWidth margin="normal">
          <InputLabel id="tone-label">Tone</InputLabel>
          <Select
            labelId="tone-label"
            value={tone}
            onChange={(e) => setTone(e.target.value)}
          >
            <MenuItem value="humorous">Humorous</MenuItem>
            <MenuItem value="formal">Formal</MenuItem>
            <MenuItem value="casual">Casual</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth margin="normal">
          <InputLabel id="platform-label">Platform</InputLabel>
          <Select
            labelId="platform-label"
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
          >
            <MenuItem value="twitter">Twitter</MenuItem>
            <MenuItem value="instagram">Instagram</MenuItem>
            <MenuItem value="linkedin">LinkedIn</MenuItem>
          </Select>
        </FormControl>

        <Button
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate Content'}
        </Button>
      </form>

      {error && (
        <Box mt="4" color="red">
          <p>{error}</p>
        </Box>
      )}

      <Box mt="4">
        <Tabs
          value={tabIndex}
          onChange={(_, newIndex) => setTabIndex(newIndex)}
          variant="fullWidth"
        >
          <Tab label="Text" />
          <Tab label="Image" />
          <Tab label="Video" />
          <Tab label="Meme" />
        </Tabs>
        <Box mt="2" p="2">
          {tabIndex === 0 && <p>{generatedContent.text || 'No text generated yet.'}</p>}
          {tabIndex === 1 && generatedContent.image && (
            <img src={generatedContent.image} alt="Generated Image" style={{ maxWidth: '100%' }} />
          )}
          {tabIndex === 2 && generatedContent.video && (
            <video controls src={generatedContent.video} style={{ maxWidth: '100%' }} />
          )}
          {tabIndex === 3 && generatedContent.meme && (
            <img src={generatedContent.meme} alt="Generated Meme" style={{ maxWidth: '100%' }} />
          )}
        </Box>
        {generatedContent.sources.length > 0 && (
          <Box mt="4">
            <h4>Sources:</h4>
            <ul>
              {generatedContent.sources.map((source, index) => (
                <li key={index}>
                  <a href={source} target="_blank" rel="noopener noreferrer">
                    {source}
                  </a>
                </li>
              ))}
            </ul>
          </Box>
        )}
      </Box>
    </Box>
  );
}
