import axios from "axios";
import config from "../config/config";


const api = axios.create(
    {
        baseURL: config.API_BASE_URL,
        timeout: config.API_TIMEOUT
    }
);

export default api;