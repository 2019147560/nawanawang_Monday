// src/lib/fetchPrograms.ts
import { supabase } from './supabase';
import type { Program, ProgramDetail } from '@/types';

// ─── Programs + Chips ───────────────────────────────────────────
export async function fetchPrograms(): Promise<Program[]> {
  // programs 테이블
  const { data: programs, error } = await supabase
    .from('programs')
    .select('*')
    .order('id');

  if (error) throw error;

  // program_chips 테이블
  const { data: chips, error: chipsError } = await supabase
    .from('program_chips')
    .select('program_id, chip');

  if (chipsError) throw chipsError;

  // chips를 program_id 기준으로 묶어서 Program에 합치기
  return programs.map((p) => ({
    id: p.id,
    tag: p.tag,
    dDay: p.d_day,           // DB 컬럼명 → camelCase 변환
    title: p.title,
    org: p.org,
    status: p.status,
    bg: p.bg,
    weeks: p.weeks,
    deadline: p.deadline,
    statusVariant: p.status_variant,
    chips: chips
      .filter((c) => c.program_id === p.id)
      .map((c) => c.chip),
  }));
}

// ─── Program Detail (상세 + 커리큘럼) ────────────────────────────
export async function fetchProgramDetail(id: number): Promise<ProgramDetail> {
  const { data: detail, error } = await supabase
    .from('program_details')
    .select('*')
    .eq('program_id', id)
    .single();

  if (error) throw error;

  const { data: curriculum, error: currError } = await supabase
    .from('program_curriculum')
    .select('weeks, description')
    .eq('program_id', id)
    .order('sort_order');

  if (currError) throw currError;

  return {
    intro: detail.intro,
    description: detail.description,
    qualification: detail.qualification,
    curriculum: curriculum.map((c) => ({
      weeks: c.weeks,
      desc: c.description,
    })),
    org: {
      name: detail.org_name,
      region: detail.region,
      phone: detail.phone,
      kakao: detail.kakao,
      homepage: detail.homepage,
      email: detail.email,
    },
  };
}
