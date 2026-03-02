import React from 'react';

const SubscriptionProgress = ({ subscription }) => {
    if (!subscription) return null;

    // Categories config mapping
    const categories = [
        { key: 'qib', label: 'QIB (Institutions)', color: 'bg-indigo-500', bg: 'bg-indigo-50' },
        { key: 'nii', label: 'NII / HNI', color: 'bg-emerald-500', bg: 'bg-emerald-50' },
        { key: 'retail', label: 'Retail Investors', color: 'bg-amber-500', bg: 'bg-amber-50' },
    ];

    // Helper to cap progress bar at 100% visually for high subscriptions
    const calcWidth = (val) => {
        if (!val) return 0;
        if (val < 1) return val * 100;
        // For values >= 1, we fill the bar 100% and show extreme oversubscription via text
        return 100;
    };

    return (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 mb-8">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-semibold text-[#1a2332]">Subscription Status</h2>
                <div className="px-3 py-1 bg-blue-50 text-blue-700 text-sm font-bold rounded-lg border border-blue-100">
                    Total: {subscription.total ? `${subscription.total}x` : 'N/A'}
                </div>
            </div>

            <div className="space-y-6">
                {categories.map((cat) => {
                    const val = subscription[cat.key];
                    if (val === undefined || val === null) return null;

                    const isOverSubscribed = val >= 1;

                    return (
                        <div key={cat.key}>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="font-medium text-gray-700">{cat.label}</span>
                                <span className={`font-bold ${isOverSubscribed ? 'text-green-600' : 'text-gray-600'}`}>
                                    {val}x {isOverSubscribed ? 'Oversubscribed' : 'Subscribed'}
                                </span>
                            </div>
                            <div className={`w-full h-3 rounded-full overflow-hidden flex ${cat.bg}`}>
                                <div
                                    className={`h-full ${cat.color} rounded-full transition-all duration-1000 ease-out`}
                                    style={{ width: `${calcWidth(val)}%` }}
                                ></div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default SubscriptionProgress;
