import streamlit as st
import xml.etree.ElementTree as ET
import re
import os 


st.set_page_config(page_title="Search PubMed Articles", page_icon="image/logo_csie2.png")
st.image("image/title_search.png")
st.sidebar.image("image/logo_NCKU.jpeg", use_column_width=True)
# Function to parse XML and extract data
def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    data = []

    for article in root.findall('.//PubmedArticle'):
        pmid_element = article.find('.//PMID')
        if pmid_element is not None:
            pmid = pmid_element.text
        else:
            pmid = ''

        title_element = article.find('.//ArticleTitle')
        if title_element is not None:
            title = title_element.text
        else:
            title = ''

        abstract_element = article.find('.//Abstract/AbstractText')
        if abstract_element is not None:
            abstract = abstract_element.text
        else:
            abstract = ''

        # Extracting additional information
        journal_info = article.find('.//Journal')
        journal_title_element = journal_info.find('.//Title')
        if journal_title_element is not None:
            journal_title = journal_title_element.text
        else:
            journal_title = ''

        journal_issn_element = journal_info.find('.//ISSN[@IssnType="Electronic"]')
        if journal_issn_element is not None:
            journal_issn = journal_issn_element.text
        else:
            journal_issn = ''

        pubdate = journal_info.find('.//PubDate')
        pubdate_year_element = pubdate.find('Year')
        pubdate_month_element = pubdate.find('Month')

        pubdate_year = pubdate_year_element.text if pubdate_year_element is not None else ''
        pubdate_month = pubdate_month_element.text if pubdate_month_element is not None else ''
        
        # Check if 'Day' element exists before accessing it
        pubdate_day_element = pubdate.find('Day')
        pubdate_day = pubdate_day_element.text if pubdate_day_element is not None else ''

        authors = article.find('.//AuthorList')
        author_list = [f"{author.find('ForeName').text} {author.find('LastName').text}" for author in authors.findall('.//Author')]

        # Check if 'KeywordList' element exists before accessing it
        keyword_list_element = article.find('.//KeywordList[@Owner="NOTNLM"]')
        if keyword_list_element is not None:
            keyword_list = [keyword.text for keyword in keyword_list_element.findall('.//Keyword')]
        else:
            keyword_list = []

        data.append({
            'PMID': pmid,
            'Title': title,
            'Journal Title': journal_title,
            'ISSN': journal_issn,
            'Publication Date': f"{pubdate_year}-{pubdate_month}-{pubdate_day}",
            'Abstract': abstract,
            'Authors': ', '.join(author_list),
            'Keywords': ', '.join(keyword_list)
        })

    return data

# Function to search and highlight occurrences of the search term
def search_and_highlight(article, search_term, case_sensitive=True):
    highlighted_fields = {}
    
    for key, value in article.items():
        flags = 0 if not case_sensitive else re.IGNORECASE
        highlighted_text = re.sub(
            fr'({re.escape(search_term)})',
            r'<span style="background-color: yellow">\1</span>',
            value,
            flags=flags,
        )
        highlighted_fields[key] = highlighted_text

    return highlighted_fields


# Sidebar
st.sidebar.title("File Management")
uploaded_files = st.sidebar.file_uploader("Upload PubMed XML Files", type=["xml"], accept_multiple_files=True)

# Page

# # Page
# st.title("PubMed Document Retrieval")
# st.subheader("Search PubMed Articles")

# Initialize data list
data = []

# Load uploaded files
for uploaded_file in uploaded_files:
    data += parse_xml(uploaded_file)

# Search
keyword = st.text_input("Enter keyword to search for:")
case_sensitive = st.toggle("Case Sensitive Search", value=True)
matching_articles = []

if st.button("Search"):
    for article in data:
        highlighted_fields = search_and_highlight(article, keyword, case_sensitive)
        # Check if any field was highlighted
        if any('<span style="background-color: yellow">' in value for value in highlighted_fields.values()):
            matching_articles.append(highlighted_fields)

    if not matching_articles:
        st.write("No matching articles found.")
    else:
        for idx, article in enumerate(matching_articles, start=1):
            st.markdown(f'<p style="text-align:center; color:red;">Matching Article {idx}:</p>', unsafe_allow_html=True)
            # st.write(f"Matching Article {idx}:")

            # Calculate and display document statistics
            num_characters = len(article['Abstract'])
            num_words = len(article['Abstract'].split())
            num_sentences = len(re.split(r'[.!?]', article['Abstract']))

            # st.write(f"Number of Characters: {num_characters}")
            # st.write(f"Number of Words: {num_words}")
            # st.write(f"Number of Sentences (EOS): {num_sentences}")

            # Create a table for document statistics
            statistics_table = {
                "Statistic": ["Number of Characters", "Number of Words", "Number of Sentences (EOS)"],
                "Value": [num_characters, num_words, num_sentences]
            }
            st.table(statistics_table)

            # st.write("Full Information:")
            for key, value in article.items():
                if key in ['PMID', 'Title', 'Journal Title', 'ISSN', 'Publication Date', 'Authors', 'Keywords']:
                    # Format these fields as bold and italic
                    st.markdown(f"**_{key}_**: {value}", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{key}**: {value}", unsafe_allow_html=True)
            st.write("---")
