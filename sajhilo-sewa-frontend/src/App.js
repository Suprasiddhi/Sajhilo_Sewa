import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import UserLoginPage from "./pages/UserLoginPage";
import UserRegisterPage from "./pages/UserRegisterPage";
import HomePage from "./pages/HomePage";
import PracticePage from "./pages/PracticePage";
import GestureDetailPage from "./pages/GestureDetailPage";
import AdminLoginPage from "./pages/AdminLoginPage";
import AdminDashboard from "./pages/AdminDashboard";
import SingleWordDetection from "./pages/SingleWordDetection";
import UpdateProfilePage from "./pages/UpdateProfilePage";
import MainLayout from "./components/layout/MainLayout";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* Admin Routes - No Global Layout */}
        <Route path="/admin" element={<AdminLoginPage />} />
        <Route 
          path="/admin/dashboard" 
          element={
            <ProtectedRoute adminOnly={true}>
              <AdminDashboard />
            </ProtectedRoute>
          } 
        />
        <Route path="/login" element={<UserLoginPage />} />
        <Route path="/register" element={<UserRegisterPage />} />
        <Route path="/updateprofile" element={<UpdateProfilePage />} />

        {/* Unified Layout with Granular Protection */}
        <Route
          path="*"
          element={
            <MainLayout>
              <Routes>
                <Route path="/" element={<HomePage />} />
                
                {/* Protected User Features */}
                <Route 
                  path="/single-word-detection" 
                  element={
                    <ProtectedRoute>
                      <SingleWordDetection />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/practice" 
                  element={
                    <ProtectedRoute>
                      <PracticePage />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/work/:id/:title" 
                  element={
                    <ProtectedRoute>
                      <GestureDetailPage />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/settings" 
                  element={
                    <ProtectedRoute>
                      <div style={{ padding: '40px', textAlign: 'center' }}><h2>Settings Coming Soon</h2></div>
                    </ProtectedRoute>
                  } 
                />

                {/* 404 handler */}
                <Route path="*" element={<div style={{ padding: '40px', textAlign: 'center' }}><h2>Page Not Found</h2></div>} />
              </Routes>
            </MainLayout>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
