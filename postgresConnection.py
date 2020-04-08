import psycopg2


class PostgresConnection:

    # Default table name is ModerationTable
    def __init__(self, tableName='ModerationTable'):
        connection = None
        cursor = None
        try:
           connection = psycopg2.connect(user="postgres",
                                          password="",
                                          port="5432",
                                          host="",
                                          database="postgres")
           cursor = connection.cursor()
        except (Exception, psycopg2.Error) as error :
            print("Postgres Error!", error)

        self.connection = connection
        self.cursor = cursor
        self.tableName = tableName

    def __del__(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    # Must call commit
    def commit(self):
        self.connection.commit()
        print('Commiting Record...')

    def insertNewArticle(self, article_id, title, author, source_id, article_url, content, mod_status, published_at, created_by):
        try:
           postgres_insert_query = f"INSERT INTO {self.tableName} (ARTICLE_ID, TITLE, AUTHOR, SOURCE_ID, ARTICLE_URL, CONTENT, MOD_STATUS, PUBLISHED_AT, CREATED_BY, UPDATED_BY) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
           record_to_insert = (article_id, title, author, source_id, article_url, content, mod_status, published_at, created_by, created_by)
           self.cursor.execute(postgres_insert_query, record_to_insert)

        except (Exception, psycopg2.Error) as error :
            print("Postgres Error!", error)

    def printAllArticles(self):
        try:
            postgres_query = f"select * from {self.tableName}"
            self.cursor.execute(postgres_query)
            print('Fetching Records...')
            print(self.cursor.fetchall())
        except (Exception, psycopg2.Error) as error :
            print("Postgres Error!", error)


    def forceDeleteAllArticles(self):
        try:
            query = f"DELETE FROM {self.tableName}"
            self.cursor.execute(query)
            print(f'Deleting all records... Query:{query}')
        except (Exception, psycopg2.Error) as error :
            print("Postgres Error!", error)

    def deleteArticleByArticleId(self, article_id):
        try:
            query = f"DELETE FROM {self.tableName} WHERE ARTICLE_ID=(%s)"
            self.cursor.execute(query, article_id)
            print('Deleting Record...')
        except (Exception, psycopg2.Error) as error :
            print("Postgres Error!", error)






























#
