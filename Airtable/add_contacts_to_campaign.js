output.markdown('# Add contacts to Lemlist Campaign');
output.text(` Fetching Campaigns from Lemlist...`);
const CONTACT_FIELDS = {
    email: "fld6je9gVo6dVhGUI",
    website: "fldIxYmFniIfkkXdy",
    campaignName: "fld66SDLvy5qJcjTr",
    addedToCampaign: "fldoLj2GP27lq9PSq"
}
const BASE_URL = 'https://starfish-app-2sc3d.ondigitalocean.app/lemlist/campaigns';

const campaigns_data = await fetchCampaigns();
const campaign_names = campaigns_data.reduce((acum, value)=>{
    acum.push(value.name)
    return acum;
}, [])
console.log(campaign_names)
let campaign_name = await input.textAsync('What is the name of the Lemlist Campaign to add the contacts to?');
const campaign = findCampaignByName(campaigns_data, campaign_name);
if (!campaign){
    output.text(`A campaign was not found with name: ${campaign_name} \n Make sure the name is correct`)
}else{
    let shouldContinue = await input.buttonsAsync(
        `Confirm you want to add all contacts from table: Contacts Lemlist Campaigns to lemlist campaign ${campaign_name}?`,
        [
            {label: 'Cancel', value: 'cancel'},
            {label: 'Go for it', value: 'yes', variant: 'danger'},
        ],
    );
    if (shouldContinue === 'yes') {
        await addContactsToCampaign(campaign)
    }else{
        output.text("Cancelled")
    }
}


async function fetchCampaigns() {
    try {
        const response = await fetch(BASE_URL+"/");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        if (data.status && data.status === 'success') {
            let campaigns = data.campaigns
            return campaigns;
        } else {
            console.error("API returned an error:", data.message || "Unknown error");
            return [];
        }
    } catch (error) {
        console.error("Fetch error:", error.message);
        return [];
    }
}


function findCampaignByName(campaigns, nameValue) {
    return campaigns.find(campaign => campaign.name === nameValue);
}

async function addContactsToCampaign(campaign){
    const table = base.getTable("tblEDB7ZOBCqPDjMi");
    const valid_contacts_view = table.getView("viwN2x7TxrxE8Uy6E")
    const contacts_query = await valid_contacts_view.selectRecordsAsync({fields: table.fields})
    const total_contacts = contacts_query.records.length;
    if(total_contacts > 0){
        output.text(`A total of ${total_contacts} will be added to the Campaign`);
        for (let i = 0; i < total_contacts; i++){
            let email = contacts_query.records[i].getCellValueAsString(CONTACT_FIELDS.email);
            let companyDomain = contacts_query.records[i].getCellValueAsString(CONTACT_FIELDS.website);
            const response = await postContactToCampaign(campaign._id, { email, companyDomain });
            if(response.status === "success"){
                await updateContactAddedToCampaign(contacts_query.records[i].id, campaign.name);
            }else{
                console.error(`${response.response}`)
            }
            console.log(`Progress ${((i+1)*100/total_contacts).toFixed(2)}%`)
        }
    }

}

async function postContactToCampaign(campaignId, contactData) {
    try {
        const response = await fetch(`${BASE_URL}/${campaignId}/contacts/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(contactData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        return data

    } catch (error) {
        console.error('There was a problem with the fetch operation:', error.message);
        return {};
    }
}

async function updateContactAddedToCampaign(record_id, campaign_name){
    const table = base.getTable("tblEDB7ZOBCqPDjMi");
    await table.updateRecordAsync(record_id, {
        [CONTACT_FIELDS.campaignName]: campaign_name,
        [CONTACT_FIELDS.addedToCampaign]: true
    })
}