import os
import json
import re
import time
from helpers.openai_handler import OpenAIHandler, OpenAIException
from helpers.airtable_handler import AirtableHandler

def process_content(text_to_translate, image_url, record_id, airtable_handler, selected_table_config, table_name):
    # list_of_languages = os.getenv("LIST_OF_LANGUAGES").split(", ")
    start_time = time.time()
    model_vision = os.getenv("OPENAI_VISION_MODEL", "gpt-4-vision-preview")
    openai_handler = OpenAIHandler(model_vision)

    fields_list = airtable_handler.get_table_schema(table_name).fields
    if not fields_list:
        print("No fields found in Content table")
        return

    language_list = extract_language_fields(fields_list)

    list_of_languages = [language['iso_code'] for language in language_list]
    max_in_batch = 32 if len(text_to_translate) > 400 else 8 if len(list_of_languages) > 32 else 4 if len(list_of_languages) > 16 else 2
    batch_size = len(list_of_languages) // max_in_batch
    batches = [list_of_languages[i:i + batch_size] for i in range(0, len(list_of_languages), batch_size)]

    is_error = False
    aggregated_data = {}
    for index, batch in enumerate(batches):
        print(f"Processing content batch {index}...{batch}")
        data, error = process_batch(batch, text_to_translate, image_url, openai_handler)
        if error:
            is_error = True
            aggregated_data.update(data)
            break  # Stop processing if error
        aggregated_data.update(data)
        # add a delay to avoid rate limiting
        time.sleep(5)

    elapsed_time = time.time() - start_time
    aggregated_data["elapsed_time"] = str(elapsed_time)
    update_airtable_record(record_id, aggregated_data, airtable_handler, is_error, language_list, selected_table_config)
    print(f"Elapsed time: {elapsed_time}")

def process_batch(batch, text_to_translate, image_url, openai_handler):

    message = prepare_message(text_to_translate, image_url, batch)
    retry_count = 3
    retry_delay = 5
    for i in range(retry_count):
        try:
            response = openai_handler.prompt_with_image_input(message, image_url)
            print(f"Batch response: {response}")
            data = process_openai_response(response)
            return data, False
        except OpenAIException as e:
            msg = f"Error in batch processing OpenAI (retry {i+1} of {retry_count}): {str(e)}\r\n batch: {batch}"
            print(msg)
            if i < retry_count - 1:
                time.sleep(retry_delay)
                continue
            else:
                break
    return {"error": msg}, True


def extract_language_fields(fields_list):
    language_pattern = re.compile(r'^([a-z]{2}(?:-[a-zA-Z]{2,4})?) - [A-Za-z ()]+$')
    return [
        {
            'iso_code': language_pattern.match(field.name).group(1),
            'field_id': field.id,
            'field_name': field.name
        }
        for field in fields_list
        if field.type in ('singleLineText','multilineText') and language_pattern.match(field.name)
    ]

