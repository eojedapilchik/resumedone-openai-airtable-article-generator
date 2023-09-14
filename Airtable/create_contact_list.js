output.markdown('# Creating Contact List');
let max_contacts = await input.textAsync('Up to how many contacts do you want to fetch per website (max: 6)?');
let max = 1;

try {
    max = parseInt(max_contacts, 10);

    if (isNaN(max) || max < 0 || max > 6) {
        console.error("Invalid input. Using default of 4.");
        max = 1;
    }
} catch (error) {
    console.error("Error parsing input. Using default of 4.");
    max = 1;
}
const MAX_CONTACTS = max;
const TABLE_WEBSITE = base.getTable("tblXPrNZmBP9iailh");
const TABLE_CONTACTS = base.getTable("tblEDB7ZOBCqPDjMi");
const TABLE_LIVE_LINKS = base.getTable("tbl8NAwDIqxcLasZL");

const LIVE_LINK_FIELDS = {
    website: "fld0xBzdTBznGHiix"
};

const WEBSITE_FIELDS = {
    website: "fldxPq6OGXTv3q7Hh",
    contacts: "fldWcQXYyLVwrIMJr",
    processed: "fld2u7Zn3MVExoUCF"

};

const CONTACTS_FIELDS = {
    email: "fld6je9gVo6dVhGUI",
    website: "fldIxYmFniIfkkXdy"

};

let websites_to_fetch = await TABLE_WEBSITE.selectRecordsAsync({fields: [WEBSITE_FIELDS.website]});
let live_websites = await TABLE_LIVE_LINKS.selectRecordsAsync({fields: [LIVE_LINK_FIELDS.website]})
const live_link_records = live_websites.records.map( website => website.getCellValueAsString(LIVE_LINK_FIELDS.website));

const already_live = [];
const no_contact_found = [];
console.log(`Initialization finished, processing websites...`);
if(websites_to_fetch.records.length){
    const website_records = websites_to_fetch.records
    const total_websites = website_records.length
    for(let i=0; i<total_websites; i++){
        const contact_founds = []
        const website_url = website_records[i].getCellValueAsString(WEBSITE_FIELDS.website);
        if(!website_url){
            continue;
        }
        const progress = Math.round(((i+1)/total_websites) * 100)
        if(live_link_records.includes(website_url)){
            console.log(`Skipping ${website_url} already in Live Links Progress: ${progress}`)
            already_live.push(website_url)
            continue;
        }
        const contacts = await checkContactData(website_url);
        if (contacts.length){
            console.log(` A total of ${contacts.length} contacts were found for ${website_url} Progress: ${progress}%`);
            contacts.forEach((contact) => {
                contact_founds.push({
                    fields:{
                        [CONTACTS_FIELDS.email]: contact.value,
                        [CONTACTS_FIELDS.website]: [{id: website_records[i].id}]
                    }
                })
            });

            await TABLE_CONTACTS.createRecordsAsync(contact_founds);
        }else{
            no_contact_found.push(website_url)
            console.log(`No contacts found for ${website_url}  Progress: ${progress}%`)
        }

    }

}

output.markdown("All websites have been processed");

output.markdown("## Already In Live Links (excluded)")
output.table(already_live)

if(no_contact_found.length){
    output.markdown("## No contact found for ")
    output.table(no_contact_found);
}

async function checkContactData(website_url){
    const url = 'https://website-contacts-scraper.p.rapidapi.com/scrape-contacts?query='+encodeURIComponent(website_url);
    const options = {
        method: 'GET',
        headers: {
            'X-RapidAPI-Key': '34255a775cmsh9cdbdb4681d872fp19c751jsna4fd3ec1c3a9',
            'X-RapidAPI-Host': 'website-contacts-scraper.p.rapidapi.com'
        }
    };

    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            console.error(`HTTP error: ${response.status}`);
            return [];
        }

        const result = await response.json();

        const emails = result?.data[0]?.emails ?? [];
        return emails.slice(0, MAX_CONTACTS);
    } catch (error) {
        console.error(error);
        return [];
    }

}