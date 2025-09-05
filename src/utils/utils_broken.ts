import { chinaCities } from '@/static/city';
import {
  MAIN_COLOR,
  PUSHUP_TITLES,
  ACTIVITY_TYPES,
  RICH_TITLE,
  getRuntimePushupColor,
} from './const';

export type RunIds = Array<number> | [];

export interface Activity {
  run_id: number;
  name: string;
  distance: number;
  moving_time: string;
  type: string;
  subtype: string;
  start_date: string;
  start_date_local: string;
  location_country?: string | null;
  summary_polyline?: string | null;
  average_heartrate?: number | null;
  elevation_gain: number | null;
  average_speed: number;
  streak: number;
}

export interface ISite {
  siteTitle: string;
  siteUrl: string;
  description: string;
  logo: string;
  navLinks: {
    name: string;
    url: string;
  }[];
}

export interface IViewState {
  latitude: number;
  longitude: number;
  zoom: number;
}

export const convertMovingTime2Sec = (m: string): number => {
  try {
    const arr = m.split(':');
    let s = 0;
    for (let i = arr.length - 1; i >= 0; i--) {
      s += parseInt(arr[i]) * Math.pow(60, arr.length - 1 - i);
    }
    return s;
  } catch (err) {
    console.log(err);
    return 0;
  }
};

export const titleForShow = (run: Activity | string): string => {
  if (typeof run === 'string') {
    return run;
  }

  const runHasCn = run.name && run.name.match(/[\u4e00-\u9fa5]/);
  if (runHasCn && !RICH_TITLE) {
    return run.name;
  }

  const distance = (run.distance / 1000.0).toFixed(0);
  let name = '';
  if (run.name) {
    name = run.name;
  }

  return name;
};

export const formatPace = (seconds: number): string => {
  if (seconds === 0) return '0:00';
  const pace = (seconds / 60).toFixed(2);
  const minutes = Math.floor(Number(pace));
  const secondsLeft = Math.floor((Number(pace) - minutes) * 60);
  return `${minutes}:${secondsLeft.toString().padStart(2, '0')}`;
};

export const subTitleForShow = (run: Activity): string => {
  const speed = run.average_speed;
  if (speed) {
    const pace = formatPace(1000.0 / speed);
    return ` Pace: ${pace}`;
  }
  return '';
};

export const colorFromType = (type: string): string => {
  switch (type) {
    case 'Pushup':
      return getRuntimePushupColor();
    default:
      return MAIN_COLOR;
  }
};

// For running geo
export const getBoundsForGeoData = (
  geoData: GeoJSON.FeatureCollection<GeoJSON.LineString>
): [[number, number], [number, number]] => {
  const { features } = geoData;
  let minLat = 90;
  let maxLat = -90;
  let minLng = 180;
  let maxLng = -180;

  for (const feature of features) {
    const { coordinates } = feature.geometry;
    for (const [lng, lat] of coordinates) {
      minLat = Math.min(minLat, lat);
      maxLat = Math.max(maxLat, lat);
      minLng = Math.min(minLng, lng);
      maxLng = Math.max(maxLng, lng);
    }
  }

  return [
    [minLng, minLat],
    [maxLng, maxLat],
  ];
};

export const scrollToMap = (): void => {
  const el = document.querySelector('.run_map');
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });
  }
};

export const sortDateFunc = (a: Activity, b: Activity): number =>
  new Date(b.start_date_local).getTime() - new Date(a.start_date_local).getTime();

export const sortDateFuncReverse = (a: Activity, b: Activity): number =>
  new Date(a.start_date_local).getTime() - new Date(b.start_date_local).getTime();

// const
export const sortDistanceFunc = (a: Activity, b: Activity): number => b.distance - a.distance;

export const filterYearRuns = (run: Activity, year: string): boolean =>
  run.start_date_local.slice(0, 4) === year;

