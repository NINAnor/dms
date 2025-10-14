import axios from 'axios';

export const config = JSON.parse(document.getElementById('initial-data')!.textContent)

export const client = axios.create({
    headers: {
        "X-CSRFToken": config.csrf
    }
})
