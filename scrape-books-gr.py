from bs4 import BeautifulSoup
from operator import itemgetter
from requests import get
from sys import argv

subject = argv[1]
start_page = int(argv[2])
stop_page = int(argv[3])
average_rating_threshold = float(argv[4])
rating_threshold = int(argv[5])


def scrape_books(subject="science", start_page=1, stop_page=11, average_rating_threshold=4.2, ratings_threshold=50000):
    if not (isinstance(subject, str) and isinstance(start_page, int) and isinstance(stop_page, int) and isinstance(average_rating_threshold, float) and isinstance(ratings_threshold, int)):
        raise TypeError("Incompatible types of arguments")

    if not (len(subject) > 0 and start_page > 0 and stop_page > 0 and stop_page > start_page and 5.0 >= average_rating_threshold >= 0.0 and ratings_threshold > 0):
        raise TypeError("Incompatible values of arguments")

    try:
        base_url = "https://www.goodreads.com"
        best_books = []
        for page in range(start_page, stop_page):
            url = f"{base_url}/search?page={page}&qid=E5tgn4SYZ5&query={subject}&tab=books&utf8=✓"
            res = get(url)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            books = soup.select('[itemtype="http://schema.org/Book"]')

            for book in books:
                ratings_string = book.select_one(".minirating").contents[-1]
                average_rating, *_, ratings, _ = ratings_string.split()

                if float(average_rating) > average_rating_threshold and int(ratings.replace(",", "")) > ratings_threshold:
                    title = book.select_one(".bookTitle").get_text(strip=True)
                    link = book.select_one(".bookTitle")["href"]
                    author = book.select_one(
                        ".authorName").get_text(strip=True)
                    best_book = {"author": author, "title": title,
                                 "average_rating": average_rating, "ratings": ratings, "link": f"{base_url}{link}"}
                    best_books.append(best_book)

        return best_books

    except Exception as err:
        print(f"There was a problem during scraping books: {err}")


def save_books(book_list=[], subject="subject"):
    if not (isinstance(book_list, list) and isinstance(subject, str)):
        raise TypeError("Incompatible types of arguments")
    if len(book_list) > 0:
        file = open(f"best-books-{subject}.md", "w")
        try:
            file.write(f"## Best books about {subject}\n")
            for book in book_list:
                title, author, average_rating, ratings, link = itemgetter(
                    "title", "author", "average_rating", "ratings", "link")(book)
                list_item = f'- [{title}]({link})<br />by {author} | <small title="Average rating">{average_rating}⭐</small> <small>{ratings} ratings</small>\n'
                file.write(list_item)
        finally:
            file.close()


best_books = scrape_books(subject, start_page, stop_page,
                          average_rating_threshold, rating_threshold)
save_books(best_books, subject)
