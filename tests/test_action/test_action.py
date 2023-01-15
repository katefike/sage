def test_tables(conn):
    with conn, conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                table_name
            FROM
                information_schema.tables
            WHERE
                table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """
        )
        for result in cursor.fetchall():
            table_name = result[0]
            print(f"FOUND {table_name}")
        print(f"CHECK")
        assert 0 == 1
