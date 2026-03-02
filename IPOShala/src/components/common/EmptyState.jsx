import React from 'react';
import { FileQuestion, TrendingUp, CalendarDays, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';

const EmptyState = ({ title, message, type = 'default', actionText, actionLink }) => {
    const getIcon = () => {
        switch (type) {
            case 'ipo': return <TrendingUp className="w-12 h-12 text-[#1a2332]" />;
            case 'calendar': return <CalendarDays className="w-12 h-12 text-[#1a2332]" />;
            case 'gmp': return <Activity className="w-12 h-12 text-[#1a2332]" />;
            default: return <FileQuestion className="w-12 h-12 text-[#1a2332]" />;
        }
    };

    return (
        <div className="flex flex-col items-center justify-center p-12 text-center bg-white border border-dashed border-gray-300 rounded-xl my-8 shadow-sm">
            <div className="bg-gray-50 p-4 rounded-full mb-6">
                {getIcon()}
            </div>

            <h3 className="text-xl font-bold text-gray-900 mb-2">
                {title || "No Data Available"}
            </h3>

            <p className="text-gray-500 max-w-md mx-auto mb-8">
                {message || "We couldn't find any information for this view right now. Check back later or explore other sections."}
            </p>

            {actionText && actionLink && (
                <Link
                    to={actionLink}
                    className="inline-flex items-center justify-center px-6 py-2.5 border border-transparent text-sm font-medium rounded-md text-white bg-[#1a2332] hover:bg-gray-800 transition-colors shadow-sm"
                >
                    {actionText}
                </Link>
            )}
        </div>
    );
};

export default EmptyState;
