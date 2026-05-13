// src/lib/fetchPrograms.ts
import { supabase } from './supabase';
import type { Program, ProgramDetail } from '@/types';

// ─── Programs + Chips ───────────────────────────────────────────
export async function fetchPrograms(): Promise<Program[]> {
  const { data: programs, error } = await supabase
    .from('programs')
    .select('*')
    .order('id');

  if (error) throw error;

  const { data: chips, error: chipsError } = await supabase
    .from('program_chips')
    .select('program_id, chip');

  if (chipsError) throw chipsError;

  return programs.map((p) => ({
    id: p.id,
    tag: p.tag,
    dDay: p.d_day,
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
  // maybeSingle() — 데이터 없어도 에러 대신 null 반환
  const { data: detail, error } = await supabase
    .from('program_details')
    .select('*')
    .eq('program_id', id)
    .maybeSingle();

  if (error) throw error;

  // 커리큘럼도 없으면 빈 배열
  const { data: curriculum } = await supabase
    .from('program_curriculum')
    .select('weeks, description')
    .eq('program_id', id)
    .order('sort_order');

  return {
    intro: detail?.intro ?? '',
    description: detail?.description ?? '',
    qualification: detail?.qualification ?? '',
    curriculum: (curriculum ?? []).map((c) => ({
      weeks: c.weeks,
      desc: c.description,
    })),
    org: {
      name: detail?.org_name ?? '',
      region: detail?.region ?? '',
      phone: detail?.phone ?? '',
      kakao: detail?.kakao ?? '',
      homepage: detail?.homepage ?? '',
      email: detail?.email ?? '',
    },
  };
}
