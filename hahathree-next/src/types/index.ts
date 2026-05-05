export type StatusVariant = 'soon' | 'closed' | 'open';

export interface Program {
  id: number;
  tag: string;
  dDay: string;
  title: string;
  org: string;
  status: string;
  bg: string;
  chips: string[];
  weeks: string;
  deadline: string;
  statusVariant?: StatusVariant;
}

export interface CurriculumItem {
  weeks: string;
  desc: string;
}

export interface OrgInfo {
  name: string;
  region: string;
  phone: string;
  kakao: string;
  homepage: string;
  email: string;
}

export interface ProgramDetail {
  intro: string;
  description: string;
  qualification: string;
  curriculum: CurriculumItem[];
  org: OrgInfo;
}

export interface Review {
  id: number;
  name: string;
  program: string;
  body: string;
}

export interface SupportPolicy {
  id: number;
  title: string;
  category: string;
  summary: string;
}

export type FilterKey = 'region' | 'level' | 'mode' | 'period' | 'status' | 'people';
export type FilterValues = Record<FilterKey, string[]>;
