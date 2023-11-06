let inputConfig = input.config();
const article_id = inputConfig.article_id ?? '';
const articles_table = base.getTable("Articles");
let keyword = "";
let country = "";
if(article_id){
    const article = await articles_table.selectRecordAsync(article_id);
    const job_name = article?.getCellValueAsString("fldHYGVGork1UuCps") ?? '';
    const record_id = article_id ?? '';
    const language = article?.getCellValueAsString("fldkv9HmOeZ0xVDaH") ?? '';
    const full_text = article?.getCellValueAsString("fld7vn74uF0ZxQhXe") ?? '';
    country = article?.getCellValueAsString("fld403w14pEpmhwSj") ?? '';
    keyword = article?.getCellValueAsString("fld7DBPK7sQlEqNl9") ?? '';
    const image_urls = article?.getCellValueAsString("fldcyNCK9wQw4PSpV") ?? '';
    console.log(`processing ${article_id}, ${job_name}, ${language}`)
    var myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    var raw = JSON.stringify({
        "job_name": job_name,
        "record_id": record_id,
        "language": language.trim(),
        "image_urls": image_urls
    });

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
    };

    if(!full_text || full_text === ''){
        await fetch("https://starfish-app-2sc3d.ondigitalocean.app/article-texts/", requestOptions)
            .then(response => response.json())
            .then(result => console.log(result))
            .catch(error => console.log('error', error));
    }

}else{
    console.log("No new Articles");
}
output.set('record_id', article_id);
output.set('keyword', keyword);
output.set('country', country);