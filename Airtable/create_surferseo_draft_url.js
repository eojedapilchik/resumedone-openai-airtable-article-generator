let inputConfig = input.config()
let text = inputConfig.cv_name
let country = inputConfig.country
let table  = base.getTable("tblpWGFIZf88LIFJw");
let record_id = inputConfig.record_id
let draft_url = '';
console.log(`country: ${country}`)
if(text && country){
  const API_KEY = 'eoPlZtUeMsrB2Xli8xx0y3gRVR0-b-uG';
  let response = await fetch('https://app.surferseo.com/api/v1/content_editors', {
    method: 'POST',
    headers: {
      'API-KEY': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      keywords: [text],
      location: country
    })
  });

  console.log(response)
  let data = await response.json()
  console.log('data ', data)
  if(data?.permalink_hash){
        draft_url = `https://app.surferseo.com/drafts/s/${data.permalink_hash}`
        await table.updateRecordAsync(record_id, {"Content URL (Surfer)": draft_url});
        console.log( draft_url)
  }else{
        console.log('no url provided')
  }

}else{
  console.log(`Link was not created, missing some value id ${record_id} text ${text} country ${country}`)
}

output.set('draft_url', draft_url);