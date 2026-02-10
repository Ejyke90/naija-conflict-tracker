'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { AlertTriangle, Database, Upload, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { motion } from 'framer-motion';

interface DataStatus {
  totalIncidents: number;
  yearlyBreakdown: Array<{
    year: number;
    incidents: number;
    fatalities: number;
  }>;
  recentMonths: Array<{
    month: string;
    incidents: number;
    states_affected: number;
  }>;
  total_statistics?: {
    total_states: number;
    total_lgas: number;
    date_range: {
      earliest: string;
      latest: string;
    };
  };
  lastUpdated?: string;
}

interface RestorationStatus {
  status: 'idle' | 'restoring' | 'success' | 'error';
  message: string;
  progress?: number;
  totalRecords?: number;
  processedRecords?: number;
}

export default function DataManagementPanel() {
  const [dataStatus, setDataStatus] = useState<DataStatus | null>(null);
  const [restorationStatus, setRestorationStatus] = useState<RestorationStatus>({
    status: 'idle',
    message: ''
  });
  const [isLoading, setIsLoading] = useState(false);

  // Check current data status
  const checkDataStatus = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/v1/data-management/verify-data-integrity');
      
      if (response.ok) {
        const data = await response.json();
        setDataStatus(data);
      } else {
        console.error('Failed to check data status');
      }
    } catch (error) {
      console.error('Error checking data status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Restore data from SQL file
  const restoreData = async (truncateExisting: boolean = true) => {
    try {
      setRestorationStatus({ status: 'restoring', message: 'Starting data restoration...' });
      
      const response = await fetch('/api/v1/data-management/restore-from-sql', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          truncate_existing: truncateExisting,
          batch_size: 1000
        })
      });

      const result = await response.json();

      if (response.ok) {
        setRestorationStatus({
          status: 'success',
          message: result.message,
          totalRecords: result.total_records,
          processedRecords: result.processed_records
        });
        
        // Refresh data status after successful restoration
        setTimeout(checkDataStatus, 2000);
      } else {
        setRestorationStatus({
          status: 'error',
          message: result.detail || 'Restoration failed'
        });
      }
    } catch (error) {
      setRestorationStatus({
        status: 'error',
        message: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    }
  };

  // Create backup before restoration
  const createBackupAndRestore = async () => {
    try {
      setRestorationStatus({ status: 'restoring', message: 'Creating backup...' });
      
      // Create backup first
      const backupResponse = await fetch('/api/v1/data-management/create-backup', {
        method: 'POST'
      });

      if (backupResponse.ok) {
        const backupResult = await backupResponse.json();
        setRestorationStatus({ 
          status: 'restoring', 
          message: `Backup created: ${backupResult.backup_file}. Starting restoration...` 
        });
        
        // Now restore data
        await restoreData(true);
      } else {
        setRestorationStatus({
          status: 'error',
          message: 'Failed to create backup'
        });
      }
    } catch (error) {
      setRestorationStatus({
        status: 'error',
        message: `Backup failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    }
  };

  useEffect(() => {
    checkDataStatus();
  }, []);

  const getDataHealthStatus = () => {
    if (!dataStatus) return 'unknown';
    
    const totalIncidents = dataStatus.totalIncidents;
    const hasRecentData = dataStatus.recentMonths.some(month => 
      parseInt(month.month.split('-')[0]) >= 2024 && month.incidents > 50
    );
    
    if (totalIncidents < 100) return 'critical';
    if (totalIncidents < 1000) return 'warning';
    if (!hasRecentData) return 'stale';
    return 'healthy';
  };

  const healthStatus = getDataHealthStatus();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Data Management</h2>
          <p className="text-muted-foreground">
            Emergency data restoration and management for Nigeria Conflict Tracker
          </p>
        </div>
        <Button onClick={checkDataStatus} disabled={isLoading} variant="outline">
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh Status
        </Button>
      </div>

      {/* Data Status Overview */}
      {dataStatus && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className={`border-l-4 ${
            healthStatus === 'healthy' ? 'border-l-green-500' :
            healthStatus === 'warning' ? 'border-l-yellow-500' :
            healthStatus === 'stale' ? 'border-l-orange-500' :
            'border-l-red-500'
          }`}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Current Data Status
                <Badge variant={
                  healthStatus === 'healthy' ? 'default' :
                  healthStatus === 'warning' ? 'secondary' :
                  healthStatus === 'stale' ? 'outline' :
                  'destructive'
                }>
                  {healthStatus.toUpperCase()}
                </Badge>
              </CardTitle>
              <CardDescription>
                Total incidents in database: {dataStatus.totalIncidents.toLocaleString()}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Yearly Breakdown */}
                <div>
                  <h4 className="font-semibold mb-2">Yearly Breakdown</h4>
                  <div className="space-y-1">
                    {dataStatus.yearlyBreakdown.map((year) => (
                      <div key={year.year} className="flex justify-between text-sm">
                        <span>{year.year}:</span>
                        <span className={year.incidents < 100 ? 'text-red-600 font-semibold' : ''}>
                          {year.incidents.toLocaleString()} incidents
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recent Months */}
                <div>
                  <h4 className="font-semibold mb-2">Recent Activity</h4>
                  <div className="space-y-1">
                    {dataStatus.recentMonths.slice(0, 6).map((month) => (
                      <div key={month.month} className="flex justify-between text-sm">
                        <span>{month.month}:</span>
                        <span className={month.incidents < 10 ? 'text-red-600 font-semibold' : ''}>
                          {month.incidents} incidents
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Data Quality Indicators */}
                <div>
                  <h4 className="font-semibold mb-2">Data Quality</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      {healthStatus === 'healthy' ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-red-500" />
                      )}
                      <span className="text-sm">
                        {healthStatus === 'healthy' ? 'Data appears complete' :
                         healthStatus === 'warning' ? 'Limited data available' :
                         healthStatus === 'stale' ? 'No recent data' :
                         'Critical data shortage'}
                      </span>
                    </div>
                    
                    {dataStatus.total_statistics && (
                      <div className="text-sm space-y-1">
                        <div>States: {dataStatus.total_statistics.total_states}</div>
                        <div>LGAs: {dataStatus.total_statistics.total_lgas}</div>
                        <div>Date Range: {dataStatus.total_statistics.date_range?.earliest} to {dataStatus.total_statistics.date_range?.latest}</div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Restoration Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Emergency Data Restoration
          </CardTitle>
          <CardDescription>
            Restore complete dataset from SQL file. This will fix missing data issues.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Warning Alert */}
          {healthStatus !== 'healthy' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-red-50 border border-red-200 rounded-lg p-4"
            >
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-red-800 mb-1">Data Issue Detected</h4>
                  <p className="text-sm text-red-700">
                    The database appears to be missing significant conflict data. 
                    The source SQL file contains {dataStatus?.totalIncidents || 0}+ records, 
                    but the database only has {dataStatus?.totalIncidents || 0} records.
                  </p>
                  <p className="text-sm text-red-700 mt-1">
                    Restoration from the SQL file is recommended to fix this issue.
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Restoration Status */}
          {restorationStatus.status !== 'idle' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className={`rounded-lg p-4 ${
                restorationStatus.status === 'success' ? 'bg-green-50 border border-green-200' :
                restorationStatus.status === 'error' ? 'bg-red-50 border border-red-200' :
                'bg-blue-50 border border-blue-200'
              }`}
            >
              <div className="flex items-center gap-3">
                {restorationStatus.status === 'restoring' && (
                  <RefreshCw className="h-5 w-5 text-blue-600 animate-spin" />
                )}
                {restorationStatus.status === 'success' && (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                )}
                {restorationStatus.status === 'error' && (
                  <AlertCircle className="h-5 w-5 text-red-600" />
                )}
                <div>
                  <p className={`font-semibold ${
                    restorationStatus.status === 'success' ? 'text-green-800' :
                    restorationStatus.status === 'error' ? 'text-red-800' :
                    'text-blue-800'
                  }`}>
                    {restorationStatus.status === 'success' ? 'Restoration Complete' :
                     restorationStatus.status === 'error' ? 'Restoration Failed' :
                     'Restoration in Progress...'}
                  </p>
                  <p className={`text-sm ${
                    restorationStatus.status === 'success' ? 'text-green-700' :
                    restorationStatus.status === 'error' ? 'text-red-700' :
                    'text-blue-700'
                  }`}>
                    {restorationStatus.message}
                  </p>
                  {restorationStatus.totalRecords && (
                    <p className="text-sm text-blue-700 mt-1">
                      Processed {restorationStatus.processedRecords} of {restorationStatus.totalRecords} records
                    </p>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={createBackupAndRestore}
              disabled={restorationStatus.status === 'restoring'}
              className="flex-1"
            >
              <Upload className="h-4 w-4 mr-2" />
              {restorationStatus.status === 'restoring' ? 'Restoring...' : 'Restore Complete Dataset'}
            </Button>
            
            <Button
              onClick={() => restoreData(false)}
              disabled={restorationStatus.status === 'restoring'}
              variant="outline"
            >
              Restore Without Truncating
            </Button>
          </div>

          <div className="text-xs text-muted-foreground">
            <p><strong>Note:</strong> This will restore data from the SQL file located on the server.</p>
            <p>The restoration process may take several minutes depending on dataset size.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
