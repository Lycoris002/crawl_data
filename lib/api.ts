// lib/api.ts – Fetch wrapper calling /api/* (proxied to FastAPI)

export interface Major {
  id: string;
  major_code: string;
  major_name: string;
  school: string;
  display_name: string;
}

export interface Subject {
  code: string;
  name: string;
  credits: number;
}

export interface Semester {
  semester?: number;
  year?: number;
  subjects: Subject[];
}

export interface MajorDetail {
  id: string;
  major_code: string;
  major_name: string;
  school: string;
  scores: Record<string, number>;
  curriculum: Semester[];
  outcomesSummary?: string;
}

export async function searchMajors(): Promise<Major[]> {
  const res = await fetch("/api/search");
  if (!res.ok) throw new Error("Failed to fetch majors");
  return res.json();
}

export async function getCurriculum(majorId: string): Promise<MajorDetail> {
  const res = await fetch(`/api/curriculum/${majorId}`);
  if (!res.ok) throw new Error("Failed to fetch curriculum");
  return res.json();
}

export async function syncData(): Promise<{
  status: string;
  message: string;
  count: number;
}> {
  const res = await fetch("/api/sync", { method: "POST" });
  if (!res.ok) throw new Error("Failed to sync data");
  return res.json();
}
