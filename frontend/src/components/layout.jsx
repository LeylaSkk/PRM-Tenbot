import React from 'react';
import Navbar from '../components/navbar';
import { Outlet } from 'react-router-dom';

function LayoutDashboard() {
    return (
        <div className="min-h-screen overflow-hidden">
            {/* TenStep-styled Navbar */}
            <Navbar />
            {/* Main content area */}
            <main className="flex items-center justify-center bg-gray-100 min-h-screen p-4 md:p-6 2xl:p-10 ">
                <Outlet />
            </main>
        </div>
    );
}

export default LayoutDashboard;
