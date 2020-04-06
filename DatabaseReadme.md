#### SQL that we can directly run on PostgreSQL.

```sql
CREATE TABLE ModerationTable (
  ID           SERIAL NOT NULL,
  ARTICLE_ID   VARCHAR(255) PRIMARY KEY NOT NULL UNIQUE,

  TITLE        VARCHAR(255) NOT NULL,
  AUTHOR       VARCHAR(255),
  SOURCE_ID    VARCHAR(255) NOT NULL,
  ARTICLE_URL  VARCHAR(255),
  IMAGE_URL    VARCHAR(255),
  CONTENT      TEXT NOT NULL,
  SUMMARY      TEXT,
  CATEGORY     VARCHAR(255),
  KEYWORDS     TEXT[],

  POSITIVITY   INT,
  MOD_STATUS   VARCHAR(255),
  BOOST_FACTOR FLOAT8,

  SPECIFICITY  VARCHAR(255) NOT NULL,
  COUNTRY      VARCHAR(255),
  STATE        VARCHAR(255),
  REGION       VARCHAR(255),
  CITY         VARCHAR(255),
  LONGITUDE    FLOAT8,
  LATITUDE     FLOAT8,

  PUBLISHED_AT TIME,
  CREATED_AT   TIME NOT NULL DEFAULT NOW(),
  CREATED_BY   VARCHAR(255),
  UPDATED_AT   TIME DEFAULT NOW(),
  UPDATED_BY   VARCHAR(255)
);
```

```sql
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
BEFORE UPDATE ON ModerationTable
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
```

```
CREATE TABLE SourceTable (
  ID           SERIAL NOT NULL,
  SOURCE_ID    VARCHAR(255) PRIMARY KEY NOT NULL UNIQUE,
  LOGO_URL     VARCHAR(255),
  TYPE         VARCHAR(255) NOT NULL,
  SPECIFICITY  VARCHAR(255),
  COUNTRY      VARCHAR(255),
  STATE        VARCHAR(255),
  REGION       VARCHAR(255),
  CITY         VARCHAR(255),
  SOURCE_URL   VARCHAR(255),

  CREATED_AT   TIME NOT NULL DEFAULT NOW(),
  UPDATED_AT   TIME DEFAULT NOW()
);
```

#### Ref
- https://www.postgresql.org/docs/9.5/datatype.html
- https://x-team.com/blog/automatic-timestamps-with-postgresql/


#### Note For ModerationTable:

- Only one table for now for moderation AND MLProcessing
- article_id should be used for direct queries. It should be in uuid4 format. Please ignore the id column
- source_id is the id specified in the SourceTable. Example: {"cdc", "who", "nyt", "twitter"} It must be unique. This must be converted from News API format to our format.

```json
"source": {
    "id": null,
    "name": "Latimes.com"
}
```

to `"source_id": "la_times"` ... etc ...

- These fields are optional, and cannot be used in the UI: {author, image_url, created_by} Do not waste time filling these when manually filling it.

- other columns, even the ones without non null specifier, must NOT be null, unless the data cannot be found.

- mod_status can only be one of these values: {"pending", "approved", "rejected", "removed"}

- BOOST_FACTOR: Articles will be sorted based on the following formula:

RANKING_SCORE = (numClicks * 1.0) * (1/(numDaysAgoPublished*2.0)) + 1/(numKilometersFromSourceToUser * 0.05) + BOOST_FACTOR

Value for each section is capped at a value to prevent infinity. Exact values of the number to be adjusted. To simplify, we can just use static distance radius and sort by reverse chronological order.

- CATEGORY must be one of these values: {"health", "food", "government", "social", "housing", "labor"} (final decision pending)

- POSITIVITY must be from 0 to 10, 10 being really positive, 5 being neutral

- specificity must be one of the following: {"international", "national", "state", "regional", "county", "city"}

- "country" must be in ISO county code format. eg: 'GB' 'US'

- For example. If "specificity" is national, "state" and "city" columns will be NULL, etc...

- STATE, REGION, and CITY are all full name of the location. No special symbols or punctuations please.

- LONGITUDE and LATITUDE will be filled out by script only.

- location fields are to be filled out manually until ML script is ready.


#### Note For SourceTable
- type must be one of the following: {"government", "news", "hospital", "social"}

- specificity must be one of the following: {"international", "national", "state", "regional", "county", "city"} A source’s content may apply beyond or below its intended audience. Individual articles should be tagged accordingly.
