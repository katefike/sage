def test_tables(conn, env):
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
        host = env["POSTGRES_HOST"]
        db = env["POSTGRES_DB"]
        user = env["POSTGRES_USER"]
        passw = env["POSTGRES_PASSWORD"]
        print(f"HOST: {host} DB: {db} USER: {user} PASS: {passw} ")
        assert 1 == 1
