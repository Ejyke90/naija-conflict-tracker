import psycopg2

conn = psycopg2.connect('postgresql://neondb_owner:npg_bL6dDyw8WEMI@ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require')
cursor = conn.cursor()

print('🔧 Fixing orphan state_id references and quoted names...')
print('=' * 50)

# Fix orphan state_ids first
cursor.execute('''
    SELECT DISTINCT c.state_id, COUNT(*) as conflict_count
    FROM conflicts c 
    LEFT JOIN states s ON c.state_id = s.id 
    WHERE s.id IS NULL
    GROUP BY c.state_id
''')
orphan_states = cursor.fetchall()

if orphan_states:
    print(f'Found {len(orphan_states)} orphan state_id references:')
    for state_id, count in orphan_states:
        print(f'  State ID {state_id}: {count} conflicts')
    
    for state_id, _ in orphan_states:
        cursor.execute('UPDATE conflicts SET state_id = NULL WHERE state_id = %s', (state_id,))
    conn.commit()
    print('✅ Orphan state_ids fixed')

# Clean quoted state names
cursor.execute("SELECT id, title FROM states WHERE title LIKE '%'")
quoted_states = cursor.fetchall()

if quoted_states:
    print(f'\nFound {len(quoted_states)} quoted state names:')
    for state_id, title in quoted_states:
        clean_title = title.strip("'")
        cursor.execute('UPDATE states SET title = %s WHERE id = %s', (clean_title, state_id))
        print(f'  ID {state_id}: "{title}" -> "{clean_title}"')
    conn.commit()
    print('✅ Quoted state names cleaned')

# Test the API query
print('\n🧪 Testing API query after fixes...')
try:
    cutoff_date = '2024-08-10'
    cursor.execute('''
        WITH current_period AS (
            SELECT 
                s.title as state,
                COUNT(c.id) as incidents,
                COALESCE(SUM(
                    c.civilian_death_male + c.civilian_death_female + c.civilian_death_unknown +
                    c.security_death_male + c.security_death_female + c.security_death_unknown
                ), 0) as fatalities
            FROM conflicts c
            JOIN states s ON c.state_id = s.id
            WHERE c.incidence_date >= %s
            GROUP BY s.title
        )
        SELECT * FROM current_period ORDER BY incidents DESC LIMIT 5
    ''', (cutoff_date,))
    results = cursor.fetchall()
    print('✅ API query successful after fixes:')
    for result in results:
        print(f'  {result[0]}: {result[1]} incidents, {result[2]} fatalities')
        
except Exception as e:
    print(f'❌ API query still failing: {e}')

cursor.close()
conn.close()
print('\n🎉 State data cleanup completed!')
