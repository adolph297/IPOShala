import React from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

const RiskMeter = ({ score, level }) => {
    // Return early if score is not defined
    if (score === undefined || score === null) return null;

    let colorClass = "text-emerald-500";
    let bgClass = "bg-emerald-500";
    let lightBgClass = "bg-emerald-50";
    let Icon = ShieldCheck;

    if (score < 45) {
        colorClass = "text-red-500";
        bgClass = "bg-red-500";
        lightBgClass = "bg-red-50";
        Icon = AlertTriangle;
    } else if (score < 75) {
        colorClass = "text-amber-500";
        bgClass = "bg-amber-500";
        lightBgClass = "bg-amber-50";
        Icon = ShieldAlert;
    }

    return (
        <div className="mb-8 border rounded-xl p-6 shadow-sm border-gray-200 bg-white">
            <h3 className="text-sm font-semibold bg-[#1a2332] text-white py-3 px-6 rounded-t-xl -mx-6 -mt-6 mb-6 uppercase tracking-widest flex flex-row items-center gap-2">
                <Icon className="w-4 h-4 text-white" />
                AI Confidence Score
            </h3>
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">

                <div className="flex-1 w-full">
                    <div className="flex justify-between items-end mb-2">
                        <span className="text-lg font-bold text-gray-800">{level}</span>
                        <span className={`text-2xl font-black ${colorClass}`}>{score}/100</span>
                    </div>

                    <div className="w-full h-4 bg-gray-100 rounded-full overflow-hidden">
                        <div
                            className={`h-full ${bgClass} transition-all duration-1000 ease-out rounded-full`}
                            style={{ width: `${score}%` }}
                        />
                    </div>

                    <div className="flex justify-between mt-2 text-xs text-gray-400 font-medium uppercase">
                        <span>High Risk</span>
                        <span>Moderate</span>
                        <span>Low Risk</span>
                    </div>
                </div>

                <div className={`w-full md:w-1/3 p-4 rounded-lg flex items-start gap-3 ${lightBgClass} border border-opacity-50`}>
                    <p className="text-sm text-gray-700 leading-relaxed">
                        <strong>AI Analysis:</strong> This internal confidence score is dynamically calculated by weighting live GMP figures against the upper bound issue price, analyzing QIB & HNI subscription momentum, and evaluating the aggregate issue size to predict relative listing stability.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default RiskMeter;
