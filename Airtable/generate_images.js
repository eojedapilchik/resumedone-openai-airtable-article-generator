// Get the job name from the input configuration
const inputConfig = input.config();
const job_name = inputConfig?.job_name + ` profesionale`?? '';
const header_language_code = inputConfig?.header_language_code[0] ?? 'en-US'
console.log(header_language_code[0])
const images_url = []
// Check if the job name is provided
if (job_name && header_language_code) {
    const queries = [
        '&limit=5'
    ]
    for (let i = 0 ; i< queries.length; i++){
        await requestFreePik(queries[i])
    }

} else {
    console.log('Job name is required.');
}

output.set('images_url', images_url.join(','))

function logImage(item) {
    console.log('Title:', item.title);
    console.log('Image URL:', item.image.source.url);
    console.log('----------------------------------');
}

async function requestFreePik(query){

    const myHeaders = new Headers({
        "Accept-Language": "en-US",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Freepik-API-Key": "some-key"  //IMPORTANT: add your API key here
    });


    const requestOptions = {
        method: 'GET',
        headers: myHeaders
    };

    const url = `https://api.freepik.com/v1/resources?locale=${header_language_code}&page=1&order=latest&term=${encodeURIComponent(job_name)}&filters[content_type][photo]=1&filters[orientation][landscape]=1&filters[people][include]=1${query ?? ''}`

    console.log(url)
    await fetch(url, requestOptions)
        .then(response => {
            if (!response.ok) {
                console.error(`HTTP error! Status: ${response.status}`)
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.data && data.data.length > 0) {
                data.data.forEach(item => {
                    logImage(item);
                    if (item?.image?.source?.url){
                        images_url.push(item.image.source.url)
                    }
                });

            } else {
                console.log('No images found.');
            }
        })
        .catch(error => console.log('Error:', error));

}
