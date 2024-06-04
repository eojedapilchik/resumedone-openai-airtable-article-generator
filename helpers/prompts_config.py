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
                        f"Do not add any introductory sentence or any context. Just generate a JSON object without key, just array of the list. Do not add markdown formatting, spaces. The result must be ready to parse with a json parser.",
    "outcome_question" :"""> Below is a part of a masterclass about the way to make great bullet points in a resume by showing \"symbols of achievements\".

We are trying to apply those specifications to help candidates make better resumes. At some point in our method, we have interviewed the candidate and know the list of their work experiences and for each experience, we have gathered a list of raw bullet points. We need a list of questions to ask them to help us qualify and quantify their “outcome” (and the “outcome” only).  as described in the transcript (”For outcome quantification, you can write, managed seven cross-functional teams to deploy email security systems across 1,500 enterprise clients. Also impressive. Here, 1,500 enterprise clients is a direct outcome of your effort.
It shows scope. Outcomes are direct causations, usually at a project or team level. And usually they are one-to-one or one-to-a-few ratio.
You did X with a few teams and Y happened. And that Y is a direct outcome that you can easily quantify. For impact quantification, you can write, reduced credit card theft by 12% by deploying email security systems across 1,500 enterprise clients.”). Using the masterclass transcript, could you provide a list of question to ask them to help us quatify the outcome (not the “effort”, not the “impact”, only the outcome). Use the transcript as a basis but do not hesitate to provide questions regarding generic KPIs across all industries and functions (if those are not specified) that will help us extract the right info from the candidate.

In this case here is our specific Bullet point context. Adapt the questions to those elements : 
Job Role : [[job_role]]
Bullet Point name : [[bullet_point_name]]

Provide, for each question, some guidance, information and examples in italic, filled with examples and as many inspiration as possible to help the user remind the content of their work experience. This guidance paragraph must be at least 4 sentences long.

5 questions exactly.
> 
> 
> No introductory sentence. No conclusion sentence. Line break between each question
> Your questions must be oriented so that they highlight achievements that will impress potential recruiters in their field the most.
> 
> Each question must be independant from previous questions answers.
> 
> Write your answer in perfect [[language]]
> 
> Masterclass transcript : “And that's our first principle. Add symbols of achievements in your documents to excite the decision maker and grab their attention. These symbols are numbers with dollar signs, percentage signs, and metrics that are known in your industry.
> 
> In this module, we will answer the most important question. How do you quantify these numbers? And then we will learn how to transform basic bullet points into achievement bullet points with Joe, and then finally discuss three reasons why this principle is so effective in winning over the corporate decision makers. So the question is, why do so many candidates not include these symbols of achievements, these numbers in their bullet points? In my 10 years of career mentorship, I've learned that there are three challenges that stop candidates from putting numbers on their resume, performance reviews, or other documents that they use to market themselves.
> 
> Challenge number one. They assume that only big achievements need to be quantified. That's not true.
> 
> You can quantify a lot of things to show symbols of achievements. Challenge number two. They don't know how to quantify because they assume that the numbers have to be perfectly accurate.
> 
> That's not true either. Nobody's checking your math. Your numbers just have to be believable and of course not made up.
> 
> Number three. They assume that only the projects they led are considered their achievements, which is a big mistake. Let's discuss how to overcome each of these three challenges.
> 
> Challenge number one. Candidates assume only big achievements should be quantified. That's not true.
> 
> We just discussed that. There are three things that you can quantify. The effort, the outcome, and the impact.
> 
> Impact is the hard one that we will discuss in detail, but for now, understand that effort and direct outcomes are easy to quantify and also show a lot of value. For effort quantification, you can write, managed seven cross-functional teams to complete email security projects three months ahead of schedule. Here we used seven cross-functional teams and three months ahead of schedule as symbols of achievements, even though they are efforts, but they look impressive.
> 
> Quantifying effort is easy because you're directly connected to it. You can estimate it fairly accurately. You can use hours, cycles, instances, cross-functional work, time saved, et cetera, to show effort.
> 
> For outcome quantification, you can write, managed seven cross-functional teams to deploy email security systems across 1,500 enterprise clients. Also impressive. Here, 1,500 enterprise clients is a direct outcome of your effort.
> 
> It shows scope. Outcomes are direct causations, usually at a project or team level. And usually they are one-to-one or one-to-a-few ratio.
> 
> You did X with a few teams and Y happened. And that Y is a direct outcome that you can easily quantify. For impact quantification, you can write, reduced credit card theft by 12% by deploying email security systems across 1,500 enterprise clients.
> 
> Impact usually has a financial element or company level metric or KPI impact that they can make the strongest impression on decision makers. Impacts are correlations. You were one of the input in the bigger impact, but sometimes it's not always clear because there are several other projects that are also contributing to that impact.
> 
> That's where the confusion happens. So here is a master tip. If you don't know what your impact is, ask yourself, what would not have happened inside the team or the company if I didn't do my work? That's something that would not have happened.
> 
> That's your impact. Because you did your work, that impact happened. It's pretty simple.
> 
> So you claim that impact. I'll share more on this in a few minutes when we discuss challenge number three. Challenge number two.
> 
> Candidates assume you need to quantify perfectly accurate numbers. That's not true. You don't have to calculate at all.
> 
> What you have to do is borrow numbers from data teams, press releases, company LinkedIn announcements, project dashboards, or internal emails from leadership that discuss overall company numbers or specific project launches that you were involved in. And if none of these work, look at your manager's or your co-workers or your department leader's LinkedIn profile. Usually they have some numbers that are directly applicable to your work and you can put those numbers in your bullet points.
> 
> And if none of these work, you can do an estimate. Estimations need to be plausible, believable, not 100% accurate so you can relax. Nobody has time to check the math.
> 
> The estimate method that I like to use is the estimate and dispute method. So first, you estimate a number through whatever method you want, top-down, bottom-up, workflow method, some equations that are known in the industry, et cetera. You can figure that out.
> 
> But what you do is you try to dispute it afterwards with industry data or some other logic or data source. And you're not simply trying to verify it, you're trying to dispute it. That intention changes your research approach and it's what a decision maker may do if your numbers seem way off.
> 
> So if the dispute doesn't nullify the original estimation that you made, you can include it in your bullet points. For example, let's say that you estimated that your work helped convert 5% of visitors into customers on your online store. So now, you dispute it by looking at data from the industry.
> 
> And you find, surely enough, most online stores have a 3% to 6% checkout rate. Cool, your estimate is fine. But if you realize that the industry checkout rate is 1% and you are at 5%, then maybe your estimation isn't correct.
> 
> So you can remove it, re-estimate it, or explain your estimation. Because it's possible that you are doing a much better job than the industry and you should explain that by writing. For example, improved checkout rate to 5% by utilizing XYZ methods to convert online visitors into customers.
> 
> That XYZ method will satisfy a decision maker who would have otherwise been skeptical that there's no way you're achieving this number. So that's enough for estimation. We can do an entire masterclass on just estimation, but it's not worth it.
> 
> All the tips that I've given you earlier are faster and more effective. Challenge number three. Candidates assume that only the projects they led are considered their achievements.
> 
> That's a massive mistake and it happens over and over again. I want you to avoid that mistake. Achievements are a team game.
> 
> You should take credit for them, even if you're not leading the project. No one accomplishes anything alone inside a company. It's always a team effort and therefore every team member deserves to take credit for that bigger impact.
> 
> Just look at all the things that CEOs take credit for. Are they hands-on for all those projects? No. Are they leading all those projects? No.
> 
> But they did some work in the background, or some might argue they did not do any work at all, but usually they did some work that enabled the teams to make that impact and they claim credit for it. You should do the same. For example, if you designed an ad creative, like a video or a story ad for a TikTok ad campaign, and that campaign drove $1 million in revenue, you should claim that by saying, designed advertising assets to assist marketing in generating $1 million in revenue per month.
> 
> That's very impressive. You can use terms like assist, contribute, co-managed, et cetera, to claim the larger impact because your team's achievement is your achievement. Your cross-functional project results are your results.
> 
> Everything that you do individually has a ripple effect inside the company and you are responsible for that impact, so you should claim it. And as I mentioned earlier, and I will mention it again because it is so important, ask yourself, what would not have happened inside the team or the company if I didn't do my work? That's something that would not have happened. That's your impact and you should claim it.
> 
> All right, let's look at some other examples with Joe to help you understand how to transform basic bullet points into achievement bullet points that make you stand out.
> 
> Thanks Adil. Hello everyone, Jo here. Very excited you're all here with us taking this masterclass.
> 
> You'll see me or an avatar version of me popping up throughout the masterclass to share examples that are based on MBH's team's 15 years of experience as hiring managers, people managers, and senior leaders in some of the most prestigious companies in the world. So let's get started. I'm going to transform two bullet points for you and then share five smaller examples to give you an even better understanding of how symbols of achievements can be integrated into your resume, LinkedIn profile, or performance reviews.
> 
> Or really, any other document you create to market yourself. And don't worry about writing them all out. We have all of these in the appendix for you to refer to whenever you want.
> 
> So let's kick it off with our first example. Instead of writing, responsible for running social media campaigns for retail stores in Texas, try writing, managed a marketing budget of $6 million per year on social media campaigns to increase retail sales in Texas by 15% year over year. You can elevate this even further by writing, managed a marketing budget of $6 million per year on social media campaigns to increase retail sales in Texas by 15% year over year, and decrease cost per acquisition by 10%.
> 
> As a hiring manager, seeing $6 million and 15% year over year is an instant credibility enhancer for me and definitely makes you stand out as a person I'd like to recruit, hire, or if you're in my team, promote. And I love the mention of the two industry metrics. Mentioning sales and cost per acquisition creates a very strong impression that you have a very deep understanding of how your work impacts the greater business and that you have the capacity to measure it.
> 
> Let's move on to our second example. Instead of writing, responsible for managing MBA-ish's sales and marketing teams to generate sales across three different revenue streams, write, generated $100 million in revenue for MBA-ish by leading sales and marketing teams to diversify master class revenue into consumer, private, and public sectors, or you can elevate this further by saying, led the sales and marketing teams to generate $100 million in revenue, representing 85% of MBA-ish's total revenue in 2022. As an aside, this isn't a real number.
> 
> Our actual revenue last year was much less impressive. What I do find impressive though is in this example, you can add your impact and then quantify it as a percentage of overall business impact. That's huge.
> 
> Showing that you helped drive a percent of revenue is far more impactful in my opinion than just generated X revenue amount because the percentage reflects the size of the impact that you had in the overall business. I understand you might not always have this information available, so you can try some of the estimate and impact methods that Adeel has shared earlier in the module. Let's go through some more examples of symbols of achievement that span different industries and career stages.
> 
> Achieved $2 million in savings by migrating to an in-house billing system. Delivered 10 memes per week that were read by 2 million readers on Instagram. Acquired five Fortune 100 clients representing $20 million in revenue annually.
> 
> Improved team productivity by 35% as measured by hours saved while simultaneously reducing OPEX by 15%. Increased lifetime value by 17% and reduced churn by 25% month over month. Month over month, year over year, you'll see those represented as MOM or YOY is crucial to mention if you have that level of data to once again reflect that impact.
> 
> We'll talk a little bit more about that in the second principle. That's it for now. I'll see you again with more examples for the second principle.
> 
> Thanks Joe. So you can see from these examples how much fun a bullet point can be. It's not fun.
> 
> It's boring. But you can see, symbols of achievements make your bullet points very impressive. Let me share three reasons why adding symbols of achievements is the most important principle in winning over a decision maker.
> 
> Number one, your resume, performance reviews, promotion cases or LinkedIn profiles are not a role description document. They are an achievements document with secondary details about your role, outcomes, and effort. That's what the decision makers are looking for, achievements.
> 
> Focus is not on role phrases such as responsible for managing XYZ or performed ABC activities. Instead, the focus is on increased revenue by X, decreased churn rate by Y percent, year over year, and so on and so forth. Putting these symbols of achievements converts your document into an achievements document and signals to the decision maker that you are a high performer.
> 
> Number two, these symbols of achievements help you stand out visually and strategically. Visually, these symbols stand out because they are numbers among a lot of words in your document. And that's a huge advantage because the decision makers or the decision maker's decision maker will skim your document for less than 30 seconds and these symbols of achievements will stand out and convince them to take an interest in you.
> 
> Strategically, these symbols stand out because 75% of other candidates are not adding numbers or not using it enough in their resume according to cultivated cultures research. And in my experience, this holds true across LinkedIn profiles, performance reviews, and other documents. Candidates are simply not putting in these symbols of achievements.
> 
> So when you add them throughout your document, you're standing out strategically against all the other candidates as someone who's achieved more than others. And see, these symbols of achievements represent objective results. Numbers make things feel real.
> 
> There's no synergy or I'm a proven leader or some other subjective claims filled with jargon words that nobody can understand. They're pure numbers that decision makers understand because those numbers are their reality in their business as well. Okay, last tip.
> 
> How often should you add these numbers? My rule of thumb is about 20 to 30 numbers on one page or numbers in every other bullet point, assuming that each bullet point is 15 to 30 words long. This ratio fills out the document nicely and makes you come across as a superb communicator who knows how to write a very effective business document. Alright, take a five-minute break before you start the next module.
> 
> You've taken in a lot of info right now. A little break will help you get ready for the next session. See you in five minutes.”
> 
> To help you define outcomes, here is a list of strategic objectives. Select the most relevant to the user’s specific bullet point context above : 
> 
> - **OBJECTIFS COMMERCIAUX SUPÉRIEURS UNIVERSELS**
>     
>     **Augmenter / améliorer / maximiser / croître / accélérer / générer / construire**
>     
>     **Objectifs de Métriques :**
>     
>     - [ ]  Augmenter la part de marché
>     - [ ]  Maximiser le revenu, la rentabilité
>     - [ ]  Améliorer la satisfaction client, la fidélité client
>     - [ ]  Innover pour le positionnement sur le marché
>     - [ ]  Développer le développement des employés, la satisfaction des employés, le moral des employés, la rétention des employés
>     - [ ]  Générer des rendements pour les actionnaires, des bénéfices par action, des dividendes
>     - [ ]  Optimiser l’efficacité opérationnelle
>     - [ ]  Améliorer la gestion de la qualité
>     - [ ]  Augmenter la responsabilité sociale
>     - [ ]  Croître et diversifier les activités
>     
>     **Diminuer / réduire / minimiser :**
>     
>     **Objectifs de Coût :**
>     
>     - [ ]  Réduire le risque
>     - [ ]  Minimiser les coûts
>     - [ ]  Réduire les menaces concurrentielles
>     - [ ]  Minimiser la dette
>     
> - **OBJECTIFS SUPÉRIEURS DE GESTION FINANCIÈRE**
>     
>     **Augmenter / améliorer / maximiser / croître / accélérer / générer / construire**
>     
>     **Objectifs de Métriques :**
>     
>     - [ ]  Augmenter le revenu top line, EBITDA, marges bénéficiaires, profit
>     - [ ]  Améliorer le P&L, bilan, compte de résultat, flux de trésorerie
>     - [ ]  Optimiser les principales métriques et ratios financiers pour améliorer la rentabilité dans votre secteur
>     
>     **Objectifs de Systèmes :**
>     
>     - [ ]  Optimiser la gouvernance d’entreprise, les contrôles internes
>     - [ ]  Évaluer les investissements, ROI, allocation budgétaire
>     - [ ]  Améliorer la stratégie opérationnelle, les prévisions
>     - [ ]  Optimiser la planification fiscale, les audits, la gestion de portefeuille
>     
>     **Objectifs de Ressources :**
>     
>     - [ ]  Accélérer les introductions en bourse (IPO), financement par dette, financement par actions, financement alternatif
>     - [ ]  Maximiser les budgets, CAPEX, OPEX, ROI
>     - [ ]  Améliorer la gestion de la performance
>     - [ ]  Développer les effectifs
>     
>     **Objectifs d’Avantage Concurrentiel :**
>     
>     - [ ]  Optimiser les fusions et acquisitions, la structure des transactions, la diligence raisonnable
>     - [ ]  Augmenter les actifs / actifs sous gestion
>     - [ ]  Améliorer les relations avec les investisseurs
>     
>     **Diminuer / réduire / minimiser :**
>     
>     **Objectifs de Coût :**
>     
>     - [ ]  Réduire le coût des biens vendus (COGS)
>     - [ ]  Réduire le coût du capital, les coûts opérationnels, la structure de coûts
>     - [ ]  Minimiser les coûts généraux
>     - [ ]  Réduire la dette
>     
>     **Objectifs de Risque :**
>     
>     - [ ]  Réduire les risques macroéconomiques
>     - [ ]  Minimiser les comptes débiteurs
>     - [ ]  Réduire les inefficacités opérationnelles
>     - [ ]  Optimiser les principales métriques de réduction des risques dans votre secteur
>     
> - **OBJECTIFS SUPÉRIEURS DE GESTION CLIENT**
>     
>     **Augmenter / améliorer / maximiser / croître / accélérer / générer / construire**
>     
>     **Objectifs de Métriques :**
>     
>     - [ ]  Augmenter la satisfaction client (CSAT, NPS)
>     - [ ]  Maximiser le revenu moyen par utilisateur (ARPU)
>     - [ ]  Améliorer la marge par utilisateur, la valeur moyenne des commandes (AOV)
>     - [ ]  Générer la valeur à vie du client
>     - [ ]  Accélérer le taux de conversion, le taux de retour des clients, le taux de retour
>     - [ ]  Augmenter le temps de présence
>     - [ ]  Croître le nombre d’utilisateurs actifs
>     - [ ]  Maximiser les taux de vente incitative/croisée
>     - [ ]  Améliorer les principales métriques et ratios clients/utilisateurs pour améliorer l’expérience client dans votre secteur
>     
>     **Objectifs de Systèmes :**
>     
>     - [ ]  Construire des parcours d’intégration
>     - [ ]  Générer des campagnes d’engagement
>     - [ ]  Maximiser le processus de rétention
>     - [ ]  Améliorer le service client
>     - [ ]  Innover avec le design thinking
>     
>     **Objectifs de Ressources :**
>     
>     - [ ]  Développer les équipes de service client
>     - [ ]  Augmenter les équipes d’acquisition clients/marketing
>     - [ ]  Améliorer les équipes produit
>     
>     **Objectifs d’Avantage Concurrentiel :**
>     
>     - [ ]  Maximiser la fidélité client
>     - [ ]  Générer des avis positifs des clients
>     - [ ]  Améliorer le sentiment des clients
>     - [ ]  Croître le bouche-à-oreille, les recommandations
>     - [ ]  Améliorer l’expérience utilisateur
>     
>     **Diminuer / réduire / minimiser :**
>     
>     **Objectifs de Coût :**
>     
>     - [ ]  Réduire le coût par utilisateur/CAC (coût d’acquisition client)
>     - [ ]  Minimiser le taux d’abandon de panier
>     - [ ]  Réduire le taux de rebond
>     
>     **Objectifs de Risque :**
>     
>     - [ ]  Réduire le taux de désabonnement
>     - [ ]  Minimiser les avis négatifs des clients
>     - [ ]  Réduire le temps de résolution
>     - [ ]  Améliorer les principales métriques et ratios financiers pour améliorer la rentabilité dans votre secteur
> - **OBJECTIFS SUPÉRIEURS DE GESTION STRATÉGIQUE**
>     
>     **Augmenter / améliorer / maximiser / croître / accélérer / générer / construire**
>     
>     **Objectifs de Métriques :**
>     
>     - [ ]  Augmenter le revenu top line, EBITDA, marges bénéficiaires, profit, prix
>     - [ ]  Maximiser le revenu mensuel récurrent (MRR), le revenu annuel récurrent (ARR)
>     
>     **Objectifs de Systèmes :**
>     
>     - [ ]  Améliorer la planification stratégique
>     - [ ]  Optimiser la chaîne de valeur
>     - [ ]  Améliorer la chaîne d’approvisionnement
>     - [ ]  Optimiser la stratégie d’entreprise, l’évaluation des investissements
>     - [ ]  Maximiser l’allocation budgétaire
>     - [ ]  Articuler la vision
>     - [ ]  Améliorer la recherche de marché
>     - [ ]  Évaluer les opportunités
>     - [ ]  Analyser les risques
>     - [ ]  Segmenter le marché
>     - [ ]  Développer de nouvelles affaires
>     - [ ]  Élargir les activités
>     
>     **Objectifs de Ressources :**
>     
>     - [ ]  Accélérer la R&D (Recherche & Développement)
>     - [ ]  Développer des partenariats
>     - [ ]  Établir des alliances stratégiques
>     - [ ]  Créer des coentreprises
>     
>     **Objectifs d’Avantage Concurrentiel :**
>     
>     - [ ]  Augmenter la part de marché
>     - [ ]  Optimiser le positionnement sur le marché, le positionnement des produits
>     - [ ]  Maximiser le mix de produits
>     - [ ]  Réduire le temps de mise sur le marché
>     - [ ]  Augmenter le marché total adressable (TAM)
>     - [ ]  Améliorer le modèle d’affaires
>     - [ ]  Développer des services pionniers dans l’industrie
>     - [ ]  Diversifier
>     - [ ]  Innover
>     - [ ]  Optimiser la distribution
>     
>     **Diminuer / réduire / minimiser**
>     
>     **Objectifs de Coût :**
>     
>     - [ ]  Réduire les effectifs
>     - [ ]  Réduire les unités commerciales
>     - [ ]  Minimiser les projets en dehors des compétences de base
>     - [ ]  Réduire l’allocation inefficace du budget
>     
>     **Objectifs de Risque :**
>     
>     - [ ]  Réduire les menaces de la chaîne de valeur
>     - [ ]  Minimiser les menaces concurrentielles, les menaces de nouveaux entrants, les perturbations
>     - [ ]  Réduire la confusion de la marque
>     - [ ]  Minimiser les faiblesses concurrentielles
>     - [ ]  Réduire l’écart d’offre de services entre les concurrents
>     - [ ]  Améliorer les systèmes, processus et ressources organisationnels défaillants
> - **OBJECTIFS SUPÉRIEURS DE GESTION DES PERSONNES**
>     
>     **Augmenter / améliorer / maximiser / croître / accélérer / générer / construire**
>     
>     **Objectifs de Métriques :**
>     
>     - [ ]  Améliorer la satisfaction des employés
>     - [ ]  Responsabiliser les employés
>     - [ ]  Maximiser le moral des employés
>     - [ ]  Augmenter l’engagement des employés
>     
>     **Objectifs de Systèmes :**
>     
>     - [ ]  Construire une culture de haute performance
>     - [ ]  Définir les rôles pour les individus, les équipes et les départements
>     - [ ]  Développer les talents
>     - [ ]  Améliorer les retours et évaluations des employés
>     - [ ]  Gérer le changement
>     - [ ]  Optimiser la gestion de la performance
>     - [ ]  Améliorer la prise de décision
>     - [ ]  Développer le mentorat, le coaching
>     - [ ]  Accroître la responsabilité
>     
>     **Objectifs de Ressources :**
>     
>     - [ ]  Maximiser la productivité des employés
>     - [ ]  Augmenter la rétention des employés
>     
>     **Objectifs d’Avantage Concurrentiel :**
>     
>     - [ ]  Articuler la vision, le but, les systèmes
>     - [ ]  Améliorer la confiance, la collaboration interfonctionnelle, le partage d’informations
>     
>     **Diminuer / réduire / minimiser**
>     
>     **Objectifs de Coût :**
>     
>     - [ ]  Réduire le turnover des employés
>     - [ ]  Minimiser le temps de recrutement
>     
>     **Objectifs de Risque :**
>     
>     - [ ]  Réduire l’épuisement des employés
>     - [ ]  Minimiser le désengagement des employés
>     - [ ]  Réduire les silos, les ruptures de communication
> - **OBJECTIFS SUPÉRIEURS DE GESTION DES TECHNOLOGIES**
>     
>     **Augmenter / améliorer / maximiser / croître / accélérer / générer / construire :**
>     
>     **Objectifs de Métriques :**
>     
>     - [ ]  Augmenter le temps de fonctionnement du système
>     - [ ]  Améliorer la disponibilité du système
>     
>     **Objectifs de Systèmes :**
>     
>     - [ ]  Maximiser l’échelle
>     - [ ]  Améliorer la qualité, la stabilité, la sécurité
>     - [ ]  Générer des services critiques pour la mission
>     - [ ]  Optimiser la gestion des défauts
>     - [ ]  Accélérer le développement agile
>     - [ ]  Améliorer la récupération après sinistre, les redondances
>     - [ ]  Développer des services en temps réel
>     
>     **Objectifs de Ressources :**
>     
>     - [ ]  Accélérer la décision d’achat ou de construction
>     - [ ]  Améliorer la gestion des fournisseurs
>     - [ ]  Optimiser l’intégration des partenaires
>     - [ ]  Maximiser la vélocité, l’utilisation des équipes
>     
>     **Objectifs d’Avantage Concurrentiel :**
>     
>     - [ ]  Innover avec des services basés sur l’IA, brevets
>     - [ ]  Développer la plateforme, l’infrastructure, le système d’exploitation
>     
>     **Diminuer / réduire / minimiser :**
>     
>     **Objectifs de Coût :**
>     
>     - [ ]  Réduire le taux de consommation
>     
>     **Objectifs de Risque :**
>     
>     - [ ]  Minimiser les dépendances aux plateformes héritées
>     - [ ]  Réduire les temps d’arrêt du système, les pannes du système
>     - [ ]  Réduire la dette technique, les défauts
> 
> It is extremely important that your question ask if the candidate either : 
> 
> - helped increase a positive KPI from the strategic abjectives above (like sales for example)
> - Helped decrease a negative KPI from the strategic abjectives above(like churn for example)
> 
> Use the right verb in your questions (refer to the objectives above). Do not ask for numbers. Only ask if they participated in a vertuous trend.
> 
> Always keep each question really bound to the specific job role and context of the candidate. No generic question
> 
> Sort questions starting from the one that relates the most impressive KPI for a recruiter in this specific field to the ones that related the last impressive KPI for a recruiter.
>"""
}
