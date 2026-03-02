import React from 'react';

const IssueDetailsTable = ({ ipo }) => {
    if (!ipo) return null;

    const details = [
        { label: "Listing Date", value: ipo.listing_date },
        { label: "Face Value", value: `₹${ipo.face_value || ipo.security_info?.faceValue || '-'}` },
        { label: "Price / Range", value: ipo.issue_price !== "-" ? `₹${ipo.issue_price}` : `₹${ipo.price_range}` },
        { label: "Lot Size", value: ipo.lot_size ? `${ipo.lot_size} Shares` : '-' },
        { label: "Total Issue Size", value: ipo.issue_size ? `₹${ipo.issue_size} Cr` : '-' },
        { label: "Fresh Issue", value: ipo.fresh_issue ? `₹${ipo.fresh_issue} Cr` : '-' },
        { label: "Offer for Sale", value: ipo.offer_for_sale ? `₹${ipo.offer_for_sale} Cr` : '-' },
        { label: "Issue Type", value: ipo.security_type === "SME" ? "SME IPO" : "Book Built Issue IPO" },
        { label: "Listing At", value: ipo.security_type === "SME" ? "NSE SME / BSE SME" : "BSE, NSE" },
    ];

    return (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden mb-8">
            <div className="text-sm font-semibold bg-[#1a2332] text-white py-3 px-6">
                {ipo.company_name} - IPO Details
            </div>
            <div className="p-0">
                <table className="min-w-full divide-y divide-gray-200">
                    <tbody className="bg-white divide-y divide-gray-100">
                        {details.map((item, index) => (
                            <tr key={index} className="hover:bg-gray-50 transition-colors">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-500 w-1/3 bg-gray-50/50">
                                    {item.label}
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                                    {item.value || "-"}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default IssueDetailsTable;
