# NLP Pipeline Fixes Summary

## Issues Fixed

### 1. **NameError: name 'text' is not defined**
- **File**: `/backend/app/nlp/groq_extractor.py`
- **Line**: 350-352 in `_calculate_confidence_score` method
- **Fix**: Changed `text` to `raw_text` in the confidence score calculation
- **Code Change**:
  ```python
  # Before (incorrect)
  if len(text) > 500:
      score += 0.05
  
  # After (correct)
  if len(raw_text) > 500:
      score += 0.05
  ```

### 2. **429 Too Many Requests (Rate Limiting)**
- **File**: `/backend/app/nlp/groq_extractor.py`
- **Fixes Applied**:
  - Added `time` and `random` imports for delay functionality
  - Added delay between API calls in `batch_extract` method (2-4 seconds)
  - Added retry logic with exponential backoff in `extract_event` method
  - Retry attempts: 3 with backoff times of 5s, 10s, 20s

### 3. **Geocoding Data Not Loading**
- **File**: `/backend/app/nlp/pipeline.py`
- **Issue**: Geocoder was using relative path "data" instead of absolute path
- **Fix**: 
  - Calculate absolute path to data directory using `Path(__file__).parent.parent.parent`
  - Pass absolute path to `NigerianGeocoder` constructor
  - Also fixed output directory path to use absolute path

### 4. **Village Data Loading Error**
- **File**: `/backend/app/nlp/geocoding.py`
- **Issue**: `village_data` was initialized as dict but used as list
- **Fix**: Restructured village data loading to use nested dictionary:
  ```python
  village_data = {
      "state": {
          "lga": {
              "village": {"lat": x, "lng": y}
          }
      }
  }
  ```

## Testing

A test script `/backend/test_pipeline_fixes.py` was created to verify:
- Geocoder loads data correctly (8 states with LGA data)
- Extractor has retry parameter for rate limiting
- Pipeline initializes with correct paths

## Usage

To run the pipeline after fixes:
```bash
cd backend
python3 -m app.nlp.pipeline
```

## Expected Improvements

1. **No more NameError crashes** - All variables properly defined
2. **Reduced rate limit errors** - Built-in delays and retry logic
3. **Proper geocoding** - Location data loads correctly for validation
4. **Better error handling** - Graceful retries on rate limit hits

## Additional Recommendations

1. **Monitor API Usage**: Keep track of Groq API usage to stay within limits
2. **Adjust Delays**: If still hitting rate limits, increase delays between calls
3. **Logging**: Monitor logs for retry patterns to optimize timing
4. **Consider Caching**: Cache recent extractions to avoid re-processing same articles
