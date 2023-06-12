


const get_cookies = (key) => {
    let cookies_str = document.cookie
    cookies_str = cookies_str.replaceAll(' ', '')
    cookies_str = cookies_str.split(';')
    let new_data = {}
    cookies_str.forEach(cookie => {
        let [dt, value] = cookie.split('=')
        try{
            value = JSON.parse(value)
        }
        catch{
            value = value
        }
        new_data[dt] = value
    })
    if (key) {
        if(new_data[key]){
            return new_data[key]
        }
        else{
            return {}
        }
    }
    else {
        return new_data
    }
}

const set_cookies = (key, value, valid_for) => {
    if (key && value) {
        if (typeof(value) == 'object'){
            value = JSON.stringify(value)
        }
        remove_cookies(key)
        document.cookie = `${key}=${value}; Expires=${valid_for ? valid_for : ''}; Path=/;`
    }
}

const remove_cookies = (key) =>{
    if (key) {
        document.cookie = `${key}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`
    }
}