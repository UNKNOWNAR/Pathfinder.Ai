/**
 * Simple LocalStorage Cache Utility with TTL
 */
const cache = {
    set(key, value, ttlMinutes = 60) {
        const now = new Date();
        const item = {
            value: value,
            expiry: now.getTime() + ttlMinutes * 60 * 1000,
        };
        localStorage.setItem(key, JSON.stringify(item));
    },

    get(key) {
        const itemStr = localStorage.getItem(key);
        if (!itemStr) return null;

        try {
            const item = JSON.parse(itemStr);
            const now = new Date();

            if (now.getTime() > item.expiry) {
                localStorage.removeItem(key);
                return null;
            }
            return item.value;
        } catch (e) {
            console.error(`Cache corruption for key ${key}`, e);
            localStorage.removeItem(key);
            return null;
        }
    },

    remove(key) {
        localStorage.removeItem(key);
    },

    clear() {
        // Only clear business data, keep auth tokens if needed
        // For this project, we'll clear everything on logout anyway
        localStorage.clear();
    }
};

export default cache;
