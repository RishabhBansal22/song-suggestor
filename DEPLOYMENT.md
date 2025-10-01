# Deployment Guide

This guide explains how to deploy the Song Suggestor application with the backend on Railway and the frontend on Vercel.

## Architecture

- **Backend (API)**: Deployed on Railway (FastAPI application)
- **Frontend (Static)**: Deployed on Vercel (HTML/CSS/JavaScript in `static/` folder)

## Railway Deployment (Backend)

### Prerequisites
1. Railway account ([railway.app](https://railway.app))
2. GitHub repository connected to Railway

### Environment Variables on Railway

Set the following environment variables in your Railway project dashboard:

```
GOOGLE_API_KEY=your_google_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app,https://your-custom-domain.com
```

**Important**: The `ALLOWED_ORIGINS` variable must include your Vercel deployment URL(s) for CORS to work properly.

### Deployment Steps

1. **Connect Repository**
   - Go to Railway dashboard
   - Create a new project
   - Connect your GitHub repository

2. **Configure Build**
   - Railway will auto-detect the Python application
   - The `Procfile` is already configured with: `web: uvicorn api:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   - Add all the environment variables listed above
   - Click "Deploy" or let Railway auto-deploy

4. **Get Your Railway URL**
   - After deployment, Railway will provide a URL like:
   - `https://song-suggestor-production.up.railway.app`
   - Copy this URL - you'll need it for Vercel configuration

### Testing the Backend

Test your Railway backend:
```bash
curl https://song-suggestor-production.up.railway.app/health
```

Expected response:
```json
{"status": "healthy", "message": "API is running smoothly ✨"}
```

---

## Vercel Deployment (Frontend)

### Prerequisites
1. Vercel account ([vercel.com](https://vercel.com))
2. Your Railway backend URL from above

### Deployment Steps

#### Option 1: Using Vercel CLI (Recommended)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from the `static/` folder**
   ```bash
   cd static/
   vercel
   ```

4. **Follow the prompts**
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N** (first time)
   - Project name? Enter a name (e.g., `song-suggestor-frontend`)
   - In which directory is your code located? **./  (current directory)**

5. **Deploy to production**
   ```bash
   vercel --prod
   ```

#### Option 2: Using Vercel Dashboard

1. **Import Project**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your GitHub repository
   - Or drag and drop the `static/` folder

2. **Configure Project**
   - Framework Preset: **Other**
   - Root Directory: `static/` 
   - Build Command: Leave empty (it's a static site)
   - Output Directory: Leave empty or set to `./`

3. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete

### Post-Deployment Configuration

After deploying to Vercel, you'll get a URL like:
- `https://your-project-name.vercel.app`

**IMPORTANT**: You must update the Railway environment variables:

1. Go to your Railway dashboard
2. Add your Vercel URL to `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://your-project-name.vercel.app,https://localhost:3000,http://127.0.0.1:8000
   ```
3. Redeploy Railway if needed

### Custom Domain (Optional)

To use a custom domain on Vercel:

1. Go to your Vercel project settings
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed
5. **Remember**: Add your custom domain to Railway's `ALLOWED_ORIGINS`

---

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:

1. **Check Railway environment variables**
   - Verify `ALLOWED_ORIGINS` includes your Vercel URL
   - Format: comma-separated list, no spaces
   - Example: `https://app.vercel.app,https://custom.com`

2. **Check the Railway logs**
   ```bash
   # In Railway dashboard, view logs to see CORS requests
   ```

3. **Verify the frontend is using the correct backend URL**
   - Open browser DevTools > Network tab
   - Check if requests go to your Railway URL
   - Look for failed OPTIONS (preflight) requests

### Frontend Not Loading

1. **Check Vercel deployment logs**
   - Go to Vercel dashboard > Deployments
   - Click on your deployment
   - View "Building" and "Functions" logs

2. **Verify file structure**
   - Ensure `index.html` is in the root of deployed folder
   - Check `app.js` and `styles.css` are accessible

3. **Test static files directly**
   ```
   https://your-app.vercel.app/index.html
   https://your-app.vercel.app/app.js
   https://your-app.vercel.app/styles.css
   ```

### Backend Not Responding

1. **Check Railway logs**
   - Railway Dashboard > Deployments > View logs
   - Look for startup errors

2. **Verify environment variables**
   - All required variables are set
   - No typos in variable names
   - API keys are valid

3. **Test endpoints directly**
   ```bash
   # Health check
   curl https://your-railway-app.up.railway.app/health
   
   # Root endpoint
   curl https://your-railway-app.up.railway.app/
   ```

### Image Upload Fails

1. **Check file size** - Maximum 10MB allowed
2. **Check file type** - Only image files supported
3. **Check Railway logs** - Look for error messages
4. **Verify API keys** - Google API and Spotify credentials

---

## Local Development

### Backend (API)

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your keys
GOOGLE_API_KEY=your_key
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret

# Run the API
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

### Frontend (Static)

Open `static/index.html` in your browser or use a local server:

```bash
# Using Python
cd static/
python -m http.server 5500

# Using Node.js
cd static/
npx http-server -p 5500
```

Frontend will be available at: `http://localhost:5500`

The frontend will automatically detect localhost and use `http://localhost:8000` as the API URL.

---

## Environment Variables Summary

### Railway (Backend)
| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `SPOTIFY_CLIENT_ID` | Spotify API client ID | Yes |
| `SPOTIFY_CLIENT_SECRET` | Spotify API client secret | Yes |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed frontend URLs | Yes |

### Vercel (Frontend)
No environment variables needed - the frontend uses the hardcoded Railway URL.

---

## Quick Checklist

Before going live, ensure:

- [ ] Railway backend is deployed and accessible
- [ ] Railway health endpoint returns 200 OK
- [ ] All Railway environment variables are set
- [ ] Vercel frontend is deployed
- [ ] Vercel URL is added to Railway's `ALLOWED_ORIGINS`
- [ ] Frontend successfully calls backend (test with an image upload)
- [ ] CORS is working (no errors in browser console)
- [ ] Custom domains are configured (if using)
- [ ] Custom domains are in Railway's `ALLOWED_ORIGINS` (if using)

---

## Support

If you encounter issues:

1. Check Railway logs for backend errors
2. Check browser console for frontend errors
3. Verify CORS configuration
4. Test API endpoints directly with curl
5. Ensure all environment variables are correctly set

## Update URLs

If your Railway or Vercel URLs change:

1. **Railway URL changed**: Update `static/app.js` line where `API_BASE_URL` is defined
2. **Vercel URL changed**: Update Railway's `ALLOWED_ORIGINS` environment variable
3. Redeploy both services after changes
