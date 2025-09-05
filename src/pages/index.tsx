import { useEffect, useState } from 'react';
import { Analytics } from '@vercel/analytics/react';
import { Helmet } from 'react-helmet-async';
import Layout from '@/components/Layout';
import PushupChart from '@/components/PushupChart';
import RunTable from '@/components/RunTable';
import SVGStat from '@/components/SVGStat';
import YearsStat from '@/components/YearsStat';
import useActivities from '@/hooks/useActivities';
import useSiteMetadata from '@/hooks/useSiteMetadata';
import { IS_CHINESE } from '@/utils/const';
import {
  Activity,
  filterAndSortRuns,
  filterYearRuns,
  titleForShow,
} from '@/utils/utils';

const Index = () => {
  const { siteTitle, siteUrl } = useSiteMetadata();
  const { activities, thisYear } = useActivities();
  const [year, setYear] = useState(thisYear);
  const [title, setTitle] = useState('');
  const [currentFilter, setCurrentFilter] = useState<{
    item: string;
    func: (_run: Activity, _value: string) => boolean;
  }>({ item: thisYear, func: filterYearRuns });

  const filterFunc = currentFilter.func;
  const filterValue = currentFilter.item;

  const { 
    filterActivities: filteredActivities,
    sumDistance: totalPushups,
    streak,
    sumMovingTime: totalMovingTime,
    heartRate,
  } = filterAndSortRuns(activities, filterFunc, filterValue, title);

  const locationsData = activities.length > 0 ? [{ country: 'Global', runs: activities.length }] : [];

  useEffect(() => {
    document.title = siteTitle;
  }, [siteTitle]);

  return (
    <>
      <Helmet>
        <title>{siteTitle}</title>
        <meta
          name="description"
          content="Personal pushup tracking page - track your daily pushup progress"
        />
        <meta property="og:image" content={`${siteUrl}/screenshot.png`} />
      </Helmet>
      <div className="App">
        <Layout>
          <SVGStat />
          <YearsStat
            year={year}
            setYear={setYear}
            onClick={(year: string) => {
              setCurrentFilter({
                item: year,
                func: filterYearRuns,
              });
            }}
          />
          
          {/* Pushup Progress Chart */}
          <PushupChart activities={filteredActivities} />
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">
                {IS_CHINESE ? '统计概览' : 'Statistics Overview'}
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>{IS_CHINESE ? '总俯卧撑' : 'Total Pushups'}:</span>
                  <span className="font-semibold">{Math.round(totalPushups)}</span>
                </div>
                <div className="flex justify-between">
                  <span>{IS_CHINESE ? '活动次数' : 'Activities'}:</span>
                  <span className="font-semibold">{filteredActivities.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>{IS_CHINESE ? '连续天数' : 'Streak'}:</span>
                  <span className="font-semibold">{streak}</span>
                </div>
                {totalMovingTime > 0 && (
                  <div className="flex justify-between">
                    <span>{IS_CHINESE ? '总时间' : 'Total Time'}:</span>
                    <span className="font-semibold">
                      {Math.round(totalMovingTime / 3600)}h {Math.round((totalMovingTime % 3600) / 60)}m
                    </span>
                  </div>
                )}
                {heartRate > 0 && (
                  <div className="flex justify-between">
                    <span>{IS_CHINESE ? '平均心率' : 'Average Heart Rate'}:</span>
                    <span className="font-semibold">{Math.round(heartRate)} bpm</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">
                {IS_CHINESE ? '最近记录' : 'Recent Records'}
              </h3>
              {filteredActivities.length > 0 ? (
                <div className="space-y-2">
                  {filteredActivities.slice(0, 5).map((activity) => (
                    <div key={activity.run_id} className="flex justify-between text-sm">
                      <span>{new Date(activity.start_date_local).toLocaleDateString()}</span>
                      <span className="font-semibold">{Math.round(activity.distance)} pushups</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">
                  {IS_CHINESE ? '暂无数据' : 'No data available'}
                </p>
              )}
            </div>
          </div>

          <RunTable
            activities={filteredActivities}
            title={titleForShow(filterValue)}
            locationsData={locationsData}
            setActivity={() => {}} // Simplified since we don't have map interaction
            runIndex={-1}
            setRunIndex={() => {}}
          />
        </Layout>
        <Analytics />
      </div>
    </>
  );
};

export default Index;