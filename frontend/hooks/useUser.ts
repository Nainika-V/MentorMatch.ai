"use client"

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface User {
  id: string;
  name: string;
  email: string;
  username: string;
  role: 'mentor' | 'mentee';
}

export function useUser() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("--- Running useUser hook to check authentication ---");
    const checkUser = async () => {
      try {
        console.log("Fetching /auth/profile...");
        const data = await api.get('/auth/profile');
        console.log("Response from /auth/profile:", data); // Log the response
        if (data && data.user) {
          console.log("User data found, setting user.");
          setUser(data.user);
        } else {
          console.log("No user data in response, setting user to null.");
          setUser(null);
        }
      } catch (error) {
        console.error("useUser Error:", error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkUser();
  }, []);

  return { user, loading, isAuthenticated: !!user };
}
