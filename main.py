import csv
import os
from datetime import time

from selenium import webdriver
from selenium.webdriver.common.by import By


def scrape_leetcode_questions():
    base_url = "https://leetcode.com/problemset/all/"

    # Configure Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode

    # Create a new Chrome browser instance
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the desired URL
    driver.get(base_url)

    # Wait for the page to load
    time.sleep(5)

    questions = []

    a_tags = driver.find_elements(By.XPATH, "//a[@class='inline-flex items-center']")

    for a_tag in a_tags:
        category_url = a_tag.get_attribute("href")

        # Create a new Chrome browser instance for each category
        category_driver = webdriver.Chrome(options=chrome_options)
        category_driver.get(category_url)
        time.sleep(5)

        title_div_tags = category_driver.find_elements(By.XPATH, "//div[@class='title-cell__ZGos']")

        for title_div_tag in title_div_tags:
            question_url = title_div_tag.find_element(By.XPATH, ".//a").get_attribute("href")

            # Create a new Chrome browser instance for each question
            question_driver = webdriver.Chrome(options=chrome_options)
            question_driver.get(question_url)
            time.sleep(5)

            question_title = question_driver.find_element(By.XPATH, "//h1[@class='inline-wrap mr-2']").text.strip()
            question_number = question_driver.find_element(By.XPATH, "//span[@class='text-label-3']").text.strip()
            question_category = a_tag.text.strip()

            question_content_div = question_driver.find_element(By.XPATH,
                                                                "//div[@data-track-load='description_content']")
            question_content = question_content_div.text.strip() if question_content_div else ""

            question_constraints_div = question_driver.find_element(By.XPATH,
                                                                    "//div[@data-track-load='constraints_content']")
            question_constraints = question_constraints_div.text.strip() if question_constraints_div else ""

            question_driver.quit()

            question_data = {
                "Number": question_number,
                "Title": question_title,
                "Category": question_category,
                "Content": question_content,
                "Constraints": question_constraints
            }
            questions.append(question_data)

        category_driver.quit()

    driver.quit()

    return questions


def save_to_csv(questions):
    fieldnames = ["Number", "Title", "Category", "Content", "Constraints"]
    file_exists = os.path.isfile("leetcode_questions.csv")

    with open("leetcode_questions.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for question in questions:
            if not is_question_exists(question["Number"]):
                writer.writerow(question)


def is_question_exists(question_number):
    with open("leetcode_questions.csv", "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip the header row
        for row in reader:
            if row[0] == question_number:
                return True
    return False


if __name__ == "__main__":
    questions = scrape_leetcode_questions()
    save_to_csv(questions)
