import axios from "axios";

const client = axios.create({
  baseURL: process.env.REACT_APP_API
})

export default client;