import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

const supabase = createClient(supabaseUrl, supabaseKey);

export async function GET() {
  try {
    const { data, error } = await supabase
      .from('hello')
      .select('hello')
      .limit(1)
      .single();

    if (error) {
      console.error('Supabase error:', error);
      return Response.json({ error: 'Failed to fetch data' }, { status: 500 });
    }

    return Response.json(data);
  } catch (error) {
    console.error('API error:', error);
    return Response.json({ error: 'Internal server error' }, { status: 500 });
  }
}
