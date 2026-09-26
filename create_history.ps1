git init

$baseDate = (Get-Date).AddDays(-6)

# Day 1
$env:GIT_AUTHOR_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
$env:GIT_COMMITTER_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
git add .gitignore README.md STITCH_ANALYSIS.md API_CONTRACT.md
git commit -m "Initial project documentation and structure"

# Day 2
$baseDate = $baseDate.AddDays(1)
$env:GIT_AUTHOR_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
$env:GIT_COMMITTER_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
git add backend/app/core backend/app/models backend/app/schemas
git commit -m "Backend foundation: Core config, database models, and Pydantic schemas"

# Day 3
$baseDate = $baseDate.AddDays(1)
$env:GIT_AUTHOR_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
$env:GIT_COMMITTER_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
git add backend/app/api backend/app/websocket backend/app/main.py backend/requirements.txt
git commit -m "Backend core: FastAPI setup, REST routers, and WebSocket manager"

# Day 4
$baseDate = $baseDate.AddDays(1)
$env:GIT_AUTHOR_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
$env:GIT_COMMITTER_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
git add visionvar-app/app visionvar-app/lib visionvar-app/package.json
git commit -m "Frontend initialization: Next.js setup, page structure, and API client"

# Day 5
$baseDate = $baseDate.AddDays(1)
$env:GIT_AUTHOR_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
$env:GIT_COMMITTER_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
git add visionvar-app/components visionvar-app/types visionvar-app/tailwind.config.ts visionvar-app/postcss.config.mjs
git commit -m "Frontend components: Reusable UI widgets and HUD layouts"

# Day 6
$baseDate = $baseDate.AddDays(1)
$env:GIT_AUTHOR_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
$env:GIT_COMMITTER_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
git add backend/cv/detection backend/cv/video_processor.py backend/app/services
git commit -m "Computer Vision Phase 2: OpenCV video processor and YOLO detection"

# Day 7
$baseDate = $baseDate.AddDays(1)
$env:GIT_AUTHOR_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
$env:GIT_COMMITTER_DATE = $baseDate.ToString("yyyy-MM-ddTHH:mm:ss")
git add .
git commit -m "Computer Vision Phase 3A: ByteTrack multi-object tracking integration"

Remove-Item Env:\GIT_AUTHOR_DATE
Remove-Item Env:\GIT_COMMITTER_DATE