def prepare_message(text_to_translate, image_url, list_of_languages):

    text_content = {
        "type": "text",
        "text": f"""
## 1. Input Details

**Text to translate:**
{text_to_translate}

**Target languages:**
{list_of_languages}

Add or remove languages from the target languages list as required.

Translate the provided text into every language specified in the list.

Use the exact language codes/keys provided in `{list_of_languages}` in the final JSON response. Do not rename, modify, or omit any language key.

**Reference screenshots:**

We will upload English screenshots only. There will be no existing target-language screenshots or translations to compare against.

Use the uploaded English screenshots to understand the page context, functionality, content structure, and intended user experience before translating.

---

## 2. Your Role

Act as an expert native-language localization specialist, professional translator, and regional content writer with deep knowledge of the target languages, local cultures, everyday communication patterns, and natural writing standards.

We are working on a professional resume-builder website.

Our goal is to provide users in every supported country with an authentic, native-language experience across the entire website, including:

- Landing pages
- Resume builders
- Checkout pages
- Subscription flows
- Dashboards
- Buttons and CTAs
- Notifications and error messages
- Instructions and descriptions
- Account pages
- Career-related content
- Other website UI elements

**Your task is NOT to produce literal, word-for-word, or generic machine-generated translations.**

Your task is to create natural, regionally appropriate content that sounds as though it was originally written by a professional native speaker of that language.

## 3. Understand the English Screenshots Before Translating

We will provide English screenshots only.

There will be:
- No existing target-language screenshots.
- No existing target-language translations for comparison.
- No reference translations to follow.

Before translating, carefully examine the provided English screenshots.

You must:

1. Understand the complete screenshot and surrounding content.
2. Understand the purpose of each page, section, button, heading, description, and message.
3. Identify the functionality and user journey behind the displayed content.
4. Understand what the user is expected to do on each screen.
5. Understand the context in which each sentence or phrase is being used.
6. Identify technical constants, placeholders, HTML elements, formatting elements, and identifiers that must remain unchanged.
7. Understand whether the content is an instruction, CTA, notification, heading, promotional message, or informational description.

**Important:** Understand the functionality and intention first. Start translating only after you understand what the content means and how it is used in the actual product.

Never translate isolated words without considering their context.

Do not guess the functionality if the screenshots do not provide sufficient context.

## 4. Native-Level Regional Localization (Highest Priority)

We do not want generic translations that sound machine-generated, awkward, unnatural, or different from how people actually communicate in the target language.

Every translation must follow the natural language standards of the target region.

Follow these requirements:

- Use authentic vocabulary commonly used by native speakers in the target country or region.
- Follow local grammar, sentence structure, spelling, punctuation, and writing conventions.
- Use expressions that local users naturally understand and recognize.
- Adapt sentence construction where necessary instead of translating English sentence structures directly.
- Maintain a natural, professional, friendly, and user-friendly tone.
- Use terminology commonly found on professional websites, resume builders, recruitment platforms, and career-related products in that region.
- Make instructions simple, clear, and easy for ordinary users to understand.
- Avoid uncommon vocabulary, unnatural expressions, overly formal language, and unnecessarily complicated sentences.
- Avoid literal translations that technically look correct but sound strange to native speakers.
- Maintain consistent terminology throughout the entire user journey.
- Consider regional differences in vocabulary, expressions, and language conventions.

### Native-speaker quality test

Before finalizing each translation, ask yourself:

"Would a native speaker from the target region naturally write this sentence on a professional resume-builder website?"

If the answer is no, improve it.

The final content should feel like locally written website content, not translated English content.

### Do not produce machine-like translations

- Do not translate English word by word.
- Do not blindly follow English sentence structure.
- Do not use awkward expressions just because they are grammatically possible.
- Do not use unnecessarily complicated vocabulary.
- Do not produce translations that sound like automated translation software.
- Do not mix regional language standards unnecessarily.
- Do not use expressions that are uncommon or unfamiliar to the target audience.

Prioritize natural communication and regional authenticity over literal translation.

## 5. Preserve HTML, Constants, Technical Elements & Formatting

This is extremely important.

Certain words and elements in our English content are intentionally kept in English because they are technical identifiers, placeholders, constants, HTML elements, or product-specific terms.

**Do not translate, modify, remove, rename, rearrange, or recreate these elements.**

Keep them exactly as they appear in the original English text.

### A. HTML tags and structures

Examples:

- `<b>`, `</b>`
- `<strong>`, `</strong>`
- `<p>`, `</p>`
- `<span>`, `</span>`
- `<div>`, `</div>`
- `<br>`
- `<a>`, `</a>`
- Any other HTML tags, attributes, classes, IDs, or HTML structures.

Preserve the complete HTML structure, including opening and closing tags.

Do not remove HTML tags or change their positions unnecessarily.

### B. Bold English text and intentionally highlighted words

Any English text intentionally displayed in bold must remain in English exactly as provided.

For example:

Original:

`Create your <b>CONTACT</b> section.`

Keep `CONTACT` exactly as it is.

Do not translate CONTACT.

This applies to ALL intentionally bold English text, not just CONTACT.

If the English content contains other bold words, technical labels, or product-specific terms, preserve them as well.

### C. Constants, placeholders, and technical identifiers

Examples:

- `DOMAIN_NAME`
- `USER_NAME`
- `EMAIL_ADDRESS`
- `CV_URL`
- `RESUME_ID`
- `{{{{user_name}}}}`
- `{{first_name}}`
- `%s`
- `${{price}}`
- `API_KEY`

These are examples only.

Identify and preserve all similar elements, including unfamiliar identifiers.

Never assume that an unfamiliar English word is translatable. First determine whether it is a technical constant, placeholder, or product-specific identifier.

### D. Special characters and formatting

Preserve all special characters and symbols exactly as they appear, including:

`()`, `{{}}`, `[]`, `>>`, `<<`, `/`, `//`, `\\`, `\\`, `.`, `*`, `^`, `%`, `$`, `#`, `@`, `!`, `~`, `:`, `;`, `=`, `+`, `-`, `_`, and similar symbols.

Do not remove, replace, rearrange, or introduce additional symbols.

**Important distinction:** Translate only the actual human-readable content. Never translate technical elements or intentionally preserved English text.

## 6. Maintain the Original Meaning and User Experience

- Never change the original meaning or functionality.
- Do not add information that does not exist in the English source.
- Do not remove important information.
- Do not invent additional descriptions or instructions.
- Maintain the same intent, tone, and purpose.
- Keep CTA buttons short, clear, and action-oriented.
- Make headings natural and suitable for the target language.
- Adapt sentence length where necessary for natural localization without changing the meaning.
- Ensure translated content is suitable for the actual UI context.

The goal is to make the experience feel native while keeping the original product functionality intact.

## 7. Consistency Across All Pages

We may provide multiple screenshots from different sections of the same website.

You must maintain consistent translations for:

- Navigation labels.
- Buttons and CTAs.
- Resume-related terminology.
- Subscription and payment terminology.
- Account and dashboard terminology.
- Career and recruitment terminology.
- Error messages and notifications.
- Instructions and descriptions.

If a specific term has already been translated, use the same terminology wherever the context is identical.

Do not randomly change terminology between pages.

If the context changes, use the most natural translation for that particular context while maintaining terminology consistency.

## 8. Final Quality Checks Before Responding

Before generating the final output, verify:

1. Does the translation sound natural to native speakers?
2. Does it follow the target region's language conventions?
3. Does it avoid literal or awkward machine-generated expressions?
4. Is the original meaning preserved?
5. Is the tone appropriate for a professional resume-builder website?
6. Are all HTML tags and structures unchanged?
7. Are all intentionally bold English words unchanged?
8. Are all constants, placeholders, variables, and technical identifiers unchanged?
9. Are all special characters preserved?
10. Is the translation consistent with the surrounding UI context?
11. Is the content ready to be copied directly into our website?
12. Have all requested languages been translated?
13. Is the JSON valid and correctly formatted?

If any translation sounds unnatural, revise it before responding.

## 9. Required Output Format â€“ JSON Only

Return the final translations in valid JSON format.

Use exactly the same language keys provided in `{list_of_languages}`.

### Example input

Text:

`Create your <b>CONTACT</b> section using DOMAIN_NAME.`

Languages:

`{{"de": "German", "fr": "French", "pt-BR": "Brazilian Portuguese"}}`

### Example output structure

{{
  "de": "Translated German content with <b>CONTACT</b> and DOMAIN_NAME preserved.",
  "fr": "Translated French content with <b>CONTACT</b> and DOMAIN_NAME preserved.",
  "pt-BR": "Translated Brazilian Portuguese content with <b>CONTACT</b> and DOMAIN_NAME preserved."
}}

The example illustrates the preservation of technical elements only. Actual human-readable content must be translated into the requested languages.

### Strict Output Rules

- Return valid JSON only.
- Use exactly the requested language keys.
- Do not include Markdown code fences.
- Do not include explanations, notes, or comments.
- Do not include the original English text unless it is part of a requested output value.
- Do not add extra keys.
- Ensure all JSON strings are correctly escaped.
- Do not omit any requested language.
- Do not include any text before or after the JSON response.

---

## 10. Our Main Objective

We are not looking for translations that simply convert English words into another language.

We want **high-quality regional localization that delivers a genuine native-speaking experience.**

Every user visiting our resume-builder website should feel that the website was originally created for their language and region.

### Priority order

1. Native-level regional language quality.
2. Natural and user-friendly expressions.
3. Correct understanding of website functionality and context.
4. Consistent terminology across the product.
5. Exact preservation of HTML, bold English text, constants, placeholders, and technical elements.
6. Accurate original meaning and functionality.
7. Valid JSON output.

**Always understand first, localize naturally second, validate everything third, and return JSON only.**

Your final translations must be ready for direct implementation on our live website."""
    } if image_url else {
        "type": "text",
        "text": f"""
      ## 1. Input Details

**Text to translate:**
{text_to_translate}

**Target languages:**
{list_of_languages}

Translate the provided text into every language specified in the list.

Use the exact language codes/keys provided in `{list_of_languages}` in the final JSON response. Do not rename, modify, or omit any language key.

**No screenshots or additional context will be provided.**

Work exclusively from the source text and the product context established in this prompt: a professional resume-builder website. Do not request screenshots or additional information.

---

## 2. Your Role

Act as an expert native-language localization specialist, professional translator, and regional content writer with deep knowledge of the target languages, local cultures, everyday communication patterns, and natural writing standards.

We are working on a professional resume-builder website. Content may include:

- Landing pages
- Resume builders
- Checkout pages and subscription flows
- Dashboards and account pages
- Buttons and CTAs
- Notifications and error messages
- Instructions and descriptions
- Career-related content
- Other website UI elements

Create natural, regionally appropriate content that sounds as though it was originally written by a professional native speaker.

Avoid literal, word-for-word translations when they sound unnatural or fail to communicate the intended meaning.

## 3. Understand the Source Text Without Screenshots

Before translating:

1. Read the complete source text.
2. Use neighboring strings, headings, labels, and descriptions, if present, to understand how the content is used.
3. Identify whether each item is a heading, CTA, field label, instruction, notification, error message, promotional message, or informational description where the text supports that interpretation.
4. Identify all technical constants, placeholders, HTML elements, formatting, and identifiers that must remain unchanged.
5. Determine the intended meaning using the source text and the resume-builder product context.

### Handling ambiguity

- Do not invent page layouts, button positions, visual states, user actions, or product capabilities.
- Do not assume character limits or available screen space.
- Keep short UI strings concise without sacrificing clarity.
- Prefer wording that preserves the original ambiguity when practical.
- Do not introduce a more specific meaning than the source supports.
- When a choice is unavoidable, use the interpretation best supported by the text and the resume-builder context, with the fewest additional assumptions.
- Do not ask clarification questions or include ambiguity notes in the output.

## 4. Native-Level Regional Localization

Every translation must follow the natural language standards of the target region.

- Use authentic vocabulary commonly used by native speakers.
- Follow local grammar, sentence structure, spelling, and writing conventions, subject to the preservation rules below.
- Adapt English sentence construction where necessary.
- Maintain a natural, professional, friendly tone.
- Use terminology familiar from local resume builders, recruitment platforms, and career-related websites.
- Keep instructions simple and easy to understand.
- Avoid uncommon vocabulary, excessive formality, and unnecessarily complicated sentences.
- Maintain consistent terminology and forms of address.
- Respect regional differences identified by the requested language or locale.

If a language key does not specify a region, use broadly understood standard language and avoid unnecessarily region-specific expressions. Do not change the language key.

### Native-speaker quality test

Before finalizing each translation, ask:

“Would a native speaker naturally write this on a professional resume-builder website?”

If the answer is no, revise it.

Prioritize natural communication while preserving the source meaning and all protected elements.

## 5. Preserve HTML, English Labels, Technical Elements, and Formatting

Translate human-readable content only, except for English text explicitly protected below.

### A. HTML tags and structure

Preserve all HTML tags, attributes, classes, IDs, nesting, and tag order exactly as provided.

Examples:

- `<b>`, `</b>`
- `<strong>`, `</strong>`
- `<p>`, `</p>`
- `<span>`, `</span>`
- `<div>`, `</div>`
- `<br>`
- `<a>`, `</a>`

Do not add, remove, rename, or rewrite tags or attributes.

Translate eligible text inside HTML elements while preserving the markup.

### B. Bold English text

Any English text intentionally displayed in bold must remain in English exactly as provided.

This includes text inside `<b>...</b>` or `<strong>...</strong>`, and text marked as bold using Markdown.

For example:

`Create your <b>CONTACT</b> section.`

Keep `<b>CONTACT</b>` unchanged and translate only the surrounding text.

Apply this rule even when the bold English text is an ordinary word rather than a technical identifier.

### C. Constants, placeholders, and technical identifiers

Preserve all constants, variables, placeholders, and technical identifiers exactly.

Examples:

- `DOMAIN_NAME`
- `USER_NAME`
- `EMAIL_ADDRESS`
- `CV_URL`
- `RESUME_ID`
- `{{{{user_name}}}}`
- `{{first_name}}`
- `%s`
- `${{price}}`
- `API_KEY`

These are examples only. Preserve unfamiliar identifiers that follow similar patterns.

Do not translate, rename, change capitalization, alter internal spacing, duplicate, omit, or reorder protected elements.

Preserve URLs, email addresses, file paths, and code fragments exactly.

An ordinary English word is not automatically a technical identifier. Use its syntax and source-text context to distinguish technical content from translatable text.

### D. Special characters and formatting

Preserve the source’s special characters, symbols, line breaks, and formatting, including:

`()`, `{{}}`, `[]`, `>>`, `<<`, `/`, `//`, `\`, `\\`, `.`, `*`, `^`, `%`, `$`, `#`, `@`, `!`, `~`, `:`, `;`, `=`, `+`, `-`, `_`

Do not add, remove, replace, or rearrange these symbols within the translated content.

These exact-preservation requirements take precedence over local punctuation preferences.

Apply the JSON escaping required to represent the preserved content correctly. For example, a literal backslash must be escaped in a JSON string.

## 6. Maintain Meaning and Intended Use

- Preserve the original meaning, intent, tone, and functionality.
- Do not add information absent from the source.
- Do not remove important information.
- Do not invent descriptions, instructions, benefits, or claims.
- Keep CTA buttons short, clear, and action-oriented.
- Make headings natural in the target language.
- Adapt sentence length and structure where needed without changing meaning.
- Do not claim that a translation fits a specific layout or has been visually validated.

## 7. Maintain Consistency

When multiple strings or sections are provided, treat them as content from the same product.

Use consistent terminology for:

- Navigation labels
- Buttons and CTAs
- Resume sections and resume-building actions
- Subscriptions and payments
- Accounts and dashboards
- Career and recruitment concepts
- Errors, notifications, and instructions

Use the same translation for the same concept when the context is identical. When the meaning changes, choose the appropriate translation for that context.

## 8. Final Quality Checks

Before responding, verify that:

1. Every requested language is included.
2. Every language key matches the input exactly.
3. The wording sounds natural to native speakers.
4. Regional language conventions are respected.
5. The original meaning and intent are preserved.
6. No unsupported context or functionality has been invented.
7. Terminology and tone are consistent.
8. HTML tags, attributes, and structure are unchanged.
9. Protected bold English text is unchanged.
10. Constants, placeholders, variables, and identifiers are unchanged.
11. Special characters and formatting are preserved.
12. The output is valid JSON with correctly escaped strings.

Revise any translation that fails these checks.

## 9. Required Output Format — JSON Only

Return one valid JSON object, with exactly one key for each requested language. Each value must be the translated text.

### Example input

Text:

`Create your <b>CONTACT</b> section using DOMAIN_NAME.`

Languages:

`{{"de": "German", "fr": "French", "pt-BR": "Brazilian Portuguese"}}`

### Example output

{{
  "de": "Erstellen Sie Ihren Abschnitt <b>CONTACT</b> mit DOMAIN_NAME.",
  "fr": "Créez votre rubrique <b>CONTACT</b> avec DOMAIN_NAME.",
  "pt-BR": "Crie sua seção <b>CONTACT</b> usando DOMAIN_NAME."
}}

### Strict output rules

- Return valid JSON only.
- Use exactly the requested language keys.
- Do not include Markdown code fences.
- Do not include explanations, notes, comments, or confidence scores.
- Do not add extra keys.
- Do not omit any requested language.
- Do not include the original English text except for protected content or a requested English translation.
- Escape all JSON strings correctly.
- Do not include any text before or after the JSON object.

## 10. Main Objective

Deliver high-quality regional localization that feels native to users of a professional resume-builder website.

Work from the source text alone, interpreted within this product context. Preserve all protected content exactly.

**Understand the text, localize naturally, validate every requirement, and return JSON only.**"""
    }
    content = [text_content]
    if image_url:
        content.append({"type": "image_url", "image_url": {"url": image_url}})
    return [{"role": "user", "content": content}]

