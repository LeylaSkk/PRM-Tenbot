import React from 'react';
import Navbar from '../components/navbar';
import { Outlet } from 'react-router-dom';

function LayoutDashboard() {
    return (
        <div className="h-auto overflow-auto">
            {/* TenStep-styled Navbar */}
            <Navbar />
            {/* Main content area */}
            <main className="flex items-center justify-center h-auto overflow-hidden  ">
                <Outlet />
            </main>
        </div>
    );
}

export default LayoutDashboard;