export const filterAndSortRuns = (
  activities: Activity[],
  filterFunc: (_run: Activity, _value: string) => boolean,
  filterValue: string,
  sortFunc: (_runs: Activity[]) => Activity[],
  geoValue?: string
) => {
  let filteredActivities: Activity[] = activities;
  if (filterFunc) {
    filteredActivities = activities.filter((run) => filterFunc(run, filterValue));
  }
  if (geoValue) {
    filteredActivities = filteredActivities.filter((run) => filterCityRuns(run, geoValue));
  }
  if (sortFunc) {
    filteredActivities = sortFunc(filteredActivities);
  }

  // For pushup activities, calculate totals
  const sumDistance = filteredActivities.reduce((sum, run) => sum + run.distance, 0);
  const sumMovingTime = filteredActivities.reduce(
    (sum, run) => sum + convertMovingTime2Sec(run.moving_time || '0'),
    0
  );
  const avgHeartRate = filteredActivities.length
    ? filteredActivities.reduce((sum, run) => sum + (run.average_heartrate || 0), 0) /
      filteredActivities.length
    : 0;

  // Calculate streak (simplified for pushups)
  const streak = filteredActivities.length;

  return {
    filterActivities: filteredActivities,
    sumDistance,
    sumMovingTime,
    streak,
    heartRate: avgHeartRate,
  };
};

export const filterCityRuns = (run: Activity, city: string): boolean => {
  if (run.location_country) {
    return run.location_country.includes(city);
  }
  return false;
};

export const filterTitleRuns = (run: Activity, title: string): boolean => {
  if (run.name) {
    return run.name.includes(title);
  }
  return false;
};

export const locationForRun = (run: Activity): string => {
  let location = run.location_country || '';
  if (location) {
    const cityMatch = chinaCities.find((c) => location.includes(c.name));
    if (cityMatch) {
      location = cityMatch.name;
    }
  }
  return location;
};

export const intComma = (x: number): string => x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');

export const kmOrMiles = (k: number): string => `${k.toFixed(0)} pushups`;

export const minutesAndSecondsFormat = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const second = seconds % 60;
  if (minutes === 0) {
    return `${second}s`;
  }
  return `${minutes}:${second.toFixed(0).toString().padStart(2, '0')}`;
};

// Add overloaded signatures for the function
export function filterAndSortRuns(
  activities: Activity[],
  filterFunc: (_run: Activity, _value: string) => boolean,
  filterValue: string,
  sortFunc?: (_runs: Activity[]) => Activity[],
  geoValue?: string
): {
  filterActivities: Activity[];
  sumDistance: number;
  sumMovingTime: number;
  streak: number;
  heartRate: number;
};

export function filterAndSortRuns(
  activities: Activity[],
  filterFunc: (_run: Activity, _value: string) => boolean,
  filterValue: string,
  title?: string
): {
  filterActivities: Activity[];
  sumDistance: number;
  sumMovingTime: number;
  streak: number;
  heartRate: number;
};

// Implementation
export function filterAndSortRuns(
  activities: Activity[],
  filterFunc: (_run: Activity, _value: string) => boolean,
  filterValue: string,
  titleOrSortFunc?: string | ((_runs: Activity[]) => Activity[]),
  geoValue?: string
): {
  filterActivities: Activity[];
  sumDistance: number;
  sumMovingTime: number;
  streak: number;
  heartRate: number;
} {
  let filteredActivities: Activity[] = activities;
  
  if (filterFunc) {
    filteredActivities = activities.filter((run) => filterFunc(run, filterValue));
  }
  
  // Handle title filtering if titleOrSortFunc is a string
  if (typeof titleOrSortFunc === 'string') {
    filteredActivities = filteredActivities.filter((run) => filterTitleRuns(run, titleOrSortFunc));
  }
  
  if (geoValue) {
    filteredActivities = filteredActivities.filter((run) => filterCityRuns(run, geoValue));
  }
  
  // Handle sorting if titleOrSortFunc is a function
  if (typeof titleOrSortFunc === 'function') {
    filteredActivities = titleOrSortFunc(filteredActivities);
  } else {
    // Default sort by date
    filteredActivities = filteredActivities.sort(sortDateFunc);
  }

  // Calculate aggregated values
  const sumDistance = filteredActivities.reduce((sum, run) => sum + run.distance, 0);
  const sumMovingTime = filteredActivities.reduce(
    (sum, run) => sum + convertMovingTime2Sec(run.moving_time || '0'),
    0
  );
  const avgHeartRate = filteredActivities.length
    ? filteredActivities.reduce((sum, run) => sum + (run.average_heartrate || 0), 0) /
      filteredActivities.length
    : 0;

  // Simple streak calculation for pushups
  const streak = filteredActivities.length;

  return {
    filterActivities: filteredActivities,
    sumDistance,
    sumMovingTime,
    streak,
    heartRate: avgHeartRate,
  };
}

// Simplified placeholder for geo features (not needed for pushups)
export const geoJsonForRuns = (runs: Activity[]): any => ({
  type: 'FeatureCollection',
  features: [],
});