import psycopg2

def insertSampleData():
    connection = None
    cursor = None

    try:
       connection = psycopg2.connect(user="postgres",
                                      password="",
                                      port="5432",
                                      host="",
                                      database="postgres")
       cursor = connection.cursor()
       postgres_insert_query = """INSERT INTO ModerationTable (ARTICLE_ID, SOURCE_ID, TITLE, CONTENT, SPECIFICITY, PUBLISHED_AT) VALUES (%s,%s,%s,%s,%s,%s)"""
       record_to_insert = ('article1', 'source1', 'Hello Google Cloud PostreSQL!', 'Example article content', 'national', '2020-04-05 05:53:00')
       cursor.execute(postgres_insert_query, record_to_insert)
       connection.commit()
       # cursor.execute("select * from ModerationTable")
       print('Fetching Records...')
       print(cursor.fetchall())

    except (Exception, psycopg2.Error) as error :
       print("Postgres Error!", error)

    finally:
        #closing database connection.
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("PostgreSQL connection is closed")
