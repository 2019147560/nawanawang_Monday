import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Supabase URL and Anon Key are required');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
  realtime: {
    params: {
      eventsPerSecond: 10,
    },
  },
});

// 인증 관련 함수들
export const auth = {
  // 회원가입
  signUp: async (email, password) => {
    return await supabase.auth.signUp({
      email,
      password,
    });
  },

  // 로그인
  signIn: async (email, password) => {
    return await supabase.auth.signInWithPassword({
      email,
      password,
    });
  },

  // 로그아웃
  signOut: async () => {
    return await supabase.auth.signOut();
  },

  // 현재 사용자 정보 조회
  getUser: async () => {
    return await supabase.auth.getUser();
  },

  // 세션 정보 조회
  getSession: async () => {
    return await supabase.auth.getSession();
  },

  // 인증 상태 변화 감지
  onAuthStateChange: (callback) => {
    return supabase.auth.onAuthStateChange(callback);
  },

  // 비밀번호 재설정 이메일 전송
  resetPassword: async (email) => {
    return await supabase.auth.resetPasswordForEmail(email);
  },

  // 새 비밀번호로 업데이트
  updatePassword: async (newPassword) => {
    return await supabase.auth.updateUser({
      password: newPassword,
    });
  },
};
