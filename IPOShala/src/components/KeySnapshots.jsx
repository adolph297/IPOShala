import React from 'react';
import { TrendingUp, Clock, BarChart3, Building2, Activity } from 'lucide-react';

const KeySnapshots = () => {
  const snapshots = [
    {
      title: 'Upcoming IPOs',
      value: '12',
      icon: Clock,
      color: 'text-blue-600'
    },
    {
      title: 'Current IPOs',
      value: '8',
      icon: TrendingUp,
      color: 'text-green-600'
    },
    {
      title: 'Recently Listed IPOs',
      value: '15',
      icon: BarChart3,
      color: 'text-orange-600'
    },
    {
      title: 'SME IPOs',
      value: '24',
      icon: Building2,
      color: 'text-purple-600'
    },
    {
      title: 'Active GMP Updates',
      value: '32',
      icon: Activity,
      color: 'text-teal-600'
    }
  ];

  return (
    <section className="py-12 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-[#1a2332] mb-8">IPO Market Snapshot</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {snapshots.map((snapshot) => {
            const Icon = snapshot.icon;
            return (
              <div
                key={snapshot.title}
                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow duration-200"
              >
                <div className="flex items-center justify-between mb-3">
                  <Icon className={`${snapshot.color} h-8 w-8`} />
                </div>
                <div className="text-3xl font-bold text-[#2a3442] mb-1">
                  {snapshot.value}
                </div>
                <div className="text-sm font-medium text-gray-600">
                  {snapshot.title}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default KeySnapshots;