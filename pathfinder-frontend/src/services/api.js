import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:5000'
});

api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config; // Always return config, even without a token (for login/signup)
});
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear expired credentials and gracefully boot out the user
      localStorage.clear();
      window.location.href = '#/login';
    }
    return Promise.reject(error);
  }
);

export default api;