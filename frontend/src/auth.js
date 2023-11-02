import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://jazhnnpcpkklxhxdlprw.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImphemhubnBjcGtrbHhoeGRscHJ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTcwOTUwMjcsImV4cCI6MjAxMjY3MTAyN30.0yYa_VFJoouSTex7uot0jL4xWuBLV6c99WBFk2J7zN4';
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

console.log(supabase);
const auth = {
  async signInWithGoogle() {
    const { user, session, error } = await supabase.auth.signInWithOAuth({
      provider: 'google'
    });
    return { user, session, error };
  },

  async signOut() {
    const { error } = await supabase.auth.signOut();
    return { error };
  },

  getCurrentUser() {
    return supabase.auth.user();    
  },
};

export default auth;
