import re


def add_p_tags(text, from_example_command:bool = False):
    # Split the input text into paragraphs based on one or more newlines
    paragraphs = re.split(r'\n+', text.strip())

    # Wrap each line with <p> tags if it doesn't already start with an HTML tag
    for i in range(len(paragraphs)):
        if not re.match(r'^\s*<[\/\w]+>', paragraphs[i]):
            open_p_tags = '<p class="lh-2">' if from_example_command else '<p>'
            paragraphs[i] = open_p_tags + paragraphs[i] + '</p>'

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


def remove_double_astrix(text):
    text = re.sub(r'\*\*', '', text)
    return text


def remove_empty_html_tags(text):
    pattern = r'<(\w+)\s*>(\s|\\n|\\r|\\t)*<\/\1>'
    
    for i in range(3):
        cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        if not re.match(pattern, cleaned_text):
            break
        
    return cleaned_text


def remove_unwrapped_headers(text):
    pattern = r'\b[hH][123]:?\s*|#{1,3}\s*'
    cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    cleaned_text = cleaned_text.replace("\"", "")
    cleaned_text = cleaned_text.replace("<>", "")
    cleaned_text = cleaned_text.replace("</>", "")
    return cleaned_text


def add_html_tags(text, from_example_command:bool = False, faq_content: bool = False):
    text = convert_bullets_to_html(text)
    if not faq_content:
        text = convert_numbers_to_ol(text)
        text = add_p_tags(text, from_example_command)
    else:
        qa = re.split(r'\n+\s*', text.strip())
        for i in range(len(qa)):
            qa[i] = add_question_tags(qa[i]) if i % 2 == 0 else add_response_tags(qa[i]) 
        text = '\n'.join(qa)
    text = remove_empty_html_tags(text)
    text = remove_double_astrix(text)
    return text


def remove_start_and_ending_new_lines(text):
    return re.sub(r'^[\r\n]+|[\r\n]+$', '', text)


def add_question_tags(text: str):
    return (f'<div class="accordian-item">'
            f'  <div class="accordian-trigger">'
            f'      <div class="accordion-question">{text}</div>'
            f'      <div class="accordian-cross">'
            f'          <div class="cross-h"></div>'
            f'          <div class="cross-h v" style="transform: translate3d(0px, 0px, 0px) scale3d(1, 1, 1) rotateX('
            f'0deg) rotateY(0deg) rotateZ(0deg) skew(0deg, 0deg); transform-style: preserve-3d;"></div>'
            f'      </div>'
            f'  </div>')


def add_response_tags(text: str):
    return (f'  <div class="accordian-content">'
            f'      <p>{text}</p>'
            f'  </div>'
            f'</div>')