import re


def add_p_tags(text):
    # Split the input text into paragraphs based on one or more newlines
    paragraphs = re.split(r'\n+', text.strip())

    # Wrap each line with <p> tags if it doesn't already start with an HTML tag
    for i in range(len(paragraphs)):
        if not re.match(r'^\s*<\w+>', paragraphs[i]):
            paragraphs[i] = '<p>' + paragraphs[i] + '</p>'

    return '\n'.join(paragraphs)


def convert_bullets_to_html(text):
    def replace_with_ul(match):
        items = match.group(0).strip().split('\n')
        li_items = ['<li>' + item[2:].strip() + '</li>' for item in items]
        return '<ul>\n' + '\n'.join(li_items) + '\n</ul>'

    # Replace bulleted lists with <ul><li>...</li></ul>
    text = re.sub(r'(?m)^\s*-\s*.+((\n\s*-.*)*)', replace_with_ul, text)
    return text


def convert_numbers_to_ol(text):
    def replace_with_ol(match):
        items = match.group(0).strip().split('\n')
        li_items = ['<li>' + re.sub(r'^\d+\.\s*', '', item).strip() + '</li>' for item in items]
        return '<ol>\n' + '\n'.join(li_items) + '\n</ol>'

    # Replace numbered lists with <ol><li>...</li></ol>
    text = re.sub(r'(?m)^\s*\d+\.\s*.+((\n\s*\d+\..*)*)', replace_with_ol, text)
    return text


def remove_double_quotes(text):
    text = re.sub(r'^\"', '', text)
    text = re.sub(r'\"$', '', text)
    return text


def remove_empty_html_tags(text):
    pattern = r'<(\w+)\s*>\s*</\1>'
    cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return cleaned_text

def remove_unwrapped_headers(text):
    pattern = r'\b[hH][123]:?\s*|#{1,3}\s*'
    cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return cleaned_text


def add_html_tags(text):
    text = convert_bullets_to_html(text)
    text = convert_numbers_to_ol(text)
    text = add_p_tags(text)
    text = remove_empty_html_tags(text)
    return text

def remove_start_and_ending_new_lines(text):
    return re.sub(r'^[\r\n]+|[\r\n]+$', '', text)