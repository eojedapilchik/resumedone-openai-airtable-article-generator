prompts_cfg = {
    'url': {
        "French": "faire une combinaise gramaticallement correcte pour : ((title of card)). bien mettre les - "
                  "entre chaque mots suivre la structure des exemples suivants: "
                  "cv-d-acheteur-junior "
                  "cv-de-barista-starbucks "
                  "cv-de -plombier "
                  "cv-d-architecte "
                  "cv-d-acteur-de-serie ",
    },
    "translate": "translate the following text into English: ((title of card))",
    "transliterate": "transliterate the following text into the Latin alphabet: ((title of card))",
    "generate_skill": f"Generate a JSON object containing 10 hard skills, 10 technical skills, and 10 soft skills for the job title provided. Avoid including introductory text, conclusions, markdown formatting, or experience levels, and don't combine tools. "
                        f"Job title: [[job_name]]",
    "extract_bullet":   f"We are analyzing a resume from a candidate."
                        f"For the following work experience, he wrote the following information :"
                        f"Job Role : [[Job Role]]"
                        f"Name of the company : [[Name of the Company]]"
                        f"Experience content : [[Experience content]]"
                        f"We are trying to extract structured bullet points from this work experience content."
                        f"Generate a list of extracted	 bullet points. Do not make up any bullet point. Simply extract in a structured list exactly what is in the « Experience Content »"
                        f"If « Experience content » has no information, only return a single element in the list which is « [[Job Role]] at [[Name of the Company]] »"
                        f"If « Experience content » has no information and « company name » are both empty, only return a single element in the list which is « [[Job Role]] »"
                        f"Do not add any introductory sentence or any context. Just generate a JSON object without key, just array of the list. Do not add markdown formatting, spaces. The result must be ready to parse with a json parser.",
    "transformation_list":   f"We are trying to separate the different sentences or bullet points from the following text :"
                        f"For the following work experience, he wrote the following information :"
                        f"Text : [[List of Transformation selection]]"
                        f"Generate a list of extracted bullet points. Do not make up any bullet point. Simply extract in a structured list exactly what is in the « text »"
                        f"Do not add any introductory sentence or any context. Just generate a JSON object without key, just array of the list. Do not add markdown formatting, spaces. The result must be ready to parse with a json parser."
}
