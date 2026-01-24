import React, { useState } from 'react';
import { Search, Loader, X } from 'lucide-react';
import { useGeocoding } from '../../hooks/useGeocoding';

interface MapControlsProps {
  onLocationSelect: (lng: number, lat: number, zoom?: number) => void;
  mapboxAccessToken: string;
  className?: string;
}

/**
 * Map controls including search and zoom
 */
export const MapControls: React.FC<MapControlsProps> = ({
  onLocationSelect,
  mapboxAccessToken,
  className = '',
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [showResults, setShowResults] = useState(false);
  const { search, isSearching } = useGeocoding(mapboxAccessToken);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);

    if (query.length < 3) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }

    const results = await search(query);
    setSearchResults(results);
    setShowResults(results.length > 0);
  };

  const handleSelectLocation = (result: any) => {
    const [lng, lat] = result.center;
    onLocationSelect(lng, lat, 10);
    setSearchQuery(result.place_name);
    setShowResults(false);
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
    setShowResults(false);
  };

  return (
    <div className={`relative ${className}`}>
      {/* Search Input */}
      <div className="relative">
        <div className="flex items-center bg-white rounded-lg shadow-lg">
          <Search className="absolute left-3 text-gray-400" size={18} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search location in Nigeria..."
            className="w-full pl-10 pr-10 py-2.5 rounded-lg border-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
          {isSearching && (
            <Loader className="absolute right-3 text-blue-500 animate-spin" size={18} />
          )}
          {searchQuery && !isSearching && (
            <button
              onClick={clearSearch}
              className="absolute right-3 text-gray-400 hover:text-gray-600"
            >
              <X size={18} />
            </button>
          )}
        </div>

        {/* Search Results Dropdown */}
        {showResults && (
          <div className="absolute top-full mt-2 w-full bg-white rounded-lg shadow-xl z-10 max-h-64 overflow-y-auto">
            {searchResults.map((result, index) => (
              <button
                key={index}
                onClick={() => handleSelectLocation(result)}
                className="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors border-b last:border-b-0"
              >
                <p className="text-sm font-medium text-gray-900">{result.text}</p>
                <p className="text-xs text-gray-600">{result.place_name}</p>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