def process_openai_response(response):
    match = re.search(r'{.*}', response, re.DOTALL)
    if match:
        response = match.group(0)
        data = json.loads(response)
        return data
    else:
        msg = f"Error converting text to json:\r\n {response}"
        print(msg)
        return {"error": msg}


def process_content_missing(text_to_translate, image_url, record_id, record_fields, airtable_handler, selected_table_config, table_name):
    start_time = time.time()
    if image_url:
        model = os.getenv("OPENAI_VISION_MODEL", "gpt-4-vision-preview")
    else:
        model = os.getenv("OPENAI_ENGINE", "gpt-3.5-turbo")
    openai_handler = OpenAIHandler(model)

    fields_list = airtable_handler.get_table_schema(table_name).fields
    if not fields_list:
        print("No fields found in Content table")
        return

    language_list = extract_language_fields(fields_list)

    # Filter to only languages with blank/missing field values
    missing_languages = [
        lang for lang in language_list
        if not record_fields.get(lang['field_name']) and not record_fields.get(lang['field_id'])
    ]

    if not missing_languages:
        print("No missing translations found, nothing to do.")
        return

    list_of_iso = [lang['iso_code'] for lang in missing_languages]
    max_in_batch = 32 if len(text_to_translate) > 400 else 8 if len(list_of_iso) > 32 else 4 if len(list_of_iso) > 16 else 2
    batch_size = max(1, len(list_of_iso) // max_in_batch)
    batches = [list_of_iso[i:i + batch_size] for i in range(0, len(list_of_iso), batch_size)]

    is_error = False
    aggregated_data = {}
    for index, batch in enumerate(batches):
        print(f"Processing missing content batch {index}...{batch}")
        data, error = process_batch(batch, text_to_translate, image_url, openai_handler)
        if error:
            is_error = True
            aggregated_data.update(data)
            break
        aggregated_data.update(data)
        time.sleep(5)

    elapsed_time = time.time() - start_time
    aggregated_data["elapsed_time"] = str(elapsed_time)
    update_airtable_record(record_id, aggregated_data, airtable_handler, is_error, missing_languages, selected_table_config)
    print(f"Elapsed time: {elapsed_time}")


def update_airtable_record(record_id: str, data: dict, airtable_handler: AirtableHandler, is_error: bool = False,
                           language_list=None, selected_table_config: dict = None):
    if language_list is None:
        language_list = []
    fields = {}
    if is_error:
        fields[selected_table_config.get('error_log_fld')]= str(data.get("error"))
    for language in language_list:
        iso_code = language['iso_code']
        field_id = language['field_id']
        fields[field_id] = data.get(iso_code, "")
    fields[selected_table_config.get("elapsed_time_fld")] = data.get("elapsed_time", "")
    airtable_handler.update_record(record_id, fields)

