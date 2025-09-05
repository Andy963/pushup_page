// Constants for Pushup Page
export const IS_CHINESE =
  typeof window !== 'undefined'
    ? !!(
        window.navigator.language && window.navigator.language.includes('zh')
      )
    : false;

const USE_GOOGLE_ANALYTICS = false;
const GOOGLE_ANALYTICS_TRACKING_ID = '';

// Information messages
const CHINESE_INFO_MESSAGE = (yearLength: number, year: string): string => {
  const yearStr = year === 'Total' ? '所有' : ` ${year} `;
  return `记录自己俯卧撑 ${yearLength} 年了，下面列表展示的是${yearStr}的数据`;
};
const ENGLISH_INFO_MESSAGE = (yearLength: number, year: string): string =>
  `Pushup Journey with ${yearLength} Years, the table shows year ${year} data`;

const INFO_MESSAGE = IS_CHINESE ? CHINESE_INFO_MESSAGE : ENGLISH_INFO_MESSAGE;

// Pushup related titles
const PUSHUP_TITLE = IS_CHINESE ? '俯卧撑' : 'Pushups';
const MORNING_PUSHUP_TITLE = IS_CHINESE ? '晨练俯卧撑' : 'Morning Pushups';
const MIDDAY_PUSHUP_TITLE = IS_CHINESE ? '午间俯卧撑' : 'Midday Pushups';
const AFTERNOON_PUSHUP_TITLE = IS_CHINESE ? '午后俯卧撑' : 'Afternoon Pushups';
const EVENING_PUSHUP_TITLE = IS_CHINESE ? '傍晚俯卧撑' : 'Evening Pushups';
const NIGHT_PUSHUP_TITLE = IS_CHINESE ? '夜晚俯卧撑' : 'Night Pushups';

// General titles
const ALL_TITLE = IS_CHINESE ? '所有' : 'All';
const ACTIVITY_COUNT_TITLE = IS_CHINESE ? '活动次数' : 'Activity Count';
const MAX_PUSHUP_TITLE = IS_CHINESE ? '最多俯卧撑' : 'Max Pushups';
const TOTAL_TIME_TITLE = IS_CHINESE ? '总时间' : 'Total Time';
const AVERAGE_PUSHUP_TITLE = IS_CHINESE ? '平均俯卧撑' : 'Average Pushups';
const TOTAL_PUSHUP_TITLE = IS_CHINESE ? '总俯卧撑' : 'Total Pushups';
const AVERAGE_HEART_RATE_TITLE = IS_CHINESE ? '平均心率' : 'Average Heart Rate';
const YEARLY_TITLE = IS_CHINESE ? 'Year' : 'Yearly';
const MONTHLY_TITLE = IS_CHINESE ? 'Month' : 'Monthly';
const WEEKLY_TITLE = IS_CHINESE ? 'Week' : 'Weekly';
const DAILY_TITLE = IS_CHINESE ? 'Day' : 'Daily';
const HOME_PAGE_TITLE = IS_CHINESE ? '首页' : 'Home';

// Set to false since pushups don't have elevation
const SHOW_ELEVATION_GAIN = false;
// Set to false for simplicity
const RICH_TITLE = false;
const USE_ANIMATION_FOR_GRID = false;

const ACTIVITY_TYPES = {
  PUSHUP_TITLE,
  ALL_TITLE,
};

const PUSHUP_TITLES = {
  MORNING_PUSHUP_TITLE,
  MIDDAY_PUSHUP_TITLE,
  AFTERNOON_PUSHUP_TITLE,
  EVENING_PUSHUP_TITLE,
  NIGHT_PUSHUP_TITLE,
};

const ACTIVITY_TOTAL = {
  ACTIVITY_COUNT_TITLE,
  MAX_PUSHUP_TITLE,
  TOTAL_TIME_TITLE,
  AVERAGE_PUSHUP_TITLE,
  TOTAL_PUSHUP_TITLE,
  AVERAGE_HEART_RATE_TITLE,
  YEARLY_TITLE,
  MONTHLY_TITLE,
  WEEKLY_TITLE,
  DAILY_TITLE,
};

// Color constants
const nike = 'rgb(224,237,94)';
const dark_vanilla = 'rgb(228,212,220)';

export const MAIN_COLOR = nike;
export const PUSHUP_COLOR_LIGHT = '#47b8e0';
export const PUSHUP_COLOR_DARK = MAIN_COLOR;

// Helper function to get theme-aware PUSHUP_COLOR
export const getRuntimePushupColor = (): string => {
  if (typeof window === 'undefined') return PUSHUP_COLOR_DARK;

  const dataTheme = document.documentElement.getAttribute('data-theme');
  const savedTheme = localStorage.getItem('theme');

  // Determine current theme (default to dark)
  const isDark =
    dataTheme === 'dark' ||
    (!dataTheme && savedTheme === 'dark') ||
    (!dataTheme && !savedTheme);

  return isDark ? PUSHUP_COLOR_DARK : PUSHUP_COLOR_LIGHT;
};

// Exports
export {
  USE_GOOGLE_ANALYTICS,
  GOOGLE_ANALYTICS_TRACKING_ID,
  INFO_MESSAGE,
  PUSHUP_TITLES,
  USE_ANIMATION_FOR_GRID,
  SHOW_ELEVATION_GAIN,
  RICH_TITLE,
  ACTIVITY_TYPES,
  ACTIVITY_TOTAL,
  HOME_PAGE_TITLE,
  PUSHUP_TITLE,
  ALL_TITLE,
  ACTIVITY_COUNT_TITLE,
  MAX_PUSHUP_TITLE,
  TOTAL_TIME_TITLE,
  AVERAGE_PUSHUP_TITLE,
  TOTAL_PUSHUP_TITLE,
  AVERAGE_HEART_RATE_TITLE,
};

// Rename RUN_TITLES to PUSHUP_TITLES for compatibility
export const RUN_TITLES = PUSHUP_TITLES;