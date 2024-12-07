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

export default function ContentGenerator() {
  const [prompt, setPrompt] = useState('');
  const [tone, setTone] = useState('humorous');
  const [platform, setPlatform] = useState('twitter');
  const [tabIndex, setTabIndex] = useState(0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log({ prompt, tone, platform });
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
        >
          Generate Content
        </Button>
      </form>

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
          {tabIndex === 0 && <p>Generated Text</p>}
          {tabIndex === 1 && <p>Generated Image</p>}
          {tabIndex === 2 && <p>Generated Video</p>}
          {tabIndex === 3 && <p>Generated Meme</p>}
        </Box>
      </Box>
    </Box>
  );
}
