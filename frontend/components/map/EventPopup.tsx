import React from 'react';
import { Popup } from 'react-map-gl';
import { format } from 'date-fns';
import { X, Calendar, MapPin, Users, Skull, AlertTriangle } from 'lucide-react';
import type { ConflictEvent } from '../../lib/map/clustering';
import { getEventColor } from '../../lib/map/colors';

interface EventPopupProps {
  event: ConflictEvent;
  onClose: () => void;
}

/**
 * Popup component displaying detailed information about a conflict event
 */
export const EventPopup: React.FC<EventPopupProps> = ({ event, onClose }) => {
  const eventColor = getEventColor(event.event_type);

  return (
    <Popup
      longitude={event.longitude}
      latitude={event.latitude}
      anchor="bottom"
      onClose={onClose}
      closeButton={false}
      maxWidth="350px"
      className="conflict-event-popup"
    >
      <div className="bg-white rounded-lg shadow-xl overflow-hidden">
        {/* Header with event type */}
        <div
          className="px-4 py-3 text-white font-semibold flex justify-between items-center"
          style={{ backgroundColor: eventColor }}
        >
          <span className="text-sm uppercase tracking-wide">
            {event.event_type}
          </span>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 transition-colors"
            aria-label="Close popup"
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-3">
          {/* Location */}
          <div className="flex items-start space-x-2">
            <MapPin size={16} className="text-gray-500 mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <p className="font-semibold text-gray-900">
                {event.community || event.lga || event.state}
              </p>
              <p className="text-gray-600">
                {event.lga && event.lga !== event.community && (
                  <>{event.lga}, </>
                )}
                {event.state}
              </p>
            </div>
          </div>

          {/* Date */}
          <div className="flex items-center space-x-2">
            <Calendar size={16} className="text-gray-500 flex-shrink-0" />
            <p className="text-sm text-gray-700">
              {event.event_date
                ? format(new Date(event.event_date), 'PPP')
                : 'Date unknown'}
            </p>
          </div>

          {/* Casualties */}
          {(event.fatalities > 0 ||
            (event.injured && event.injured > 0) ||
            (event.kidnapped && event.kidnapped > 0) ||
            (event.displaced && event.displaced > 0)) && (
            <div className="border-t pt-3 space-y-2">
              <div className="flex items-center space-x-2 mb-2">
                <AlertTriangle size={16} className="text-red-600 flex-shrink-0" />
                <p className="text-sm font-semibold text-gray-900">Impact</p>
              </div>

              <div className="grid grid-cols-2 gap-2 text-sm">
                {event.fatalities > 0 && (
                  <div className="flex items-center space-x-2">
                    <Skull size={14} className="text-red-600 flex-shrink-0" />
                    <span className="text-gray-700">
                      <span className="font-semibold">{event.fatalities}</span> fatalities
                    </span>
                  </div>
                )}

                {event.injured && event.injured > 0 && (
                  <div className="flex items-center space-x-2">
                    <span className="text-orange-600">🏥</span>
                    <span className="text-gray-700">
                      <span className="font-semibold">{event.injured}</span> injured
                    </span>
                  </div>
                )}

                {event.kidnapped && event.kidnapped > 0 && (
                  <div className="flex items-center space-x-2">
                    <span className="text-purple-600">⛓️</span>
                    <span className="text-gray-700">
                      <span className="font-semibold">{event.kidnapped}</span> kidnapped
                    </span>
                  </div>
                )}

                {event.displaced && event.displaced > 0 && (
                  <div className="flex items-center space-x-2">
                    <span className="text-blue-600">🏠</span>
                    <span className="text-gray-700">
                      <span className="font-semibold">{event.displaced}</span> displaced
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Actors */}
          {event.actors && event.actors.length > 0 && (
            <div className="border-t pt-3">
              <div className="flex items-start space-x-2">
                <Users size={16} className="text-gray-500 mt-0.5 flex-shrink-0" />
                <div className="text-sm">
                  <p className="font-semibold text-gray-900 mb-1">Actors:</p>
                  <ul className="space-y-1">
                    {event.actors.map((actor, index) => (
                      <li key={index} className="text-gray-700 flex items-start">
                        <span className="mr-2">•</span>
                        <span>{actor}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Description */}
          {event.description && (
            <div className="border-t pt-3">
              <p className="text-sm text-gray-700 line-clamp-3">
                {event.description}
              </p>
            </div>
          )}

          {/* View Details Link */}
          <div className="border-t pt-3">
            <button
              className="text-sm font-medium hover:underline"
              style={{ color: eventColor }}
              onClick={() => {
                // Navigate to details page (implement as needed)
                console.log('View details for event:', event.id);
              }}
            >
              View Full Details →
            </button>
          </div>
        </div>
      </div>
    </Popup>
  );
};
