import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd

def fetch_amazon_collection(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch Amazon collection. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    product_list = []
    products = soup.find_all("div", attrs={'data-component-type': 's-search-result'})
    for product in products:
        pd_data = {
            'Name': product.find("h2", attrs={'class': 'a-size-medium a-spacing-none a-color-base a-text-normal'}).text.strip() if product.find("h2", attrs={'class': 'a-size-medium a-spacing-none a-color-base a-text-normal'}) else "N/A",
            'Price': product.find("span", attrs={'class': 'a-price-whole'}).text.strip() if product.find("span", attrs={'class': 'a-price-whole'}) else "N/A",
            'Discount': product.find("span", attrs={'class': 'a-price a-text-price'}).find("span", attrs={'class': 'a-offscreen'}).text.strip() if product.find("span", attrs={'class': 'a-price a-text-price'}) else "N/A",
            'Availability': "Available" if product.find("span", attrs={'class': 'a-declarative'}) else "Out of Stock",
            'Ratings': product.find("span", attrs={'class': 'a-icon-alt'}).text.strip() if product.find("span", attrs={'class': 'a-icon-alt'}) else "N/A"
        }
        product_list.append(pd_data)

    return pd.DataFrame(product_list)

def fetch_snapdeal_collection(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch Snapdeal collection. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    product_list = []
    products = soup.find_all("div", attrs={"ismlt": "false"})
    for product in products:
        pd_data = {
            'Name': product.find("p", attrs={'class': 'product-title'}).text.strip() if product.find("p", attrs={'class': 'product-title'}) else "N/A",
            'Price': product.find("span", attrs={'class': 'lfloat product-price'}).text.strip() if product.find("span", attrs={'class': 'lfloat product-price'}) else "N/A",
            'Discount': product.find("div", attrs={'class': 'product-discount'}).text.strip() if product.find("div", attrs={'class': 'product-discount'}) else "N/A",
            'Availability': "Available",
            'Ratings': product.find("div", attrs={'class': 'filled-stars'}).attrs.get('style', "0").split(':')[1].replace('%', '').strip() if product.find("div", attrs={'class': 'filled-stars'}) else "N/A"
        }
        product_list.append(pd_data)

    return pd.DataFrame(product_list)

def fetch_amazon_individual(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch Amazon individual product. Status code: {response.status_code}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "html.parser")
    name = soup.find("span", attrs={'id': 'productTitle'}).text.strip() if soup.find("span", attrs={'id': 'productTitle'}) else "N/A"
    reviews = [review.find("span", attrs={'class': 'a-size-base review-text review-text-content'}).text.strip() for review in soup.find_all("div", attrs={'data-hook': 'review'})]

    if not reviews:
        reviews = ["No reviews found"]

    product_reviews = pd.DataFrame({"Product Name": [name] * len(reviews), "Review": reviews})
    return product_reviews

def fetch_snapdeal_individual(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch Snapdeal individual product. Status code: {response.status_code}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "html.parser")
    name = soup.find("span", attrs={'class': 'section-head customer_review_tab'}).text.strip() if soup.find("span", attrs={'class': 'section-head customer_review_tab'}) else "N/A"
    reviews_section = soup.find_all("div", attrs={'class': 'commentlist'})
    reviews = [review.text.strip() for review in reviews_section] if reviews_section else ["No reviews found"]

    product_reviews = pd.DataFrame({"Product Name": [name] * len(reviews), "Review": reviews})
    return product_reviews

def main():
    st.title("E-Commerce Product Scraper")
    st.sidebar.header("Scraper Options")

    option = st.sidebar.radio("Select an option", ("Amazon Collection", "Snapdeal Collection", "Individual Product"))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    if option == "Amazon Collection":
        url = st.text_input("Enter Amazon collection URL:")
        if st.button("Scrape Amazon Collection"):
            data = fetch_amazon_collection(url, headers)
            if not data.empty:
                st.dataframe(data)
                csv = data.to_csv(index=False)
                st.download_button("Download CSV", data=csv, file_name="amazon_collection.csv", mime="text/csv")

    elif option == "Snapdeal Collection":
        url = st.text_input("Enter Snapdeal collection URL:")
        if st.button("Scrape Snapdeal Collection"):
            data = fetch_snapdeal_collection(url, headers)
            if not data.empty:
                st.dataframe(data)
                csv = data.to_csv(index=False)
                st.download_button("Download CSV", data=csv, file_name="snapdeal_collection.csv", mime="text/csv")

    elif option == "Individual Product":
        platform = st.selectbox("Select Platform", ("Amazon", "Snapdeal"))
        url = st.text_input(f"Enter {platform} individual product URL:")
        if st.button("Scrape Individual Product"):
            if platform == "Amazon":
                product_reviews = fetch_amazon_individual(url, headers)
            else:
                product_reviews = fetch_snapdeal_individual(url, headers)

            if not product_reviews.empty:
                st.dataframe(product_reviews)
                csv = product_reviews.to_csv(index=False)
                st.download_button("Download CSV", data=csv, file_name=f"{platform.lower()}_individual_reviews.csv", mime="text/csv")

if __name__ == "__main__":
    main()