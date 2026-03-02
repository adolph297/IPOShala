import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import PageHeader from '@/components/common/PageHeader';
import { searchIPOs } from '../services/ipos';
import { Loader2 } from 'lucide-react';

const SearchResults = () => {
    const [searchParams] = useSearchParams();
    const query = searchParams.get('q') || '';
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (query) {
            setLoading(true);
            searchIPOs(query)
                .then(data => {
                    setResults(Array.isArray(data) ? data : []);
                })
                .catch(err => console.error("Error fetching search results:", err))
                .finally(() => setLoading(false));
        } else {
            setResults([]);
            setLoading(false);
        }
    }, [query]);

    return (
        <>
            <Helmet>
                <title>Search Results "{query}" - IPOshala</title>
            </Helmet>
            <PageHeader title="Search Results" subtitle={`Found ${results.length} result(s) for "${query}"`} />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                {loading ? (
                    <div className="flex justify-center items-center py-20">
                        <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
                        <span className="ml-3 text-lg text-gray-600">Searching...</span>
                    </div>
                ) : results.length === 0 ? (
                    <div className="text-center py-20 bg-gray-50 rounded-lg shadow-sm border border-gray-100">
                        <h3 className="text-xl font-medium text-gray-900">No matching IPOs found.</h3>
                        <p className="mt-2 text-gray-500">We couldn't find anything matching "{query}". Please try a different company name or symbol.</p>
                        <Link to="/" className="mt-6 inline-block bg-blue-600 text-white px-6 py-2 rounded-md font-medium hover:bg-blue-700 transition">
                            Return Home
                        </Link>
                    </div>
                ) : (
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                        <ul className="divide-y divide-gray-200">
                            {results.map((result) => (
                                <li key={result.id} className="hover:bg-gray-50 transition duration-150">
                                    <Link to={`/ipo/${result.id}`} className="block p-6">
                                        <div className="flex items-center justify-between">
                                            <div className="flex flex-col">
                                                <div className="flex items-center space-x-3">
                                                    <span className="text-lg font-medium text-blue-600">{result.name}</span>
                                                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${result.type === 'SME' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}`}>
                                                        {result.type}
                                                    </span>
                                                </div>
                                                <span className="text-sm text-gray-500 mt-1">Symbol: {result.symbol}</span>
                                            </div>
                                            <div className="flex flex-col items-end">
                                                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${result.status === 'LIVE' ? 'bg-green-100 text-green-800' :
                                                    result.status === 'UPCOMING' ? 'bg-blue-100 text-blue-800' :
                                                        'bg-gray-100 text-gray-800'
                                                    }`}>
                                                    {result.status}
                                                </span>
                                                <span className="text-sm text-gray-400 mt-1">Click to view details &rarr;</span>
                                            </div>
                                        </div>
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </>
    );
};

export default SearchResults;
