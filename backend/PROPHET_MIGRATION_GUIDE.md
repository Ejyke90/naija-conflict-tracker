# Prophet Model Migration Guide

## Overview

This guide explains how to handle Prophet model migration issues, particularly the `stan_backend` attribute error that occurs when loading older pickled models with Prophet 1.1+.

## Problem

When upgrading to Prophet 1.1+ with cmdstanpy backend, older pickled models may cause:
```
AttributeError: 'Prophet' object has no attribute 'stan_backend'
```

## Solutions

### 1. Automatic Migration (Recommended)

The updated `ProphetForecaster` class now includes automatic model migration:

```python
from app.ml.prophet_forecaster import ProphetForecaster

# This will automatically load existing models or train new ones if migration fails
forecaster = ProphetForecaster()
result = forecaster.forecast(
    state="Borno",
    weeks_ahead=4,
    use_cached_model=True  # Enables automatic model loading/saving
)
```

### 2. Manual Migration Script

Use the migration script for bulk model updates:

```bash
# Migrate all models in default directory
python3 scripts/migrate_prophet_models.py

# Migrate models in specific directory
python3 scripts/migrate_prophet_models.py /path/to/models
```

### 3. Programmatic Migration

```python
from scripts.migrate_prophet_models import ProphetModelMigrator

migrator = ProphetModelMigrator("saved_models")
results = migrator.migrate_directory()

print(f"Migrated {results['successful_migrations']}/{results['total_files']} models")
```

## New Features

### Enhanced ProphetForecaster

- **Automatic Model Caching**: Models are automatically saved and loaded
- **Migration Handling**: Old models are automatically migrated on load
- **Fallback Training**: If migration fails, models are retrained automatically
- **Model Management**: List, inspect, and manage saved models

### Key Methods

```python
# Load or train model with automatic fallback
forecaster.get_or_train_model(model_name="state_borno", df=data)

# Save model with metadata
forecaster.save_model("my_model", include_metadata=True)

# Load model with migration handling
success = forecaster.load_model("my_model", force_retrain_on_failure=True)

# List all saved models
models = forecaster.list_saved_models()
```

## Model Storage Format

New models are saved in a migration-safe format:

```python
{
    "model": Prophet(...),  # The actual Prophet model
    "saved_at": "2026-02-10T19:30:36.736516",
    "prophet_version": "1.3.0",
    "last_forecast": [...]  # Optional metadata
}
```

## Dependencies

Ensure your `requirements.txt` includes:

```
prophet==1.1.4
cmdstanpy>=1.0.0
```

## Troubleshooting

### Model Loading Fails

1. Check model compatibility:
```python
from app.ml.prophet_forecaster import ProphetForecaster
forecaster = ProphetForecaster()
models = forecaster.list_saved_models()
print(models)
```

2. Run migration manually:
```bash
python3 scripts/migrate_prophet_models.py
```

3. Force retraining:
```python
result = forecaster.forecast(state="Borno", use_cached_model=False)
```

### Migration Script Fails

1. Check file permissions on models directory
2. Ensure sufficient disk space for backups
3. Verify Prophet and cmdstanpy versions

## Best Practices

1. **Use Model Caching**: Enable `use_cached_model=True` for better performance
2. **Regular Migration**: Run migration script after Prophet upgrades
3. **Backup Models**: Keep backups of critical models before migration
4. **Monitor Logs**: Check migration logs for failed models
5. **Version Tracking**: Model metadata includes Prophet version for compatibility

## Testing

Test the migration functionality:

```bash
python3 test_prophet_migration.py
```

This will:
- Create and save a test model
- Test model loading with migration
- Test the migration script
- Verify forecast functionality

## Migration Log

All migrations are logged with:
- Timestamp
- Model path
- Migration status
- Action taken
- Any errors encountered

Check logs for troubleshooting:
```python
migrator = ProphetModelMigrator("saved_models")
report = migrator.create_migration_report()
print(report)
```
