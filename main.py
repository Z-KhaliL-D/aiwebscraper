import streamlit as st
import requests
import pandas as pd
from io import StringIO
from scrape import scrape_website, clean_body_content, extract_body_content
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("HUGGINGFACE_API_KEY")



st.title("LLM-Powered Web Scraper 🌐")

# Input for the URL to scrape
url = st.text_input("Enter the URL you want to scrape:")

if st.button("Scrape"):
    if not url.strip():
        st.error("Please enter a valid URL.")
    else:
        with st.spinner("Scraping the URL..."):
            result = scrape_website(url)
            if result:
                body_content = extract_body_content(result)
                cleaned_content = clean_body_content(body_content)
                st.session_state.dom_content = cleaned_content
                with st.expander("View Extracted Content"):
                    st.text_area("DOM content", cleaned_content, height=300)
            else:
                st.error("Failed to retrieve content. Please check the URL.")

if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe what you want to extract from the page:")

    if st.button("Parse Content"):
        if not parse_description.strip():
            st.error("Please enter a description of what to parse.")
        else:
            with st.spinner("Parsing content..."):
                # Improved prompt template with strict table formatting
                prompt = f"""
### Instruction:
You are a precise data extraction assistant. Your ONLY task is to convert content into clean tables containing EXACTLY what is asked for - nothing more, nothing less.

### Information to Extract:
{parse_description}

### CRITICAL RULES:
- Extract ONLY the specific information requested
- Return ONLY formatted tables - NO comments, NO explanations
- If multiple pieces of data are requested, return ONLY those specific tables
- Maintain EXACT data relationships as found in source
- ANY deviation from requested data is incorrect
- Return "NO_DATA_FOUND" if requested data is not present

### Data Processing Rules:
1. TEXT HANDLING:
   - Clean all extracted text (remove excess whitespace, HTML tags, special characters)
   - Preserve meaningful text formatting (lists, paragraphs, emphasis)
   - Handle all Unicode characters properly
   - Maintain numerical precision
   - Keep data hierarchies intact

2. TABLE HANDLING:
   - Extract ALL columns and rows found in source
   - Preserve original column names, order, and relationships
   - Handle complex nested tables
   - Process merged cells appropriately
   - Maintain data type consistency
   - Handle multi-line cell content
   - Preserve table relationships and hierarchies

3. DATA TYPES TO HANDLE:
   - Text (short and long form)
   - Numbers (integers, decimals, percentages)
   - Dates (multiple formats)
   - Currency values
   - Links/URLs
   - Lists within cells
   - Boolean values (Yes/No, True/False)
   - Status indicators

### Formatting Requirements:
1. Basic Rules:
   - Start with header row containing all column names
   - Add separator row with appropriate number of dashes
   - Align columns consistently
   - Use | as column separator
   - Handle empty values with "N/A"

2. Special Cases:
   - Long text: Preserve line breaks when needed
   - Numbers: Maintain original formatting
   - Dates: Keep source format
   - Lists: Format as comma-separated values within cells

### EXAMPLES OF CORRECT FORMATS:

1. BASIC PRODUCT TABLE:
| Product ID | Name | Price | Stock | Category | Last Updated |
|------------|------|-------|--------|----------|--------------|
| P001 | Gaming Laptop | $1,299.99 | 45 | Electronics | 2024-02-13 |
| P002 | Wireless Mouse | $29.99 | N/A | Accessories | 2024-02-13 |

2. FINANCIAL DATA:
| Quarter | Revenue | Growth % | Status | Notes |
|---------|----------|-----------|--------|-------|
| Q1 2024 | $5.2M | +12.5% | On Track | Strong performance in NA |
| Q2 2024 | $4.8M | -7.8% | Warning | Supply chain issues |

3. EMPLOYEE DIRECTORY:
| ID | Name | Department | Skills | Projects | Contact |
|----|------|------------|---------|-----------|---------|
| E101 | John Doe | Engineering | Python, Java | Project A, Project B | john@example.com |
| E102 | Jane Smith | Design | UI/UX, Figma | Website Redesign | jane@example.com |

4. INVENTORY STATUS:
| Location | Items | Available | Reserved | Status |
|----------|-------|-----------|-----------|--------|
| Warehouse A | 15,000 | 12,500 | 2,500 | Active |
| Warehouse B | 8,000 | N/A | 1,200 | Maintenance |

5. EVENT SCHEDULE:
| Event | Date | Location | Capacity | Status | Details |
|-------|------|----------|-----------|---------|---------|
| Conference | 2024-03-15 | Hall A | 500/1000 | Open | Keynote: AI in 2024 |
| Workshop | 2024-03-16 | Room 401 | 50/50 | Full | Hands-on ML Training |

6. COMPLEX DATA WITH NESTED INFORMATION:
| Project | Team Lead | Members | Timeline | Milestones | Budget Status |
|---------|-----------|----------|----------|------------|---------------|
| Mobile App | Sarah Chen | John, Mike, Lisa | Q1-Q2 2024 | Design: Complete, Dev: 60% | Within budget |
| Web Portal | Alex Kim | Emma, David | Q2-Q3 2024 | Planning: 90%, Design: 30% | Over by 10% |

### Error Handling:
- No data: Return ONLY "NO_DATA_FOUND"
- Partial data: Extract ONLY available requested information
- Invalid structure: Restructure ONLY requested data into table format
- NEVER add explanatory text or comments

### Context:
Text to analyze:
{st.session_state.dom_content}

### FINAL CHECK BEFORE RESPONDING:
1. Is ONLY the requested data present?
2. Are there ANY extra comments or explanations?
3. Is the table format EXACTLY as specified?
4. Remove ANY text that isn't part of the requested data
5. Verify NO additional information is included

### Response:
"""

                model_id = "mistralai/Mistral-7B-Instruct-v0.3"
                API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
                headers = {"Authorization": f"Bearer {API_KEY}"}

                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 800,  # Increased token limit
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "return_full_text": False
                    }
                }

                try:
                    response = requests.post(API_URL, headers=headers, json=payload)
                    result_json = response.json()

                    if isinstance(result_json, list) and result_json:
                        generated_text = result_json[0].get("generated_text", "").strip()
                    else:
                        generated_text = result_json.get("generated_text", "").strip()

                    if not generated_text or generated_text == "NO_DATA_FOUND":
                        st.warning("No matching information found.")
                    elif "|" in generated_text:
                        try:
                            # Extract and clean table lines
                            lines = [
                                line.strip()
                                for line in generated_text.split('\n')
                                if '|' in line and line.strip()
                            ]

                            # Ensure we have header and data
                            if len(lines) >= 3:  # Header + separator + at least one data row
                                # Process the table
                                header = [col.strip() for col in lines[0].split('|')[1:-1]]
                                data_rows = []

                                for line in lines[2:]:  # Skip header and separator
                                    if '|' in line:
                                        cells = [cell.strip() for cell in line.split('|')[1:-1]]
                                        if len(cells) == len(header):  # Ensure correct number of columns
                                            data_rows.append(cells)

                                if data_rows:
                                    df = pd.DataFrame(data_rows, columns=header)
                                    st.write("Parsed Data:")
                                    st.dataframe(df)

                                    # Add download button
                                    csv = df.to_csv(index=False)
                                    st.download_button(
                                        "Download as CSV",
                                        csv,
                                        "parsed_data.csv",
                                        "text/csv",
                                        key='download-csv'
                                    )
                                else:
                                    st.warning("No valid data rows found in the table.")
                            else:
                                st.warning("Invalid table format in response.")

                            # Always show raw output for debugging
                            with st.expander("Show raw output"):
                                st.code(generated_text)

                        except Exception as e:
                            st.error(f"Error processing table: {str(e)}")
                            st.text("Raw output:")
                            st.text(generated_text)
                    else:
                        st.write("Parsed Data:")
                        st.write(generated_text)

                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
                    st.text("Raw output:")
                    st.text(str(e))
