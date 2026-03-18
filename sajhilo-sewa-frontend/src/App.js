import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import PracticePage from "./pages/PracticePage";
import AdminLoginPage from "./pages/AdminLoginPage";
import AdminDashboard from "./pages/AdminDashboard";
import SingleWordDetection from "./pages/SingleWordDetection";
import MainLayout from "./components/layout/MainLayout";
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* Admin Routes - No Global Layout */}
        <Route path="/admin" element={<AdminLoginPage />} />
        <Route path="/admin/dashboard" element={<AdminDashboard />} />

        {/* User Routes - With Layout */}
        <Route
          path="*"
          element={
            <MainLayout>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/single-word-detection" element={<SingleWordDetection />} />
                <Route path="/practice" element={<PracticePage />} />
                <Route path="/history" element={<div style={{ padding: '40px', textAlign: 'center' }}><h2>History Coming Soon</h2></div>} />
                <Route path="/settings" element={<div style={{ padding: '40px', textAlign: 'center' }}><h2>Settings Coming Soon</h2></div>} />
              </Routes>
            </MainLayout>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
