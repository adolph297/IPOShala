import React, { useEffect, useState } from 'react';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import { Link } from 'react-router-dom';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, Clock } from 'lucide-react';

const Calendar = () => {
    const [currentDate, setCurrentDate] = useState(new Date());
    const [ipos, setIpos] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch both live and upcoming to plot on calendar
        Promise.all([
            fetch('http://localhost:8000/api/ipos/live').then(r => r.json()),
            fetch('http://localhost:8000/api/ipos/upcoming').then(r => r.json())
        ])
            .then(([live, upcoming]) => {
                setIpos([...(Array.isArray(live) ? live : []), ...(Array.isArray(upcoming) ? upcoming : [])]);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    const getDaysInMonth = (date) => {
        return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
    };

    const getFirstDayOfMonth = (date) => {
        return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
    };

    const prevMonth = () => {
        setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
    };

    const nextMonth = () => {
        setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
    };

    const daysInMonth = getDaysInMonth(currentDate);
    const firstDay = getFirstDayOfMonth(currentDate);

    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

    // Helper to parse dates
    const parseDate = (dStr) => {
        if (!dStr || dStr === '-') return null;
        const ts = Date.parse(dStr);
        return isNaN(ts) ? null : new Date(ts);
    };

    const getEventsForDay = (day) => {
        const checkDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
        const checkStr = checkDate.toISOString().split('T')[0];

        return ipos.filter(ipo => {
            const start = parseDate(ipo.issue_start_date);
            const end = parseDate(ipo.issue_end_date);
            const listing = parseDate(ipo.listing_date); // Note: we don't have this explicitly in live, maybe from NSE quote later.

            let isEvent = false;
            const events = [];

            if (start && start.toISOString().split('T')[0] === checkStr) { events.push('Open'); isEvent = true; }
            if (end && end.toISOString().split('T')[0] === checkStr) { events.push('Close'); isEvent = true; }
            if (listing && listing.toISOString().split('T')[0] === checkStr) { events.push('Listing'); isEvent = true; }

            // Also highlight active days
            if (start && end && checkDate >= start && checkDate <= end) {
                isEvent = true;
                if (events.length === 0) events.push('Active');
            }

            if (isEvent) {
                return { ...ipo, events };
            }
            return false;
        }).map(ipo => {
            const start = parseDate(ipo.issue_start_date);
            const end = parseDate(ipo.issue_end_date);
            const events = [];
            if (start && start.toISOString().split('T')[0] === checkStr) events.push('Open');
            if (end && end.toISOString().split('T')[0] === checkStr) events.push('Close');
            if (start && end && checkDate > start && checkDate < end) events.push('Active');
            return { ...ipo, events };
        }).filter(i => i.events.length > 0);
    };

    return (
        <>
            <Helmet>
                <title>IPO Calendar & Listing Dates Tracker - IPOshala</title>
                <meta name="description" content="Track upcoming and live IPO release dates alongside exchange listings in a clean monthly calendar layout to never miss an investment opportunity." />
                <meta property="og:title" content="IPO Calendar - IPOshala" />
                <meta property="og:description" content="Interactive calendar to track opening, closing, and allotment dates for all Mainboard and SME Initial Public Offerings." />
            </Helmet>

            <PageHeader
                title="IPO Calendar"
                subtitle="Track opening, closing, and listing dates for all upcoming public issues."
            />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    {/* Calendar Header */}
                    <div className="px-6 py-5 border-b border-gray-200 flex items-center justify-between bg-gray-50">
                        <h2 className="text-xl font-bold text-[#1a2332] flex items-center">
                            <CalendarIcon className="mr-2 text-blue-600" />
                            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
                        </h2>
                        <div className="flex space-x-2">
                            <button onClick={prevMonth} className="p-2 border border-gray-300 rounded hover:bg-gray-100 transition-colors">
                                <ChevronLeft size={20} className="text-gray-600" />
                            </button>
                            <button onClick={nextMonth} className="p-2 border border-gray-300 rounded hover:bg-gray-100 transition-colors">
                                <ChevronRight size={20} className="text-gray-600" />
                            </button>
                        </div>
                    </div>

                    {/* Calendar Grid */}
                    <div className="p-6">
                        {loading ? (
                            <div className="flex justify-center items-center py-20 text-gray-500">
                                <Clock className="animate-spin mr-2" /> Loading Calendar Events...
                            </div>
                        ) : (
                            <>
                                <div className="grid grid-cols-7 gap-px bg-gray-200 mb-px rounded-t-lg overflow-hidden">
                                    {dayNames.map(day => (
                                        <div key={day} className="bg-gray-50 py-3 text-center text-sm font-semibold text-gray-700">
                                            {day}
                                        </div>
                                    ))}
                                </div>

                                <div className="grid grid-cols-7 gap-px bg-gray-200 border border-t-0 border-gray-200 rounded-b-lg overflow-hidden">
                                    {/* Empty cells for previous month */}
                                    {Array.from({ length: firstDay }).map((_, i) => (
                                        <div key={`empty-${i}`} className="bg-white min-h-[120px] p-2 opacity-50"></div>
                                    ))}

                                    {/* Days of current month */}
                                    {Array.from({ length: daysInMonth }).map((_, i) => {
                                        const day = i + 1;
                                        const isToday = new Date().getDate() === day && new Date().getMonth() === currentDate.getMonth() && new Date().getFullYear() === currentDate.getFullYear();
                                        const events = getEventsForDay(day);

                                        return (
                                            <div key={day} className={`bg-white min-h-[120px] p-2 transition-colors hover:bg-gray-50 ${isToday ? 'ring-2 ring-inset ring-blue-500 bg-blue-50/10' : ''}`}>
                                                <div className={`text-sm font-medium w-8 h-8 flex items-center justify-center rounded-full mb-2 ${isToday ? 'bg-blue-600 text-white' : 'text-gray-700'}`}>
                                                    {day}
                                                </div>

                                                <div className="space-y-1">
                                                    {events.map((event, idx) => (
                                                        <Link
                                                            key={`${event.symbol}-${idx}`}
                                                            to={`/ipo/${event.symbol}`}
                                                            className="block text-xs p-1.5 rounded truncate bg-gray-100 hover:bg-blue-100 text-gray-800 transition-colors border-l-2 border-blue-500"
                                                            title={event.company_name}
                                                        >
                                                            <span className="font-semibold">{event.events[0][0]}</span>: {event.symbol}
                                                        </Link>
                                                    ))}
                                                </div>
                                            </div>
                                        );
                                    })}

                                    {/* Empty cells for next month to fill grid */}
                                    {Array.from({ length: 42 - (daysInMonth + firstDay) }).map((_, i) => (
                                        <div key={`empty-end-${i}`} className="bg-white min-h-[120px] p-2 opacity-50"></div>
                                    ))}
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
};

export default Calendar;
