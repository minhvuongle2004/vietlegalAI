import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://llinrxwekykjmdrrpxtn.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxsaW5yeHdla3lram1kcnJweHRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg3Nzg0MTgsImV4cCI6MjEwNDM1NDQxOH0.xJXAUANUCuKU_PcwN_rltyO_ylNJpLwS8LkyK1JE0Do';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});
