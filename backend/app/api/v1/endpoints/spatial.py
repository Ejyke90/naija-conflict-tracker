from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.db.database import get_db
from app.models.conflict import ConflictEvent
from app.models.location import Location

router = APIRouter()

@router.get("/proximity/{lat}/{lng}")
async def get_conflicts_by_proximity(
    lat: float,
    lng: float,
    radius_km: float = Query(50, description="Radius in kilometers"),
    limit: int = Query(100, description="Maximum number of results"),
    days_back: int = Query(30, description="Days to look back"),
    db: Session = Depends(get_db)
):
    """
    Find all conflicts within a specified radius of a point.
    Example: Find all incidents within 50km of Abuja
    """
    try:
        # Calculate date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days_back)
        
        # PostGIS spatial query using ST_DWithin for proximity search
        query = text("""
            SELECT 
                c.id,
                c.event_type,
                c.fatalities,
                c.date_occurred,
                c.description,
                l.name as location_name,
                l.state,
                l.lga,
                l.ward,
                ST_X(c.coordinates) as longitude,
                ST_Y(c.coordinates) as latitude,
                ST_Distance(
                    c.coordinates::geography,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography
                ) / 1000 as distance_km
            FROM conflicts c
            JOIN locations l ON c.location_id = l.id
            WHERE c.coordinates IS NOT NULL
            AND c.date_occurred >= :date_threshold
            AND ST_DWithin(
                c.coordinates::geography,
                ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                :radius_m
            )
            ORDER BY distance_km ASC
            LIMIT :limit
        """)
        
        result = db.execute(query, {
            'lat': lat,
            'lng': lng,
            'radius_m': radius_km * 1000,  # Convert km to meters
            'date_threshold': date_threshold,
            'limit': limit
        })
        
        conflicts = []
        for row in result:
            conflicts.append({
                'id': row.id,
                'event_type': row.event_type,
                'fatalities': row.fatalities,
                'date_occurred': row.date_occurred.isoformat() if row.date_occurred else None,
                'description': row.description,
                'location': {
                    'name': row.location_name,
                    'state': row.state,
                    'lga': row.lga,
                    'ward': row.ward,
                    'coordinates': {
                        'lat': row.latitude,
                        'lng': row.longitude
                    }
                },
                'distance_km': round(row.distance_km, 2)
            })
        
        return {
            'center': {'lat': lat, 'lng': lng},
            'radius_km': radius_km,
            'total_found': len(conflicts),
            'conflicts': conflicts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spatial query failed: {str(e)}")

@router.get("/diffusion-index")
async def calculate_diffusion_index(
    bbox: str = Query(..., description="Bounding box as 'minLng,minLat,maxLng,maxLat'"),
    grid_size_km: float = Query(10, description="Grid cell size in kilometers"),
    days_back: int = Query(30, description="Days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Calculate ACLED-style Conflict Diffusion Index using grid methodology.
    Returns percentage of grid cells experiencing violence.
    """
    try:
        # Parse bounding box
        min_lng, min_lat, max_lng, max_lat = map(float, bbox.split(','))
        
        # Calculate date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days_back)
        
        # Create grid and count conflicts per cell
        query = text("""
            WITH grid AS (
                SELECT 
                    i * :grid_size + :min_lng as grid_lng,
                    j * :grid_size + :min_lat as grid_lat,
                    ST_MakeEnvelope(
                        i * :grid_size + :min_lng,
                        j * :grid_size + :min_lat,
                        (i + 1) * :grid_size + :min_lng,
                        (j + 1) * :grid_size + :min_lat,
                        4326
                    ) as cell_geom
                FROM generate_series(
                    0, 
                    CAST((:max_lng - :min_lng) / :grid_size AS INTEGER)
                ) i
                CROSS JOIN generate_series(
                    0, 
                    CAST((:max_lat - :min_lat) / :grid_size AS INTEGER)
                ) j
            ),
            conflict_cells AS (
                SELECT 
                    g.grid_lng,
                    g.grid_lat,
                    COUNT(c.id) as conflict_count,
                    SUM(c.fatalities) as total_fatalities
                FROM grid g
                LEFT JOIN conflicts c ON ST_Within(c.coordinates, g.cell_geom)
                    AND c.date_occurred >= :date_threshold
                GROUP BY g.grid_lng, g.grid_lat, g.cell_geom
            )
            SELECT 
                COUNT(*) as total_cells,
                COUNT(CASE WHEN conflict_count > 0 THEN 1 END) as affected_cells,
                ROUND(
                    (COUNT(CASE WHEN conflict_count > 0 THEN 1 END)::float / COUNT(*)::float) * 100, 
                    2
                ) as diffusion_index,
                SUM(conflict_count) as total_conflicts,
                SUM(total_fatalities) as total_fatalities,
                json_agg(
                    json_build_object(
                        'lng', grid_lng,
                        'lat', grid_lat,
                        'conflicts', conflict_count,
                        'fatalities', total_fatalities
                    )
                ) as grid_data
            FROM conflict_cells
        """)
        
        # Convert km to degrees (approximate)
        grid_size_deg = grid_size_km / 111.0  # 1 degree ≈ 111 km
        
        result = db.execute(query, {
            'min_lng': min_lng,
            'min_lat': min_lat,
            'max_lng': max_lng,
            'max_lat': max_lat,
            'grid_size': grid_size_deg,
            'date_threshold': date_threshold
        }).fetchone()
        
        return {
            'analysis_period': f"Last {days_back} days",
            'grid_size_km': grid_size_km,
            'bounding_box': {
                'min_lng': min_lng, 'min_lat': min_lat,
                'max_lng': max_lng, 'max_lat': max_lat
            },
            'metrics': {
                'total_cells': result.total_cells,
                'affected_cells': result.affected_cells,
                'diffusion_index': result.diffusion_index,
                'total_conflicts': result.total_conflicts,
                'total_fatalities': result.total_fatalities
            },
            'grid_data': result.grid_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diffusion index calculation failed: {str(e)}")

@router.get("/buffer-analysis/{lat}/{lng}")
async def calculate_buffer_exposure(
    lat: float,
    lng: float,
    buffer_km: float = Query(2, description="Buffer radius in kilometers (2km or 5km)"),
    db: Session = Depends(get_db)
):
    """
    Calculate population exposure within buffer zones around conflict points.
    Uses WorldPop methodology for population estimates.
    """
    try:
        # Create buffer zone and calculate exposure
        query = text("""
            WITH buffer_zone AS (
                SELECT ST_Buffer(
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                    :buffer_m
                )::geometry as buffer_geom
            ),
            nearby_conflicts AS (
                SELECT 
                    c.id,
                    c.event_type,
                    c.fatalities,
                    c.date_occurred,
                    l.name as location_name,
                    l.state,
                    l.population_estimate,
                    ST_Distance(
                        c.coordinates::geography,
                        ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography
                    ) / 1000 as distance_km
                FROM conflicts c
                JOIN locations l ON c.location_id = l.id
                CROSS JOIN buffer_zone b
                WHERE c.coordinates IS NOT NULL
                AND ST_Within(c.coordinates, b.buffer_geom)
            )
            SELECT 
                COUNT(*) as conflicts_in_buffer,
                SUM(fatalities) as total_fatalities,
                AVG(l.population_estimate) as avg_population_estimate,
                json_agg(
                    json_build_object(
                        'id', nc.id,
                        'event_type', nc.event_type,
                        'fatalities', nc.fatalities,
                        'location', nc.location_name,
                        'state', nc.state,
                        'distance_km', ROUND(nc.distance_km::numeric, 2)
                    )
                ) as conflicts
            FROM nearby_conflicts nc
            JOIN locations l ON l.name = nc.location_name
        """)
        
        result = db.execute(query, {
            'lat': lat,
            'lng': lng,
            'buffer_m': buffer_km * 1000
        }).fetchone()
        
        # Estimate population exposure (simplified calculation)
        # In production, this would integrate with WorldPop raster data
        estimated_population = result.avg_population_estimate or 50000  # Default estimate
        exposure_factor = min(1.0, buffer_km / 10.0)  # Adjust based on buffer size
        exposed_population = int(estimated_population * exposure_factor)
        
        return {
            'center': {'lat': lat, 'lng': lng},
            'buffer_km': buffer_km,
            'analysis': {
                'conflicts_in_buffer': result.conflicts_in_buffer or 0,
                'total_fatalities': result.total_fatalities or 0,
                'estimated_exposed_population': exposed_population,
                'risk_level': 'high' if (result.conflicts_in_buffer or 0) > 5 else 
                           'medium' if (result.conflicts_in_buffer or 0) > 2 else 'low'
            },
            'conflicts': result.conflicts if result.conflicts and result.conflicts[0] else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Buffer analysis failed: {str(e)}")

@router.get("/hierarchical-data/{zoom_level}")
async def get_hierarchical_data(
    zoom_level: int,
    bbox: str = Query(..., description="Bounding box as 'minLng,minLat,maxLng,maxLat'"),
    db: Session = Depends(get_db)
):
    """
    Get hierarchical conflict data based on zoom level:
    - Zoom 0-6: State-level heatmap data
    - Zoom 7-10: LGA-level cluster data  
    - Zoom 11+: Ward-level individual markers
    """
    try:
        min_lng, min_lat, max_lng, max_lat = map(float, bbox.split(','))
        
        if zoom_level <= 6:
            # State-level aggregation for heatmap
            query = text("""
                SELECT 
                    l.state,
                    COUNT(c.id) as conflict_count,
                    SUM(c.fatalities) as total_fatalities,
                    AVG(ST_X(c.coordinates)) as center_lng,
                    AVG(ST_Y(c.coordinates)) as center_lat,
                    MAX(c.date_occurred) as latest_incident
                FROM conflicts c
                JOIN locations l ON c.location_id = l.id
                WHERE c.coordinates IS NOT NULL
                AND ST_X(c.coordinates) BETWEEN :min_lng AND :max_lng
                AND ST_Y(c.coordinates) BETWEEN :min_lat AND :max_lat
                GROUP BY l.state
                HAVING COUNT(c.id) > 0
                ORDER BY conflict_count DESC
            """)
            
            result = db.execute(query, {
                'min_lng': min_lng, 'min_lat': min_lat,
                'max_lng': max_lng, 'max_lat': max_lat
            })
            
            return {
                'zoom_level': zoom_level,
                'data_type': 'state_heatmap',
                'features': [
                    {
                        'state': row.state,
                        'conflict_count': row.conflict_count,
                        'total_fatalities': row.total_fatalities,
                        'center': {'lat': row.center_lat, 'lng': row.center_lng},
                        'latest_incident': row.latest_incident.isoformat() if row.latest_incident else None,
                        'intensity': min(1.0, row.conflict_count / 50.0)  # Normalize for heatmap
                    }
                    for row in result
                ]
            }
            
        elif zoom_level <= 10:
            # LGA-level clustering
            query = text("""
                SELECT 
                    l.state,
                    l.lga,
                    COUNT(c.id) as conflict_count,
                    SUM(c.fatalities) as total_fatalities,
                    AVG(ST_X(c.coordinates)) as center_lng,
                    AVG(ST_Y(c.coordinates)) as center_lat,
                    array_agg(DISTINCT c.event_type) as event_types
                FROM conflicts c
                JOIN locations l ON c.location_id = l.id
                WHERE c.coordinates IS NOT NULL
                AND ST_X(c.coordinates) BETWEEN :min_lng AND :max_lng
                AND ST_Y(c.coordinates) BETWEEN :min_lat AND :max_lat
                GROUP BY l.state, l.lga
                HAVING COUNT(c.id) > 0
                ORDER BY conflict_count DESC
            """)
            
            result = db.execute(query, {
                'min_lng': min_lng, 'min_lat': min_lat,
                'max_lng': max_lng, 'max_lat': max_lat
            })
            
            return {
                'zoom_level': zoom_level,
                'data_type': 'lga_clusters',
                'features': [
                    {
                        'state': row.state,
                        'lga': row.lga,
                        'conflict_count': row.conflict_count,
                        'total_fatalities': row.total_fatalities,
                        'center': {'lat': row.center_lat, 'lng': row.center_lng},
                        'event_types': row.event_types,
                        'cluster_size': min(50, max(10, row.conflict_count * 2))
                    }
                    for row in result
                ]
            }
            
        else:
            # Ward-level individual markers
            query = text("""
                SELECT 
                    c.id,
                    c.event_type,
                    c.fatalities,
                    c.date_occurred,
                    c.description,
                    l.name as location_name,
                    l.state,
                    l.lga,
                    l.ward,
                    ST_X(c.coordinates) as longitude,
                    ST_Y(c.coordinates) as latitude
                FROM conflicts c
                JOIN locations l ON c.location_id = l.id
                WHERE c.coordinates IS NOT NULL
                AND ST_X(c.coordinates) BETWEEN :min_lng AND :max_lng
                AND ST_Y(c.coordinates) BETWEEN :min_lat AND :max_lat
                ORDER BY c.date_occurred DESC
                LIMIT 500
            """)
            
            result = db.execute(query, {
                'min_lng': min_lng, 'min_lat': min_lat,
                'max_lng': max_lng, 'max_lat': max_lat
            })
            
            return {
                'zoom_level': zoom_level,
                'data_type': 'ward_markers',
                'features': [
                    {
                        'id': row.id,
                        'event_type': row.event_type,
                        'fatalities': row.fatalities,
                        'date_occurred': row.date_occurred.isoformat() if row.date_occurred else None,
                        'description': row.description,
                        'location': {
                            'name': row.location_name,
                            'state': row.state,
                            'lga': row.lga,
                            'ward': row.ward,
                            'coordinates': {'lat': row.latitude, 'lng': row.longitude}
                        }
                    }
                    for row in result
                ]
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hierarchical data query failed: {str(e)}")
