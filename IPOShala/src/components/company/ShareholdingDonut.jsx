import React from 'react';

const ShareholdingDonut = ({ data = {} }) => {
    // Robust fallback: if data is empty or all-zero, use a default set for demonstration
    const hasData = data && (Number(data.promoter || 0) > 0 || Number(data.public || 0) > 0);

    const displayData = hasData ? data : {
        promoter: 74.50,
        public: 24.10,
        employee_trusts: 1.40
    };

    const entries = [
        { label: 'Promoter & Promoter Group', value: Number(displayData.promoter || 0), color: '#3b82f6' }, // Blue
        { label: 'Public', value: Number(displayData.public || 0), color: '#10b981' }, // Green
        { label: 'Employee Trusts', value: Number(displayData.employee_trusts || 0), color: '#f59e0b' }, // Amber
    ].filter(e => e.value > 0);

    const total = entries.reduce((acc, curr) => acc + curr.value, 0);

    if (total === 0) {
        return <div className="text-center py-4 text-gray-400 italic text-sm">No data to display in chart</div>;
    }

    // Calculate SVG paths
    let currentPercentage = 0;
    const size = 200;
    const center = size / 2;
    const radius = 80;
    const strokeWidth = 30;

    const getCoordinatesForPercentage = (percentage) => {
        const x = Math.cos(2 * Math.PI * percentage);
        const y = Math.sin(2 * Math.PI * percentage);
        return [x, y];
    };

    const slices = entries.map((entry, i) => {
        const slicePercentage = entry.value / total;
        const startPercentage = currentPercentage;
        const endPercentage = currentPercentage + slicePercentage;

        currentPercentage += slicePercentage;

        const [startX, startY] = getCoordinatesForPercentage(startPercentage - 0.25);
        const [endX, endY] = getCoordinatesForPercentage(endPercentage - 0.25);

        const largeArcFlag = slicePercentage > 0.5 ? 1 : 0;

        const pathData = [
            `M ${center + startX * radius} ${center + startY * radius}`,
            `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${center + endX * radius} ${center + endY * radius}`
        ].join(' ');

        return (
            <path
                key={i}
                d={pathData}
                fill="none"
                stroke={entry.color}
                strokeWidth={strokeWidth}
            />
        );
    });

    return (
        <div className="flex flex-col md:flex-row items-center gap-8 py-6">
            <div className="relative" style={{ width: size, height: size }}>
                <svg viewBox={`0 0 ${size} ${size}`} className="transform -rotate-90">
                    {slices}
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">TOTAL</span>
                    <span className="text-xl font-black text-gray-900 leading-tight">{total.toFixed(1)}%</span>
                    {!hasData && (
                        <div className="bg-amber-500 text-white text-[8px] font-bold px-1 rounded-full mt-1">MOCK</div>
                    )}
                </div>
            </div>

            <div className="flex-1 space-y-3">
                {entries.map((entry, i) => (
                    <div key={i} className="flex items-center justify-between group">
                        <div className="flex items-center gap-3">
                            <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: entry.color }} />
                            <span className="text-sm text-gray-600 font-medium">{entry.label}</span>
                        </div>
                        <span className="text-sm font-bold text-gray-900">{entry.value.toFixed(2)}%</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ShareholdingDonut;
