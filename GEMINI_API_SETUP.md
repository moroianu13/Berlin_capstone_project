# Google Gemini AI Setup Guide

## Get Your Free Gemini API Key

1. **Visit Google AI Studio:**
   - Go to https://makersuite.google.com/app/apikey
   - Sign in with your Google account

2. **Create API Key:**
   - Click "Get API Key" or "Create API Key"
   - Select "Create API key in new project" or use existing project
   - Copy the generated API key

3. **Add to .env_docker:**
   ```bash
   GEMINI_API_KEY=your_actual_api_key_here
   ```

4. **Restart Docker:**
   ```bash
   docker-compose down
   docker-compose up --build
   ```

## Free Tier Limits

- **60 requests per minute** (RPM)
- **1 million tokens per minute** (TPM)
- **1,500 requests per day** (RPD)

Perfect for development and small-scale projects!

## Features Now Enabled

✅ **Fluent AI Conversations** - Natural language understanding
✅ **Context-Aware Responses** - Remembers conversation history
✅ **Berlin RentWise Integration** - Knows about your website features
✅ **Fallback System** - Uses Wikipedia/YAML if AI unavailable

## Test the Chatbot

1. Open http://localhost
2. Click the Berlin Bear chat icon
3. Try asking:
   - "What neighborhoods are good for families?"
   - "Tell me about living in Berlin"
   - "I'm looking for affordable rent, any suggestions?"
   - "What's the nightlife like in Friedrichshain?"

The AI will provide natural, conversational responses!
