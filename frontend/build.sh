#!/bin/bash
# Vercel build script for frontend

# Export production API URL if not already set
export VITE_API_URL="${VITE_API_URL:-https://pie-global-funitures.onrender.com/api}"
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-https://pie-global-funitures.onrender.com}"

echo "Building with API URL: $VITE_API_URL"

# Run the build
npm run build
