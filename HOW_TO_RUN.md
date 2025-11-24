# 🚀 FINAL SIMPLE INSTRUCTIONS

## Current Status
✅ Backend running on port 8000
✅ Frontend server running on port 3000

## How to Run and Test

### Step 1: Open Browser
Open your web browser and go to:
```
http://localhost:3000
```

### Step 2: Wait for Page to Load
You should see the "Hiver Copilot" interface

### Step 3: Type Query
In the search box, type:
```
How do I configure automations in Hiver?
```

### Step 4: Click Search
Click the blue "Search" button

### Step 5: Wait
- First time: Wait 10-15 seconds (model is loading)
- If you see an error about "RAG engine loading", click Search again
- Second time: Should work instantly

### Step 6: See Results
You should see:
- Confidence Score
- AI-Generated Answer
- 3 Retrieved Articles

## If It's Still Not Working

### Option 1: Check Browser Console
1. Press F12 in your browser
2. Go to Console tab
3. Look for error messages
4. Tell me what errors you see

### Option 2: Test API Directly
Open PowerShell and run:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health"
```

Should show:
```
status: healthy
rag_engine_initialized: true or false
```

## Current Servers Running
- Backend: `python main_simple.py` (port 8000)
- Frontend: `python -m http.server 3000` (port 3000)

## To Restart Everything
1. Close all terminals
2. Open new terminal:
```powershell
cd C:\Users\Hp\Downloads\HIVER_TASK3\backend
python main_simple.py
```
3. Open another terminal:
```powershell
cd C:\Users\Hp\Downloads\HIVER_TASK3
python -m http.server 3000
```
4. Open browser: `http://localhost:3000`

---

**Everything should be working now!** Just open `http://localhost:3000` in your browser.
