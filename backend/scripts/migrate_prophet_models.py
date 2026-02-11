#!/usr/bin/env python3
"""
Prophet Model Migration Script
Handles migration of pickled Prophet models that may have stan_backend attribute issues
"""

import os
import pickle
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

import pandas as pd
from prophet import Prophet

logger = logging.getLogger(__name__)


class ProphetModelMigrator:
    """
    Migrates old pickled Prophet models to be compatible with Prophet 1.1+
    Handles stan_backend attribute errors and missing attributes
    """
    
    def __init__(self, models_directory: str = "saved_models"):
        self.models_directory = Path(models_directory)
        self.models_directory.mkdir(exist_ok=True)
        self.migration_log = []
        
    def migrate_pickled_model(self, model_path: str) -> Dict[str, Any]:
        """
        Attempt to load and migrate a pickled Prophet model
        
        Args:
            model_path: Path to the pickled model file
            
        Returns:
            Dictionary with migration status and details
        """
        model_path = Path(model_path)
        migration_result = {
            "model_path": str(model_path),
            "migration_timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "error": None,
            "action_taken": None
        }
        
        try:
            # Try to load the pickled model
            with open(model_path, 'rb') as f:
                pickled_data = pickle.load(f)
            
            # Check if it's a Prophet model or contains one
            if isinstance(pickled_data, Prophet):
                model = pickled_data
                migration_result["action_taken"] = "direct_prophet_model"
            elif isinstance(pickled_data, dict) and 'model' in pickled_data:
                model = pickled_data['model']
                migration_result["action_taken"] = "dict_with_model_key"
            else:
                migration_result["status"] = "failed"
                migration_result["error"] = "Not a Prophet model or recognized format"
                self.migration_log.append(migration_result)
                return migration_result
            
            # Test if the model has stan_backend issues
            try:
                # Try to access potentially problematic attributes
                _ = hasattr(model, 'stan_backend')
                _ = model.predict(pd.DataFrame({'ds': [pd.Timestamp.now()], 'y': [1]}))
                
                migration_result["status"] = "success"
                migration_result["action_taken"] = "no_migration_needed"
                logger.info(f"Model {model_path} is compatible, no migration needed")
                
            except AttributeError as e:
                if 'stan_backend' in str(e):
                    logger.warning(f"Model {model_path} has stan_backend issue, attempting migration...")
                    migration_result = self._fix_stan_backend_issues(model, model_path, migration_result)
                else:
                    migration_result["status"] = "failed"
                    migration_result["error"] = f"AttributeError: {e}"
                    
        except Exception as e:
            migration_result["status"] = "failed"
            migration_result["error"] = f"Loading error: {e}"
            logger.error(f"Failed to migrate model {model_path}: {e}")
        
        self.migration_log.append(migration_result)
        return migration_result
    
    def _fix_stan_backend_issues(self, model: Prophet, model_path: Path, migration_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix stan_backend related issues in a Prophet model
        
        Args:
            model: The Prophet model with issues
            model_path: Path to the original model file
            migration_result: Current migration result dictionary
            
        Returns:
            Updated migration result
        """
        try:
            # Create a new model with the same parameters
            new_model = Prophet(
                yearly_seasonality=getattr(model, 'yearly_seasonality', True),
                weekly_seasonality=getattr(model, 'weekly_seasonality', False),
                daily_seasonality=getattr(model, 'daily_seasonality', False),
                changepoint_prior_scale=getattr(model, 'changepoint_prior_scale', 0.05),
                seasonality_mode=getattr(model, 'seasonality_mode', 'additive'),
                seasonality_prior_scale=getattr(model, 'seasonality_prior_scale', 10.0),
                holidays_prior_scale=getattr(model, 'holidays_prior_scale', 10.0),
                mcmc_samples=getattr(model, 'mcmc_samples', 0),
                interval_width=getattr(model, 'interval_width', 0.95),
                uncertainty_samples=getattr(model, 'uncertainty_samples', 1000)
            )
            
            # Copy fitted parameters if they exist
            if hasattr(model, 'history') and model.history is not None:
                try:
                    # Re-fit the model with the same data if available
                    new_model.fit(model.history)
                    migration_result["action_taken"] = "refitted_with_history"
                except Exception as refit_error:
                    logger.warning(f"Could not refit model with history: {refit_error}")
                    migration_result["action_taken"] = "created_new_model_params"
            
            # Save the migrated model
            backup_path = model_path.parent / f"{model_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{model_path.suffix}"
            model_path.rename(backup_path)
            
            with open(model_path, 'wb') as f:
                pickle.dump(new_model, f)
            
            migration_result["status"] = "success"
            migration_result["backup_path"] = str(backup_path)
            logger.info(f"Successfully migrated model {model_path}, backup saved to {backup_path}")
            
        except Exception as e:
            migration_result["status"] = "failed"
            migration_result["error"] = f"Migration error: {e}"
            logger.error(f"Failed to migrate model {model_path}: {e}")
        
        return migration_result
    
    def migrate_directory(self, pattern: str = "*.pkl") -> Dict[str, Any]:
        """
        Migrate all pickled models in a directory
        
        Args:
            pattern: File pattern to match (default: *.pkl)
            
        Returns:
            Summary of migration results
        """
        model_files = list(self.models_directory.glob(pattern))
        
        if not model_files:
            return {
                "total_files": 0,
                "successful_migrations": 0,
                "failed_migrations": 0,
                "files": [],
                "message": "No model files found"
            }
        
        results = []
        successful = 0
        failed = 0
        
        for model_file in model_files:
            result = self.migrate_pickled_model(model_file)
            results.append(result)
            
            if result["status"] == "success":
                successful += 1
            else:
                failed += 1
        
        return {
            "total_files": len(model_files),
            "successful_migrations": successful,
            "failed_migrations": failed,
            "files": results,
            "migration_summary": f"Migrated {successful}/{len(model_files)} models successfully"
        }
    
    def create_migration_report(self) -> str:
        """Generate a text report of all migrations performed"""
        if not self.migration_log:
            return "No migrations performed."
        
        report_lines = [
            "Prophet Model Migration Report",
            "=" * 40,
            f"Generated: {datetime.now().isoformat()}",
            f"Total migrations attempted: {len(self.migration_log)}",
            ""
        ]
        
        successful = sum(1 for log in self.migration_log if log["status"] == "success")
        failed = sum(1 for log in self.migration_log if log["status"] == "failed")
        
        report_lines.extend([
            f"Successful migrations: {successful}",
            f"Failed migrations: {failed}",
            ""
        ])
        
        for i, log in enumerate(self.migration_log, 1):
            report_lines.extend([
                f"Migration {i}:",
                f"  File: {log['model_path']}",
                f"  Status: {log['status']}",
                f"  Action: {log.get('action_taken', 'N/A')}",
            ])
            
            if log.get("error"):
                report_lines.append(f"  Error: {log['error']}")
            
            if log.get("backup_path"):
                report_lines.append(f"  Backup: {log['backup_path']}")
            
            report_lines.append("")
        
        return "\n".join(report_lines)


def main():
    """Run migration on default models directory"""
    import sys
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    models_dir = sys.argv[1] if len(sys.argv) > 1 else "saved_models"
    
    migrator = ProphetModelMigrator(models_dir)
    results = migrator.migrate_directory()
    
    # Handle case where no models are found
    if "migration_summary" not in results:
        print(results.get("message", "No migration performed"))
        return 0
    
    print(results["migration_summary"])
    
    if results["failed_migrations"] > 0:
        print(f"\n{results['failed_migrations']} migrations failed. Check logs for details.")
        sys.exit(1)
    else:
        print("\nAll migrations completed successfully!")
        return 0


if __name__ == "__main__":
    main()
