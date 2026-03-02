import React, { useEffect, useState } from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import { Activity, TrendingUp, Target, BarChart3, PieChart } from 'lucide-react';

const Analytics = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('http://localhost:8000/api/analytics/overview')
            .then(res => res.json())
            .then(result => {
                if (result.metrics) {
                    setData(result);
                }
                setLoading(false);
            })
            .catch(console.error);
    }, []);

    if (loading) {
        return <div className="min-h-screen py-20 text-center"><div className="w-8 h-8 border-4 border-blue-600 border-t-transparent flex items-center justify-center animate-spin rounded-full mx-auto mb-4"></div>Loading analytics...</div>;
    }

    if (!data) {
        return <div className="min-h-screen py-20 text-center text-gray-500">Analytics data unavailable.</div>;
    }

    const { metrics, yearly } = data;

    return (
        <>
            <Helmet>
                <title>IPO Analytics Dashboard | Institutional IPO Metrics - IPOshala</title>
                <meta name="description" content="View historical IPO trends, average listing gains, SME vs Mainboard performance, and track overall IPO win rates in our institutional analytics dashboard." />
                <meta property="og:title" content="IPO Analytics Dashboard - IPOshala" />
                <meta property="og:description" content="A comprehensive visualized breakdown of past IPO performances, win rates, and capital raised across Mainboard and SME exchanges." />
            </Helmet>

            <PageHeader
                title="Institutional Analytics Dashboard"
                subtitle="Uncover historical trends, average listing gains, and track win rates over time."
            />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                {/* Top Metric Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                    {/* Card 1 */}
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Total Listed</h3>
                            <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                                <BarChart3 size={20} />
                            </div>
                        </div>
                        <p className="text-3xl font-bold text-gray-900">{metrics.total_listed}</p>
                        <p className="text-sm font-medium text-gray-500 mt-2">
                            <span className="text-blue-600">{metrics.mainboard_count}</span> Mainboard / <span className="text-emerald-600">{metrics.sme_count}</span> SME
                        </p>
                    </div>

                    {/* Card 2 */}
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Avg Listing Gain</h3>
                            <div className="p-2 bg-emerald-50 rounded-lg text-emerald-600">
                                <TrendingUp size={20} />
                            </div>
                        </div>
                        <p className="text-3xl font-bold text-gray-900">{metrics.avg_listing_gain}%</p>
                        <p className="text-sm font-medium text-gray-500 mt-2">Historical Average</p>
                    </div>

                    {/* Card 3 */}
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Overall Win Rate</h3>
                            <div className="p-2 bg-purple-50 rounded-lg text-purple-600">
                                <Target size={20} />
                            </div>
                        </div>
                        <p className="text-3xl font-bold text-gray-900">{metrics.win_rate}%</p>
                        <p className="text-sm font-medium text-gray-500 mt-2">Positive returns on listing</p>
                    </div>

                    {/* Card 4 */}
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Market Activity</h3>
                            <div className="p-2 bg-orange-50 rounded-lg text-orange-600">
                                <Activity size={20} />
                            </div>
                        </div>
                        <p className="text-3xl font-bold text-gray-900">High</p>
                        <p className="text-sm font-medium text-gray-500 mt-2">Based on current pipeline</p>
                    </div>
                </div>

                {/* Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Chart 1: Average Gain per Year */}
                    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                        <h3 className="text-lg font-bold text-[#1a2332] mb-6 flex items-center">
                            <PieChart className="mr-2 text-blue-500" size={20} />
                            Average Listing Gains by Year (%)
                        </h3>
                        <div className="h-80 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={yearly} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                                    <XAxis dataKey="year" tick={{ fill: '#6B7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                                    <YAxis tick={{ fill: '#6B7280', fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(val) => `${val}%`} />
                                    <RechartsTooltip
                                        contentStyle={{ backgroundColor: '#1a2332', color: '#fff', borderRadius: '8px', border: 'none' }}
                                        itemStyle={{ color: '#fff' }}
                                        formatter={(val) => [`${val}%`, 'Avg Gain']}
                                    />
                                    <Line type="monotone" dataKey="avg_gain" stroke="#2563EB" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 8 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Chart 2: Volume & Win Rate */}
                    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                        <h3 className="text-lg font-bold text-[#1a2332] mb-6 flex items-center">
                            <BarChart3 className="mr-2 text-emerald-500" size={20} />
                            IPO Volume & Win Rate
                        </h3>
                        <div className="h-80 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={yearly} margin={{ top: 5, right: 0, left: -20, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                                    <XAxis dataKey="year" tick={{ fill: '#6B7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                                    <YAxis yAxisId="left" tick={{ fill: '#6B7280', fontSize: 12 }} axisLine={false} tickLine={false} />
                                    <YAxis yAxisId="right" orientation="right" tick={{ fill: '#6B7280', fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(val) => `${val}%`} />
                                    <RechartsTooltip
                                        contentStyle={{ backgroundColor: '#1a2332', color: '#fff', borderRadius: '8px', border: 'none' }}
                                        itemStyle={{ color: '#fff' }}
                                    />
                                    <Legend />
                                    <Bar yAxisId="left" dataKey="ipos" name="Total IPOs" fill="#6366f1" radius={[4, 4, 0, 0]} barSize={30} />
                                    <Bar yAxisId="right" dataKey="win_rate" name="Win Rate %" fill="#10B981" radius={[4, 4, 0, 0]} barSize={30} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

            </div>
        </>
    );
};
export default Analytics;
