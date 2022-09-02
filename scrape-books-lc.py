from bs4 import BeautifulSoup
from operator import itemgetter
from requests import get


def scrape_books(start_page=1, stop_page=11, average_rating_threshold=8.0, ratings_threshold=2000):
    if not (isinstance(start_page, int) and isinstance(stop_page, int) and isinstance(average_rating_threshold, float) and isinstance(ratings_threshold, int)):
        raise TypeError("Incompatible types of arguments")

    if not (start_page > 0 and stop_page > 0 and stop_page > start_page and 10.0 >= average_rating_threshold >= 0.0 and ratings_threshold > 0):
        raise TypeError("Incompatible values of arguments")

    try:
        base_url = "https://lubimyczytac.pl"
        best_books = []
        for page in range(start_page, stop_page):
            url = f"{base_url}/katalog?page={page}&listId=booksFilteredList&category[]=67&rating[]=0&rating[]=10&publishedYear[]=1200&publishedYear[]=2022&catalogSortBy=ratings-desc&paginatorType=Standard"
            res = get(url)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            books = soup.select(".authorAllBooks__single")

            for book in books:
                average_rating = float(book.select_one(
                    ".listLibrary__ratingStarsNumber").get_text(strip=True).replace(",", "."))
                ratings_string = book.select_one(
                    ".listLibrary__ratingAll").get_text(strip=True).split()[0]
                ratings = int(0 if ratings_string ==
                              "ocen" else ratings_string)

                if average_rating > average_rating_threshold and ratings > ratings_threshold:
                    title = book.select_one(
                        ".authorAllBooks__singleTextTitle").get_text(strip=True)
                    author = book.select_one(
                        ".authorAllBooks__singleTextAuthor").get_text(strip=True)
                    link = book.select_one(
                        ".authorAllBooks__singleTextTitle")["href"]
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
        file = open(f"najlepsze-ksiazki-{subject}.md", "w")
        try:
            file.write(f"## Najlepsze książki z kategorii: {subject}\n")
            for book in book_list:
                title, author, average_rating, ratings, link = itemgetter(
                    "title", "author", "average_rating", "ratings", "link")(book)
                list_item = f'- [{title}]({link})<br />autorstwa {author} | <small title="Średnia ocen">{average_rating}⭐</small> <small>{ratings} ocen</small>\n'
                file.write(list_item)
        finally:
            file.close()


best_books = scrape_books(1, 40, 7.9, 250)
save_books(best_books, "psychologia")
