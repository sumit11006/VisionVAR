import { redirect } from 'next/navigation';
import { MATCH_ID } from '@/lib/mockData/match';

export default function RootPage() {
  redirect(`/sessions`);
}
