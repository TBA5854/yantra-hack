# Flutter Web Integration - Deployment Guide

## Overview

The Flutter web app connects to the ML Risk API (`localhost:8000`) to display real-time risk predictions with SHAP explanations.

---

## Setup

### 1. Install Dependencies

```bash
cd flutter
flutter pub get
```

### 2. Configure API Endpoint

Edit `lib/config/api_config.dart` if your API is not on `localhost:8000`:

```dart
static const String baseUrl = 'http://localhost:8000';
```

### 3. Build and Run

```bash
# Development mode (hot reload)
flutter run -d chrome --web-port 3000

# Production build
flutter build web
```

---

## Features Integrated

### Command Center Page

**ML Enhancements:**
- ✅ ML prediction badge (indicates when ML is active)
- ✅ Risk rating display (AAA, AA, A, B, C)
- ✅ Ensemble score visualization

**Location:** `lib/pages/web/screens/command_center_page.dart`

### Stress Breakdown Page

**ML Enhancements:**
- ✅ SHAP feature contribution card
- ✅ Top 5 features with impact bars
- ✅ Color-coded (red = increases risk, green = reduces risk)

**Location:** `lib/pages/web/screens/stress_breakdown_page.dart`

---

## Data Flow

```
FastAPI Backend (:8000)
  ↓
HttpRiskRepository (HTTP GET /risk/current)
  ↓
RiskState Model (with ML fields)
  ↓
RiskNotifierProvider (Riverpod)  
  ↓
Web Pages (Command Center, Stress Breakdown)
```

---

## API Integration

### Repository Implementation

**File:** `lib/data/repositories/risk_repository.dart`

```dart
// Real API mode (default)
HttpRiskRepository(baseUrl: 'http://localhost:8000')

// Mock mode (for testing)
MockRiskRepository()
```

Switch between modes using environment variable:
```bash
flutter run -d chrome --dart-define=USE_REAL_API=true
```

### Polling vs WebSocket

Currently uses **HTTP polling** (5-second intervals):
```dart
static const Duration refreshInterval = Duration(seconds: 5);
```

TODO: Implement WebSocket connection to `/ws/risk` for real-time updates.

---

## UI Components

### SHAP Explainability Card

**File:** `lib/pages/web/widgets/shap_explainability_card.dart`

**Features:**
- Displays top 5 ML features
- Contribution percentage bars
- Human-readable explanations
- Color-coded impact (positive/negative)

**Usage:**
```dart
ShapExplainabilityCard(
  explainability: riskState.explainability,
)
```

---

## Testing

### Run with Mock Data
```bash
flutter run -d chrome --dart-define=USE_REAL_API=false
```

### Run with Live API
```bash
# Ensure FastAPI is running on port 8000
flutter run -d chrome --dart-define=USE_REAL_API=true
```

---

## Next Steps

1. **WebSocket Integration**: Replace HTTP polling with WebSocket for < 100ms latency
2. **Error Handling**: Add retry logic and offline mode
3. **Caching**: Implement local caching for historical data
4. **Charts**: Add historical risk timeline from `/risk/history`
5. **Alerts**: Display on-chain alerts from `/alerts`

---

## Troubleshooting

### CORS Errors

If you see CORS errors, ensure FastAPI has CORS middleware configured:

```python
# backend/src/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Flutter web port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Not Connecting

1. Check FastAPI is running: `curl http://localhost:8000/health`
2. Check browser console for network errors
3. Verify `api_config.dart` has correct baseUrl

### ML Data Not Showing

1. Ensure `mlEnabled` is `true` in API response
2. Check `explainability` field is present
3. Verify SHAP calculations in backend

---

## Production Deployment

### Build for Production

```bash
flutter build web --release
```

Output: `build/web/`

### Deploy to Static Hosting

```bash
# Firebase Hosting
firebase deploy --only hosting

# Nginx
cp -r build/web/* /var/www/atlas/

# AWS S3
aws s3 sync build/web/ s3://your-bucket/
```

### Environment Variables

Set API URL for production:

```bash
flutter build web --dart-define=API_BASE_URL=https://api.yourdomain.com
```

---

**Status**: Flutter web integration complete. Ready for real-time ML predictions with SHAP explanations.
