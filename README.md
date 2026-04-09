# Media Processor App (Full Stack)

A full-stack web application that allows users to process media files directly from a URL using powerful FFmpeg operations.
The system allows users to input a media URL and perform operations such as thumbnail extraction, video compression, and audio extraction using FFmpeg via Python subprocess.
The backend handles downloading, processing, and returning media efficiently, while the frontend provides an interactive UI with real-time feedback.
Real-world deployment challenges such as cross-origin requests, stateless server behavior, and media streaming by implementing direct file responses and blob handling on the frontend are addressed.

## Live Demo

🔗 Frontend (Vercel):  
https://media-processor-ten.vercel.app  

🔗 Backend (Render):  
https://media-processor-92kn.onrender.com  

## Overview

This application enables users to:

- Extract thumbnails from videos
- Compress videos
- Extract audio from video files

The system is built using a **React frontend** and a **FastAPI backend**, with media processing handled via **FFmpeg using Python subprocess**.

## Architecture

Frontend (React)

↓

Backend API (FastAPI)

↓

Media Processing (FFmpeg via subprocess)

## Setup Instructions (Local)

1. Clone Repository:
   
-git clone https://github.com/YOUR_USERNAME/media-processor-app.git

-cd media-processor-app

2. Backend Setup:
   
-cd backend

-python3 -m venv venv

-source venv/bin/activate

-pip install -r requirements.txt

-uvicorn app:app --reload

3. Frontend Setup:
   
-cd frontend

-npm install

-npm start

Sample Input:
https://download.samplelib.com/mp4/sample-5s.mp4
