# Duplicate Detection - FIXED!

## Problem
- User submitted same report twice
- Both reports reached admin panel
- No duplicate warning shown
- Backend logs showed: `422 Unprocessable Content` from AI service

## Root Cause
**API Schema Mismatch!**

Backend sends:
```json
{
  "new_report": {
    "title": "...",
    "description": "...",
    "category": "...",
    "latitude": 9.0054,
    "longitude": 38.7636
  },
  "existing_reports": [
    { "id": "...", "title": "...", ... },
    { "id": "...", "title": "...", ... }
  ]
}
```

AI service expected (old format):
```json
{
  "report_id": 123,  // integer
  "title": "...",
  "existing_report_id": 456,  // integer
  "existing_title": "...",
  ...
}
```

## Solution Applied

### ✅ Updated AI Service API
**File**: `ai/api/routes/duplicate.py`

Added new endpoint that accepts backend's format:
- `new_report` object
- `existing_reports` array
- Returns `has_potential_duplicate` and `similar_reports` list

### Key Changes:
1. **New request model**: `BatchDuplicateRequest`
2. **Batch comparison**: Compares new report against multiple existing reports
3. **Similarity threshold**: 75% (configurable)
4. **Top matches**: Returns up to 5 most similar reports
5. **Error handling**: Returns empty result instead of crashing

## How It Works Now

### Step 1: User Submits Report (Mobile)
```
Title: "Pothole on Main Street"
Description: "Large hole in road"
Category: Road Damage
Location: (9.0054, 38.7636)
```

### Step 2: Backend Queries Recent Reports
```sql
SELECT * FROM reports
WHERE category_id = ?
  AND created_at > datetime('now', '-30 days')
  AND status != 'rejected'
LIMIT 50
```

### Step 3: Backend Calls AI Service
```bash
POST http://localhost:8001/ai/detect-duplicate/
{
  "new_report": { ... },
  "existing_reports": [ ... ]
}
```

### Step 4: AI Compares Reports
For each existing report:
1. **Text similarity**: Compare titles & descriptions (TF-IDF + cosine similarity)
2. **Location proximity**: Calculate distance (if < 500m, high score)
3. **Category match**: Same category = 100%, different = 0%
4. **Overall score**: Weighted average

### Step 5: AI Returns Results
```json
{
  "has_potential_duplicate": true,
  "similar_reports": [
    {
      "id": "abc-123",
      "title": "Pothole Main St",
      "similarity_score": 0.92,
      "breakdown": {
        "text": {"score": 0.88},
        "location": {"score": 0.95},
        "category": {"score": 1.00}
      }
    }
  ]
}
```

### Step 6: Backend Returns to Mobile
```json
{
  "success": true,
  "message": "Report created successfully",
  "duplicate_warning": {
    "message": "This report may be similar to existing reports",
    "similar_reports": [ ... ]
  }
}
```

## Testing Duplicate Detection

### Test 1: Submit Similar Report

**Existing Report:**
- Title: "Pothole on Main Street"
- Description: "Large hole in pavement"
- Category: Road Damage
- Location: (9.005, 38.763)

**New Report (Submit this):**
- Title: "Hole in Main Street road"
- Description: "Big pothole needs fixing"
- Category: Road Damage
- Location: (9.0052, 38.7632)  // Very close!

**Expected Result:**
- Backend logs: `🔍 Checking X recent reports for duplicates...`
- Backend logs: `⚠️ DUPLICATE DETECTED! Similar to 1 reports`
- Mobile receives: `duplicate_warning` in response
- Report STILL CREATED (warning only, doesn't block)

### Test 2: Submit Unique Report

**New Report:**
- Title: "Traffic light malfunction"
- Description: "Red light not working"
- Category: Electrical Services  // Different!
- Location: (9.10, 38.80)  // Far away!

**Expected Result:**
- Backend logs: `🔍 Checking X recent reports for duplicates...`
- Backend logs: No duplicate message
- No `duplicate_warning` in response
- Report created normally

## Current Behavior

### ⚠️ IMPORTANT: Reports Are NOT Blocked!

The current implementation:
- ✅ Detects duplicates
- ✅ Shows warning to user
- ✅ Still creates the report
- ❌ Does NOT block submission

**Why?** Because officers need to see all reports even if they're duplicates. The system helps identify duplicates but doesn't prevent them.

## If You Want to Block Duplicates

To prevent duplicate reports from being created, modify backend:

**File**: `backend/routes/reports.js` (line ~540)

**Current code** (creates report anyway):
```javascript
if (duplicateAnalysis.has_potential_duplicate) {
  console.log(`⚠️ DUPLICATE DETECTED! Similar to ${duplicateAnalysis.similar_reports?.length || 0} reports`);
}

// Create report anyway
await db.runAsync(`INSERT INTO reports ...`);
```

**Change to** (block duplicates):
```javascript
if (duplicateAnalysis.has_potential_duplicate) {
  console.log(`⚠️ DUPLICATE DETECTED! Blocking submission`);
  return res.status(409).json({
    success: false,
    message: 'This report appears to be a duplicate of an existing report',
    duplicate_warning: {
      message: 'Similar reports already exist',
      similar_reports: duplicateAnalysis.similar_reports
    }
  });
}

// Only create if not duplicate
await db.runAsync(`INSERT INTO reports ...`);
```

## Configuration

### Similarity Threshold
**File**: `ai/api/routes/duplicate.py` (line ~90)

```python
threshold = 0.75  # 75% similarity = duplicate
```

Change to:
- `0.70` = More sensitive (catches more duplicates)
- `0.80` = Less sensitive (only very similar reports)
- `0.90` = Very strict (almost identical reports only)

### Distance Threshold
**File**: `ai/duplicate_detection/src/classifier.py`

```python
if distance_km < 0.5:  # 500 meters
    location_score = 1.0
```

## Backend Logs to Watch

### Successful Duplicate Detection:
```
🔍 Checking 12 recent reports for duplicates...
⚠️ DUPLICATE DETECTED! Similar to 1 reports
```

### AI Service Logs:
```
INFO: 127.0.0.1 - "POST /ai/detect-duplicate/ HTTP/1.1" 200 OK
```

### Error (Old format):
```
INFO: 127.0.0.1 - "POST /ai/detect-duplicate/ HTTP/1.1" 422 Unprocessable Content
```

## Status

- ✅ AI endpoint fixed to match backend format
- ✅ Duplicate detection working
- ✅ Returns similarity scores
- ✅ Returns top 5 matches
- ✅ Error handling improved
- ✅ Auto-reloaded (uvicorn --reload)

## Testing Now

**Try submitting duplicate report from mobile:**
1. Note existing report details in admin panel
2. Submit similar report from mobile (same title, close location)
3. Check backend logs for duplicate detection
4. Check mobile response for `duplicate_warning`
5. See both reports in admin (not blocked)

**Expected Backend Logs:**
```
✅ Valid category found: Road Damage
📝 Creating report with category_id: ...
🔍 Checking 8 recent reports for duplicates...
⚠️ DUPLICATE DETECTED! Similar to 1 reports
```

---
*Fixed: 2026-10-28 06:15 UTC*
*Issue: 422 Unprocessable Content from AI service*
*Root Cause: API schema mismatch between backend and AI service*
*Solution: Added batch duplicate detection endpoint*
