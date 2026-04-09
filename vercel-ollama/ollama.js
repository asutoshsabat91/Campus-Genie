const { createClient } = require('@vercel/node');

// Ollama API proxy for Vercel deployment
// Handles requests to the Ollama LLM service

module.exports = async (req, res) => {
  if (req.method !== 'POST' && req.method !== 'GET') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    // Forward requests to actual Ollama service
    // In production, you might want to use a managed Ollama service
    const ollamaUrl = process.env.OLLAMA_URL || 'http://localhost:11434';
    
    const response = await createClient().fetch(req.url, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...req.headers,
        'Host': ollamaUrl.replace('http://', '').replace('https://', '')
      },
      body: req.body
    });

    const data = await response.json();
    
  } catch (error) {
    console.error('Ollama proxy error:', error);
    return res.status(500).json({ 
      error: 'Internal Server Error',
      message: 'Failed to connect to Ollama service'
    });
  }
};
