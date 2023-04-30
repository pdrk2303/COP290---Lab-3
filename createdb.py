import openpyxl
from firsttry import app, db
app.app_context().push()
from firsttry.models import Books

workbook = openpyxl.load_workbook('books.xlsx')
worksheet = workbook.active



book_id = 1
for row in worksheet.iter_rows(values_only=True):

    # Create a new Book object with the data
    book = Books(
        id=book_id,  # Assigning book id as primary key
        url=row[0],
        title=row[1],
        titleComplete=row[2],
        description=row[3],
        imageUrl=row[4],
        genre0=row[5],
        genre1=row[6],
        genre2=row[7],
        genre3=row[8],
        publisher=row[9],
        author=row[10],
        likes=row[11],
        numPages=row[12],
        Date=row[13],
        Summary=row[14],
    )

    # Add the Book object to the session
    db.session.add(book)
    book_id += 1

# Commit the changes to the database
db.session.commit()
