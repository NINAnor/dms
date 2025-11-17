import axios from 'axios';
import { Config } from './types';

export const config: Config = JSON.parse(document.getElementById('initial-data')!.textContent);

console.debug(config);

export const client = axios.create({
  headers: {
    'X-CSRFToken': config.csrf,
  },
});
