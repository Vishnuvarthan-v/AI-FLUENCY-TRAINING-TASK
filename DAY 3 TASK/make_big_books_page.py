# Create a large HTML file for testing the agent guards

with open("big_books.html", "w", encoding="utf-8") as file:

    file.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Big Bookstore Catalogue</title>
</head>
<body>

<h1>Big Bookstore Catalogue</h1>

<p>
This page contains many book records.
It is intentionally large for testing
observation truncation and character budgets.
</p>

<h2>Book Catalogue</h2>
""")

    for i in range(1, 3001):

        file.write(f"""
<div class="book">

    <h3>Book {i}: Advanced Programming Book {i}</h3>

    <p>
        Book ID: BOOK{i:04d}
    </p>

    <p>
        Title: Advanced Programming Book {i}
    </p>

    <p>
        Price: Rs. {500 + (i % 500)}
    </p>

    <p>
        Category: Programming and Computer Science
    </p>

    <p>
        Author: Author {i}
    </p>

    <p>
        Stock: {10 + (i % 50)}
    </p>

    <p>
        Description:
        This is a detailed description for book {i}.
        This book contains programming concepts,
        algorithms, data structures, software development,
        artificial intelligence, machine learning,
        databases, and computer science fundamentals.
    </p>

</div>
""")

    file.write("""
</body>
</html>
""")

print("big_books.html created successfully.")