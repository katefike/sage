def test_tables(conn, ENV):
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
        host = ENV["POSTGRES_HOST"]
        db = ENV["POSTGRES_DB"]
        user = ENV["POSTGRES_USER"]
        passw = ENV["POSTGRES_PASSWORD"]
        print(f"HOST: {host} DB: {db} USER: {user} PASS: {passw} ")
        assert 0 == 1
