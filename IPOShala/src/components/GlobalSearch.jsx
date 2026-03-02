import React, { useState, useEffect, useRef } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { searchIPOs } from '../services/ipos';

const GlobalSearch = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showDropdown, setShowDropdown] = useState(false);
    const searchRef = useRef(null);
    const navigate = useNavigate();

    // Debounce logic
    useEffect(() => {
        const timer = setTimeout(() => {
            if (query.trim().length >= 2) {
                setLoading(true);
                searchIPOs(query)
                    .then(data => {
                        setResults(data);
                        setShowDropdown(true);
                    })
                    .catch(err => console.error("Search error", err))
                    .finally(() => setLoading(false));
            } else {
                setResults([]);
                setShowDropdown(false);
            }
        }, 300); // 300ms debounce

        return () => clearTimeout(timer);
    }, [query]);

    // Click outside to close dropdown
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (searchRef.current && !searchRef.current.contains(event.target)) {
                setShowDropdown(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            setShowDropdown(false);
            navigate(`/search?q=${encodeURIComponent(query)}`);
        }
    };

    return (
        <div className="relative w-full max-w-sm" ref={searchRef}>
            <form onSubmit={handleSearchSubmit} className="relative">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search IPOs..."
                    className="w-full pl-10 pr-4 py-2 bg-[#2a3442] text-white border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400"
                />
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    {loading ? (
                        <Loader2 className="h-5 w-5 text-gray-400 animate-spin" />
                    ) : (
                        <Search className="h-5 w-5 text-gray-400" />
                    )}
                </div>
            </form>

            {/* Dropdown Results */}
            {showDropdown && results.length > 0 && (
                <div className="absolute z-50 mt-1 w-full bg-white rounded-md shadow-lg border border-gray-200 overflow-hidden">
                    <ul className="max-h-60 overflow-y-auto py-1">
                        {results.map((result, idx) => (
                            <li key={`${result.id}-${idx}`}>
                                <Link
                                    to={`/ipo/${result.id}`}
                                    onClick={() => {
                                        setShowDropdown(false);
                                        setQuery('');
                                    }}
                                    className="block px-4 py-2 hover:bg-gray-100 transition-colors"
                                >
                                    <div className="flex justify-between items-center">
                                        <span className="font-medium text-sm text-gray-900 line-clamp-1">{result.name}</span>
                                        <span className={`text-xs px-2 py-0.5 rounded-full ${result.type === 'SME' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}`}>
                                            {result.type}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center mt-1">
                                        <span className="text-xs text-gray-500">{result.symbol}</span>
                                        <span className="text-xs text-gray-500">{result.status}</span>
                                    </div>
                                </Link>
                            </li>
                        ))}
                    </ul>
                    <div className="border-t border-gray-100">
                        <button
                            onClick={handleSearchSubmit}
                            className="block w-full text-center px-4 py-2 text-sm text-blue-600 hover:bg-gray-50 font-medium"
                        >
                            View all results
                        </button>
                    </div>
                </div>
            )}
            {showDropdown && query.length >= 2 && results.length === 0 && !loading && (
                <div className="absolute z-50 mt-1 w-full bg-white rounded-md shadow-lg border border-gray-200 p-4 text-center text-sm text-gray-500">
                    No IPOs found for "{query}"
                </div>
            )}
        </div>
    );
};

export default GlobalSearch;
