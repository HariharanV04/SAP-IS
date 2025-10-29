import React, { useState } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import Navigation from '@components/Navigation';
import Header from '@/components/Header';
function PrivateLayout() {
    const [isExpanded, setIsExpanded] = useState(true);
    const [isCompact, setIsCompact] = useState(true);

    const toggleSidebar = () => {
        setIsExpanded(!isExpanded);
    };
    return (
        <>
            <Header isExpanded={isExpanded} toggleSidebar={toggleSidebar} />
            <Navigation isExpanded={isExpanded} />

            <div className="bg-slate-50 min-h-full p-6 pb-4 pt-24 md:ml-20">                
                <Outlet />
            </div>


        </>
    )
}

export default PrivateLayout