# ZipTieTask

## Python Developer Recruitment Task

The goal of this task is to create a fully working API solution based on Python FastAPI and a MySQL database.

Your project needs to meet the following requirements:
- The database needs to contain at least 2 tables connected with one-to-many relationships (remember to create foreign key(s)).
- The tables should have at least 4 columns each and a properly defined primary key.
- All of the columns should be of the minimal possible size (and type) for their purpose.
- The tables should be mapped using SQLAlchemy ORM models.
- The API should have at least 3 endpoints defined:
    - Adding records into table 1.
    - Adding records into table 2.
    - Reading records from table 1 after joining corresponding data from table 2.
- The endpoints should have defined input and response models and basic data validation logic.
- All of the database operations within endpoints should utilize SQLAlchemy ORM models.
- The endpoint responsible for reading the data should support pagination.
- requirements.txt should be generated.
- Docstrings are optional, but welcomed.
